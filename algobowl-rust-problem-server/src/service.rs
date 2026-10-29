//! Connect RPC service for problem support workers.

use std::sync::Arc;

use bytes::Bytes;
use connectrpc::{ConnectError, ConnectRpcService, RequestContext, ServiceRequest, ServiceResult};
use http_body_util::{BodyExt, Full};
use rand::SeedableRng;
use rand::rngs::StdRng;
use tower::ServiceExt;
use worker::{Headers, Request, Response};

use crate::problemlib::{FileFormatError, VerificationError, decode_text};
use crate::proto::algobowl::problemsupport::v1 as pb;
use pb::__buffa::oneof::{verified_output, verify_input_response, verify_output_response};

/// A problem input file.
pub trait Input: Sized {
    /// Parses an input file.
    ///
    /// # Errors
    ///
    /// Returns an error if the file is malformed.
    fn read(lines: Vec<&str>) -> Result<Self, FileFormatError>;

    /// Writes the normalized input file.
    fn write(&self, out: &mut String);
}

/// A problem output file for an input of type `I`.
pub trait Output<I>: Sized {
    /// Parses an output file for an input.
    ///
    /// # Errors
    ///
    /// Returns an error if the file is malformed.
    fn read(input: &I, lines: Vec<&str>) -> Result<Self, FileFormatError>;

    /// Writes the normalized output file.
    fn write(&self, out: &mut String);

    /// Returns the score reported in the output file.
    fn score(&self) -> i64;

    /// Verifies the output for its input.
    ///
    /// Returns the actual score of the output, or `None` if the problem only
    /// checks validity.  An output whose actual score differs from its
    /// reported score is rejected.
    ///
    /// # Errors
    ///
    /// Returns an error if the output is not a valid solution.
    fn verify(&self, input: &I) -> Result<Option<i64>, VerificationError>;
}

/// A problem statement served alongside the problem.
pub struct Statement {
    format: pb::StatementFormat,
    url: &'static str,
}

impl Statement {
    /// A PDF statement.  A root-relative URL is resolved against each
    /// request's origin.
    pub const fn pdf(url: &'static str) -> Self {
        Statement {
            format: pb::StatementFormat::Pdf,
            url,
        }
    }

    /// A Markdown statement.  A root-relative URL is resolved against each
    /// request's origin.
    pub const fn markdown(url: &'static str) -> Self {
        Statement {
            format: pb::StatementFormat::Markdown,
            url,
        }
    }
}

/// Describes a problem and serves its problem support RPCs.
pub struct Problem<I, O> {
    /// Whether lower or higher scores are better.
    pub rank_sort: pb::RankSort,
    /// Number of decimal places to display scores with.
    pub score_decimal_places: i32,
    /// Problem statements.
    pub statements: &'static [Statement],
    /// Generates a random input, if supported.
    pub generate: Option<fn(&mut StdRng) -> I>,
    /// Produces a trivial solution for an input, if supported.
    pub trivial_solve: Option<fn(&I) -> O>,
}

/// The origin of a request, used to resolve root-relative statement URLs.
#[derive(Clone)]
struct RequestOrigin(String);

impl<I: Input + 'static, O: Output<I> + 'static> Problem<I, O> {
    /// Serves a request from the Workers runtime.
    ///
    /// # Errors
    ///
    /// Returns an error if the request or response cannot be converted
    /// between the Workers runtime and the RPC service.
    pub async fn serve(&'static self, mut req: Request) -> worker::Result<Response> {
        let url = req.url()?;
        let mut builder = http::Request::builder()
            .method(req.method().to_string().as_str())
            .uri(url.as_str())
            .extension(RequestOrigin(url.origin().ascii_serialization()));
        for (name, value) in req.headers().entries() {
            // Client deadlines are enforced with a Tokio timer, which is not
            // available in Workers.  Workers enforce their own time limits.
            if name.eq_ignore_ascii_case("connect-timeout-ms") {
                continue;
            }
            builder = builder.header(name, value);
        }
        let request = builder
            .body(Full::new(Bytes::from(req.bytes().await?)))
            .map_err(|e| worker::Error::RustError(e.to_string()))?;

        let service = ConnectRpcService::new(pb::ProblemSupportServiceServer::from_arc(Arc::new(
            ProblemService(self),
        )));
        let Ok(response) = service.oneshot(request).await;
        let (parts, body) = response.into_parts();
        let body = body
            .collect()
            .await
            .map_err(|e| worker::Error::RustError(e.to_string()))?
            .to_bytes();

        let headers = Headers::new();
        for (name, value) in &parts.headers {
            if let Ok(value) = value.to_str() {
                headers.append(name.as_str(), value)?;
            }
        }
        Ok(Response::from_bytes(body.to_vec())?
            .with_status(parts.status.as_u16())
            .with_headers(headers))
    }

    fn get_problem_info(&self, origin: &str) -> pb::GetProblemInfoResponse {
        let statements = self
            .statements
            .iter()
            .map(|statement| pb::StatementInfo {
                format: statement.format.into(),
                url: if statement.url.starts_with('/') {
                    format!("{origin}{}", statement.url)
                } else {
                    statement.url.to_owned()
                },
                ..Default::default()
            })
            .collect();
        let supported_solvers = self
            .trivial_solve
            .map(|_| pb::SolverInfo {
                solver_type: pb::SolverType::Trivial.into(),
                ..Default::default()
            })
            .into_iter()
            .collect();
        pb::GetProblemInfoResponse {
            rank_sort: self.rank_sort.into(),
            score_decimal_places: self.score_decimal_places,
            statements,
            supported_solvers,
            supports_generate_input: self.generate.is_some(),
            ..Default::default()
        }
    }

    fn verify_input(&self, content: &[u8]) -> pb::VerifyInputResponse {
        let result = match read_input::<I>(content) {
            Ok(input) => verify_input_response::Result::NormalizedContent(write_input(&input)),
            Err(FileFormatError(message)) => verify_input_response::Result::FormatError(message),
        };
        pb::VerifyInputResponse {
            result: Some(result),
            ..Default::default()
        }
    }

    fn verify_output(
        &self,
        input_content: &[u8],
        output_content: &[u8],
    ) -> pb::VerifyOutputResponse {
        let parsed = read_input::<I>(input_content).and_then(|input| {
            let text = decode_text(output_content)?;
            let output = O::read(&input, text.lines().collect())?;
            Ok((input, output))
        });
        let (input, output) = match parsed {
            Ok(parsed) => parsed,
            Err(FileFormatError(message)) => {
                return pb::VerifyOutputResponse {
                    result: Some(verify_output_response::Result::FormatError(message)),
                    ..Default::default()
                };
            }
        };

        let reported_score = output.score();
        let accepted = || verified_output::Verification::Accepted(Box::default());
        let rejected = |rejection_reason| {
            verified_output::Verification::Rejected(Box::new(pb::RejectedOutput {
                rejection_reason,
                ..Default::default()
            }))
        };
        let (actual_score, verification) = match output.verify(&input) {
            Ok(Some(actual)) if actual == reported_score => (Some(actual), accepted()),
            Ok(Some(actual)) => (
                Some(actual),
                rejected(format!(
                    "Reported score ({reported_score}) does not match actual ({actual})"
                )),
            ),
            Ok(None) => (None, accepted()),
            Err(VerificationError(reason)) => (None, rejected(reason)),
        };
        let mut normalized_content = String::new();
        output.write(&mut normalized_content);
        pb::VerifyOutputResponse {
            result: Some(verify_output_response::Result::Output(Box::new(
                pb::VerifiedOutput {
                    normalized_content: normalized_content.into_bytes(),
                    reported_score,
                    actual_score,
                    verification: Some(verification),
                    ..Default::default()
                },
            ))),
            ..Default::default()
        }
    }

    fn generate_input(&self, seed: Option<i64>) -> Result<pb::GenerateInputResponse, ConnectError> {
        let generate = self
            .generate
            .ok_or_else(|| ConnectError::unimplemented("generate_input is not implemented"))?;
        let seed = seed.map_or_else(random_seed, |seed| seed as u64);
        let input = generate(&mut StdRng::seed_from_u64(seed));
        Ok(pb::GenerateInputResponse {
            content: write_input(&input),
            ..Default::default()
        })
    }

    fn solve(
        &self,
        input_content: &[u8],
        solver_type: Option<pb::SolverType>,
    ) -> Result<pb::SolveResponse, ConnectError> {
        let input = read_input::<I>(input_content)
            .map_err(|FileFormatError(message)| ConnectError::invalid_argument(message))?;
        let solver = match solver_type {
            Some(pb::SolverType::Trivial) => self.trivial_solve,
            _ => None,
        }
        .ok_or_else(|| ConnectError::unimplemented("solver is not implemented"))?;
        let mut output_content = String::new();
        solver(&input).write(&mut output_content);
        Ok(pb::SolveResponse {
            output_content: output_content.into_bytes(),
            ..Default::default()
        })
    }
}

/// Implements the generated service trait for a problem.
struct ProblemService<I: 'static, O: 'static>(&'static Problem<I, O>);

// Returning concrete response types from `async fn` is the documented way to
// implement connectrpc service traits.
#[allow(refining_impl_trait)]
impl<I: Input + 'static, O: Output<I> + 'static> pb::ProblemSupportService
    for ProblemService<I, O>
{
    async fn get_problem_info(
        &self,
        ctx: RequestContext,
        _request: ServiceRequest<'_, pb::GetProblemInfoRequest>,
    ) -> ServiceResult<pb::GetProblemInfoResponse> {
        let origin = ctx
            .extensions()
            .get::<RequestOrigin>()
            .map_or("", |origin| origin.0.as_str());
        Ok(self.0.get_problem_info(origin).into())
    }

    async fn verify_input(
        &self,
        _ctx: RequestContext,
        request: ServiceRequest<'_, pb::VerifyInputRequest>,
    ) -> ServiceResult<pb::VerifyInputResponse> {
        Ok(self.0.verify_input(request.content).into())
    }

    async fn verify_output(
        &self,
        _ctx: RequestContext,
        request: ServiceRequest<'_, pb::VerifyOutputRequest>,
    ) -> ServiceResult<pb::VerifyOutputResponse> {
        Ok(self
            .0
            .verify_output(request.input_content, request.output_content)
            .into())
    }

    async fn generate_input(
        &self,
        _ctx: RequestContext,
        request: ServiceRequest<'_, pb::GenerateInputRequest>,
    ) -> ServiceResult<pb::GenerateInputResponse> {
        Ok(self.0.generate_input(request.seed)?.into())
    }

    async fn solve(
        &self,
        _ctx: RequestContext,
        request: ServiceRequest<'_, pb::SolveRequest>,
    ) -> ServiceResult<pb::SolveResponse> {
        Ok(self
            .0
            .solve(request.input_content, request.solver_type.as_known())?
            .into())
    }
}

/// Returns a random seed, for requests that do not provide one.
fn random_seed() -> u64 {
    (worker::js_sys::Math::random() * (1u64 << 53) as f64) as u64
}

fn read_input<I: Input>(content: &[u8]) -> Result<I, FileFormatError> {
    let text = decode_text(content)?;
    I::read(text.lines().collect())
}

fn write_input<I: Input>(input: &I) -> Vec<u8> {
    let mut content = String::new();
    input.write(&mut content);
    content.into_bytes()
}
