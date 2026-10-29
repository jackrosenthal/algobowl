///Shorthand for `OwnedView<GetProblemInfoRequestView<'static>>`.
pub type OwnedGetProblemInfoRequestView = ::buffa::view::OwnedView<
    crate::proto::algobowl::problemsupport::v1::__buffa::view::GetProblemInfoRequestView<
        'static,
    >,
>;
///Shorthand for `OwnedView<GetProblemInfoResponseView<'static>>`.
pub type OwnedGetProblemInfoResponseView = ::buffa::view::OwnedView<
    crate::proto::algobowl::problemsupport::v1::__buffa::view::GetProblemInfoResponseView<
        'static,
    >,
>;
///Shorthand for `OwnedView<VerifyInputRequestView<'static>>`.
pub type OwnedVerifyInputRequestView = ::buffa::view::OwnedView<
    crate::proto::algobowl::problemsupport::v1::__buffa::view::VerifyInputRequestView<
        'static,
    >,
>;
///Shorthand for `OwnedView<VerifyInputResponseView<'static>>`.
pub type OwnedVerifyInputResponseView = ::buffa::view::OwnedView<
    crate::proto::algobowl::problemsupport::v1::__buffa::view::VerifyInputResponseView<
        'static,
    >,
>;
///Shorthand for `OwnedView<VerifyOutputRequestView<'static>>`.
pub type OwnedVerifyOutputRequestView = ::buffa::view::OwnedView<
    crate::proto::algobowl::problemsupport::v1::__buffa::view::VerifyOutputRequestView<
        'static,
    >,
>;
///Shorthand for `OwnedView<VerifyOutputResponseView<'static>>`.
pub type OwnedVerifyOutputResponseView = ::buffa::view::OwnedView<
    crate::proto::algobowl::problemsupport::v1::__buffa::view::VerifyOutputResponseView<
        'static,
    >,
>;
///Shorthand for `OwnedView<GenerateInputRequestView<'static>>`.
pub type OwnedGenerateInputRequestView = ::buffa::view::OwnedView<
    crate::proto::algobowl::problemsupport::v1::__buffa::view::GenerateInputRequestView<
        'static,
    >,
>;
///Shorthand for `OwnedView<GenerateInputResponseView<'static>>`.
pub type OwnedGenerateInputResponseView = ::buffa::view::OwnedView<
    crate::proto::algobowl::problemsupport::v1::__buffa::view::GenerateInputResponseView<
        'static,
    >,
>;
///Shorthand for `OwnedView<SolveRequestView<'static>>`.
pub type OwnedSolveRequestView = ::buffa::view::OwnedView<
    crate::proto::algobowl::problemsupport::v1::__buffa::view::SolveRequestView<'static>,
>;
///Shorthand for `OwnedView<SolveResponseView<'static>>`.
pub type OwnedSolveResponseView = ::buffa::view::OwnedView<
    crate::proto::algobowl::problemsupport::v1::__buffa::view::SolveResponseView<'static>,
>;
impl ::connectrpc::Encodable<
    crate::proto::algobowl::problemsupport::v1::GetProblemInfoResponse,
>
for crate::proto::algobowl::problemsupport::v1::__buffa::view::GetProblemInfoResponseView<
    '_,
> {
    fn encode(
        &self,
        codec: ::connectrpc::CodecFormat,
    ) -> ::std::result::Result<::buffa::bytes::Bytes, ::connectrpc::ConnectError> {
        ::connectrpc::__codegen::encode_view_body(self, codec)
    }
}
impl ::connectrpc::Encodable<
    crate::proto::algobowl::problemsupport::v1::GetProblemInfoResponse,
>
for ::buffa::view::OwnedView<
    crate::proto::algobowl::problemsupport::v1::__buffa::view::GetProblemInfoResponseView<
        'static,
    >,
> {
    fn encode(
        &self,
        codec: ::connectrpc::CodecFormat,
    ) -> ::std::result::Result<::buffa::bytes::Bytes, ::connectrpc::ConnectError> {
        ::connectrpc::__codegen::encode_view_body(self.reborrow(), codec)
    }
    /// An `OwnedView` still holds the buffer it was decoded from, so
    /// its large fields can be handed to the response body by
    /// reference count instead of copied. The bare view impl above
    /// cannot do this: it has borrows but no buffer to name.
    fn encode_segments(
        &self,
        codec: ::connectrpc::CodecFormat,
    ) -> ::std::result::Result<::connectrpc::EncodedBody, ::connectrpc::ConnectError> {
        ::connectrpc::__codegen::encode_view_body_segments(
            self.reborrow(),
            self.bytes(),
            codec,
        )
    }
}
impl ::connectrpc::Encodable<
    crate::proto::algobowl::problemsupport::v1::VerifyInputResponse,
>
for crate::proto::algobowl::problemsupport::v1::__buffa::view::VerifyInputResponseView<
    '_,
> {
    fn encode(
        &self,
        codec: ::connectrpc::CodecFormat,
    ) -> ::std::result::Result<::buffa::bytes::Bytes, ::connectrpc::ConnectError> {
        ::connectrpc::__codegen::encode_view_body(self, codec)
    }
}
impl ::connectrpc::Encodable<
    crate::proto::algobowl::problemsupport::v1::VerifyInputResponse,
>
for ::buffa::view::OwnedView<
    crate::proto::algobowl::problemsupport::v1::__buffa::view::VerifyInputResponseView<
        'static,
    >,
> {
    fn encode(
        &self,
        codec: ::connectrpc::CodecFormat,
    ) -> ::std::result::Result<::buffa::bytes::Bytes, ::connectrpc::ConnectError> {
        ::connectrpc::__codegen::encode_view_body(self.reborrow(), codec)
    }
    /// An `OwnedView` still holds the buffer it was decoded from, so
    /// its large fields can be handed to the response body by
    /// reference count instead of copied. The bare view impl above
    /// cannot do this: it has borrows but no buffer to name.
    fn encode_segments(
        &self,
        codec: ::connectrpc::CodecFormat,
    ) -> ::std::result::Result<::connectrpc::EncodedBody, ::connectrpc::ConnectError> {
        ::connectrpc::__codegen::encode_view_body_segments(
            self.reborrow(),
            self.bytes(),
            codec,
        )
    }
}
impl ::connectrpc::Encodable<
    crate::proto::algobowl::problemsupport::v1::VerifyOutputResponse,
>
for crate::proto::algobowl::problemsupport::v1::__buffa::view::VerifyOutputResponseView<
    '_,
> {
    fn encode(
        &self,
        codec: ::connectrpc::CodecFormat,
    ) -> ::std::result::Result<::buffa::bytes::Bytes, ::connectrpc::ConnectError> {
        ::connectrpc::__codegen::encode_view_body(self, codec)
    }
}
impl ::connectrpc::Encodable<
    crate::proto::algobowl::problemsupport::v1::VerifyOutputResponse,
>
for ::buffa::view::OwnedView<
    crate::proto::algobowl::problemsupport::v1::__buffa::view::VerifyOutputResponseView<
        'static,
    >,
> {
    fn encode(
        &self,
        codec: ::connectrpc::CodecFormat,
    ) -> ::std::result::Result<::buffa::bytes::Bytes, ::connectrpc::ConnectError> {
        ::connectrpc::__codegen::encode_view_body(self.reborrow(), codec)
    }
    /// An `OwnedView` still holds the buffer it was decoded from, so
    /// its large fields can be handed to the response body by
    /// reference count instead of copied. The bare view impl above
    /// cannot do this: it has borrows but no buffer to name.
    fn encode_segments(
        &self,
        codec: ::connectrpc::CodecFormat,
    ) -> ::std::result::Result<::connectrpc::EncodedBody, ::connectrpc::ConnectError> {
        ::connectrpc::__codegen::encode_view_body_segments(
            self.reborrow(),
            self.bytes(),
            codec,
        )
    }
}
impl ::connectrpc::Encodable<
    crate::proto::algobowl::problemsupport::v1::GenerateInputResponse,
>
for crate::proto::algobowl::problemsupport::v1::__buffa::view::GenerateInputResponseView<
    '_,
> {
    fn encode(
        &self,
        codec: ::connectrpc::CodecFormat,
    ) -> ::std::result::Result<::buffa::bytes::Bytes, ::connectrpc::ConnectError> {
        ::connectrpc::__codegen::encode_view_body(self, codec)
    }
}
impl ::connectrpc::Encodable<
    crate::proto::algobowl::problemsupport::v1::GenerateInputResponse,
>
for ::buffa::view::OwnedView<
    crate::proto::algobowl::problemsupport::v1::__buffa::view::GenerateInputResponseView<
        'static,
    >,
> {
    fn encode(
        &self,
        codec: ::connectrpc::CodecFormat,
    ) -> ::std::result::Result<::buffa::bytes::Bytes, ::connectrpc::ConnectError> {
        ::connectrpc::__codegen::encode_view_body(self.reborrow(), codec)
    }
    /// An `OwnedView` still holds the buffer it was decoded from, so
    /// its large fields can be handed to the response body by
    /// reference count instead of copied. The bare view impl above
    /// cannot do this: it has borrows but no buffer to name.
    fn encode_segments(
        &self,
        codec: ::connectrpc::CodecFormat,
    ) -> ::std::result::Result<::connectrpc::EncodedBody, ::connectrpc::ConnectError> {
        ::connectrpc::__codegen::encode_view_body_segments(
            self.reborrow(),
            self.bytes(),
            codec,
        )
    }
}
impl ::connectrpc::Encodable<crate::proto::algobowl::problemsupport::v1::SolveResponse>
for crate::proto::algobowl::problemsupport::v1::__buffa::view::SolveResponseView<'_> {
    fn encode(
        &self,
        codec: ::connectrpc::CodecFormat,
    ) -> ::std::result::Result<::buffa::bytes::Bytes, ::connectrpc::ConnectError> {
        ::connectrpc::__codegen::encode_view_body(self, codec)
    }
}
impl ::connectrpc::Encodable<crate::proto::algobowl::problemsupport::v1::SolveResponse>
for ::buffa::view::OwnedView<
    crate::proto::algobowl::problemsupport::v1::__buffa::view::SolveResponseView<'static>,
> {
    fn encode(
        &self,
        codec: ::connectrpc::CodecFormat,
    ) -> ::std::result::Result<::buffa::bytes::Bytes, ::connectrpc::ConnectError> {
        ::connectrpc::__codegen::encode_view_body(self.reborrow(), codec)
    }
    /// An `OwnedView` still holds the buffer it was decoded from, so
    /// its large fields can be handed to the response body by
    /// reference count instead of copied. The bare view impl above
    /// cannot do this: it has borrows but no buffer to name.
    fn encode_segments(
        &self,
        codec: ::connectrpc::CodecFormat,
    ) -> ::std::result::Result<::connectrpc::EncodedBody, ::connectrpc::ConnectError> {
        ::connectrpc::__codegen::encode_view_body_segments(
            self.reborrow(),
            self.bytes(),
            codec,
        )
    }
}
/// Full service name for this service.
pub const PROBLEM_SUPPORT_SERVICE_SERVICE_NAME: &str = "algobowl.problemsupport.v1.ProblemSupportService";
/// Static [`Spec`](::connectrpc::Spec) for the `GetProblemInfo` RPC, as seen by the server; the generated client passes it with [`origin`](::connectrpc::Spec::origin) `Client` (compare across sides with [`Spec::same_method`](::connectrpc::Spec::same_method)).
pub const PROBLEM_SUPPORT_SERVICE_GET_PROBLEM_INFO_SPEC: ::connectrpc::Spec = ::connectrpc::Spec::server(
        "/algobowl.problemsupport.v1.ProblemSupportService/GetProblemInfo",
        ::connectrpc::StreamType::Unary,
    )
    .with_idempotency_level(::connectrpc::IdempotencyLevel::Unknown);
/// Static [`Spec`](::connectrpc::Spec) for the `VerifyInput` RPC, as seen by the server; the generated client passes it with [`origin`](::connectrpc::Spec::origin) `Client` (compare across sides with [`Spec::same_method`](::connectrpc::Spec::same_method)).
pub const PROBLEM_SUPPORT_SERVICE_VERIFY_INPUT_SPEC: ::connectrpc::Spec = ::connectrpc::Spec::server(
        "/algobowl.problemsupport.v1.ProblemSupportService/VerifyInput",
        ::connectrpc::StreamType::Unary,
    )
    .with_idempotency_level(::connectrpc::IdempotencyLevel::Unknown);
/// Static [`Spec`](::connectrpc::Spec) for the `VerifyOutput` RPC, as seen by the server; the generated client passes it with [`origin`](::connectrpc::Spec::origin) `Client` (compare across sides with [`Spec::same_method`](::connectrpc::Spec::same_method)).
pub const PROBLEM_SUPPORT_SERVICE_VERIFY_OUTPUT_SPEC: ::connectrpc::Spec = ::connectrpc::Spec::server(
        "/algobowl.problemsupport.v1.ProblemSupportService/VerifyOutput",
        ::connectrpc::StreamType::Unary,
    )
    .with_idempotency_level(::connectrpc::IdempotencyLevel::Unknown);
/// Static [`Spec`](::connectrpc::Spec) for the `GenerateInput` RPC, as seen by the server; the generated client passes it with [`origin`](::connectrpc::Spec::origin) `Client` (compare across sides with [`Spec::same_method`](::connectrpc::Spec::same_method)).
pub const PROBLEM_SUPPORT_SERVICE_GENERATE_INPUT_SPEC: ::connectrpc::Spec = ::connectrpc::Spec::server(
        "/algobowl.problemsupport.v1.ProblemSupportService/GenerateInput",
        ::connectrpc::StreamType::Unary,
    )
    .with_idempotency_level(::connectrpc::IdempotencyLevel::Unknown);
/// Static [`Spec`](::connectrpc::Spec) for the `Solve` RPC, as seen by the server; the generated client passes it with [`origin`](::connectrpc::Spec::origin) `Client` (compare across sides with [`Spec::same_method`](::connectrpc::Spec::same_method)).
pub const PROBLEM_SUPPORT_SERVICE_SOLVE_SPEC: ::connectrpc::Spec = ::connectrpc::Spec::server(
        "/algobowl.problemsupport.v1.ProblemSupportService/Solve",
        ::connectrpc::StreamType::Unary,
    )
    .with_idempotency_level(::connectrpc::IdempotencyLevel::Unknown);
/// Server trait for ProblemSupportService.
///
/// # Implementing handlers
///
/// Implement methods with plain `async fn`; the returned future satisfies
/// the `Send` bound automatically.
///
/// **Unary and server-streaming requests** arrive as
/// [`ServiceRequest<'_, Req>`](::connectrpc::ServiceRequest): a zero-copy
/// view of the request plus its body, valid for the duration of the call.
/// Fields are read directly (`request.name` is a `&str` into the decoded
/// buffer) and the borrow may be held across `.await` points. Anything
/// that must outlive the call — `tokio::spawn`, channels, server state,
/// or data captured by a returned response stream — takes owned data:
/// call `request.to_owned_message()` (or copy the specific fields)
/// first.
///
/// **Client-streaming and bidi requests** arrive as
/// [`InboundStream<Req>`](::connectrpc::InboundStream) — a
/// `ServiceStream` of [`StreamMessage`](::connectrpc::StreamMessage)s.
/// Each item owns its decoded buffer and is `Send + 'static`, so items
/// can be buffered or moved into spawned tasks; read fields zero-copy
/// through the generated accessor methods (`item.name()`) or `.view()`,
/// convert with `.to_owned_message()`, or yield an item back unchanged —
/// `StreamMessage<M>` implements `Encodable<M>`.
///
/// Request types resolved through `extern_path` (e.g. well-known types
/// from another crate) use the same wrappers; the crate that owns the
/// type must be generated with buffa ≥ 0.9.0 and views enabled so the
/// backing `HasMessageView` impl exists.
///
/// The `impl Encodable<Out>` return bound accepts the owned `Out`, the
/// generated `OutView<'_>` / `OwnedOutView`,
/// [`MaybeBorrowed`](::connectrpc::MaybeBorrowed), or
/// [`PreEncoded`](::connectrpc::PreEncoded) for handlers that encode a
/// non-`'static` view internally and pass the bytes across the handler
/// boundary. View bodies are not emitted for output types mapped via
/// `extern_path` (the impl would be an orphan); return owned for
/// WKT/extern outputs.
///
/// Server-streaming and bidi-streaming methods return
/// `ServiceStream<impl Encodable<Out> + Send + use<Self>>`. The
/// `use<Self>` precise-capturing clause excludes `&self`'s lifetime and
/// the request's lifetime (unary methods use `use<'a, Self>` and may
/// borrow from `&self`), so stream items must be `'static` and cannot
/// borrow from the request. To stream view-encoded data, encode each
/// item inside the stream body and yield
/// [`PreEncoded`](::connectrpc::PreEncoded) — see its `# Streaming
/// example` doc.
#[allow(clippy::type_complexity)]
pub trait ProblemSupportService: Send + Sync + 'static {
    /// Handle the GetProblemInfo RPC.
    ///
    /// `'a` lets the response body borrow from `&self` (e.g. server-resident state).
    ///
    /// `request` is borrowed from the request body and is valid for the
    /// duration of the call; message fields are read directly on it
    /// (zero-copy). The response cannot borrow from `request` — use
    /// `.to_owned_message()` (or copy the specific fields) for anything
    /// returned, stored, or moved into `tokio::spawn`.
    fn get_problem_info<'a>(
        &'a self,
        ctx: ::connectrpc::RequestContext,
        request: ::connectrpc::ServiceRequest<
            '_,
            crate::proto::algobowl::problemsupport::v1::GetProblemInfoRequest,
        >,
    ) -> impl ::std::future::Future<
        Output = ::connectrpc::ServiceResult<
            impl ::connectrpc::Encodable<
                crate::proto::algobowl::problemsupport::v1::GetProblemInfoResponse,
            > + Send + use<'a, Self>,
        >,
    > + Send;
    /// Handle the VerifyInput RPC.
    ///
    /// `'a` lets the response body borrow from `&self` (e.g. server-resident state).
    ///
    /// `request` is borrowed from the request body and is valid for the
    /// duration of the call; message fields are read directly on it
    /// (zero-copy). The response cannot borrow from `request` — use
    /// `.to_owned_message()` (or copy the specific fields) for anything
    /// returned, stored, or moved into `tokio::spawn`.
    fn verify_input<'a>(
        &'a self,
        ctx: ::connectrpc::RequestContext,
        request: ::connectrpc::ServiceRequest<
            '_,
            crate::proto::algobowl::problemsupport::v1::VerifyInputRequest,
        >,
    ) -> impl ::std::future::Future<
        Output = ::connectrpc::ServiceResult<
            impl ::connectrpc::Encodable<
                crate::proto::algobowl::problemsupport::v1::VerifyInputResponse,
            > + Send + use<'a, Self>,
        >,
    > + Send;
    /// Handle the VerifyOutput RPC.
    ///
    /// `'a` lets the response body borrow from `&self` (e.g. server-resident state).
    ///
    /// `request` is borrowed from the request body and is valid for the
    /// duration of the call; message fields are read directly on it
    /// (zero-copy). The response cannot borrow from `request` — use
    /// `.to_owned_message()` (or copy the specific fields) for anything
    /// returned, stored, or moved into `tokio::spawn`.
    fn verify_output<'a>(
        &'a self,
        ctx: ::connectrpc::RequestContext,
        request: ::connectrpc::ServiceRequest<
            '_,
            crate::proto::algobowl::problemsupport::v1::VerifyOutputRequest,
        >,
    ) -> impl ::std::future::Future<
        Output = ::connectrpc::ServiceResult<
            impl ::connectrpc::Encodable<
                crate::proto::algobowl::problemsupport::v1::VerifyOutputResponse,
            > + Send + use<'a, Self>,
        >,
    > + Send;
    /// Handle the GenerateInput RPC.
    ///
    /// `'a` lets the response body borrow from `&self` (e.g. server-resident state).
    ///
    /// `request` is borrowed from the request body and is valid for the
    /// duration of the call; message fields are read directly on it
    /// (zero-copy). The response cannot borrow from `request` — use
    /// `.to_owned_message()` (or copy the specific fields) for anything
    /// returned, stored, or moved into `tokio::spawn`.
    fn generate_input<'a>(
        &'a self,
        ctx: ::connectrpc::RequestContext,
        request: ::connectrpc::ServiceRequest<
            '_,
            crate::proto::algobowl::problemsupport::v1::GenerateInputRequest,
        >,
    ) -> impl ::std::future::Future<
        Output = ::connectrpc::ServiceResult<
            impl ::connectrpc::Encodable<
                crate::proto::algobowl::problemsupport::v1::GenerateInputResponse,
            > + Send + use<'a, Self>,
        >,
    > + Send;
    /// Handle the Solve RPC.
    ///
    /// `'a` lets the response body borrow from `&self` (e.g. server-resident state).
    ///
    /// `request` is borrowed from the request body and is valid for the
    /// duration of the call; message fields are read directly on it
    /// (zero-copy). The response cannot borrow from `request` — use
    /// `.to_owned_message()` (or copy the specific fields) for anything
    /// returned, stored, or moved into `tokio::spawn`.
    fn solve<'a>(
        &'a self,
        ctx: ::connectrpc::RequestContext,
        request: ::connectrpc::ServiceRequest<
            '_,
            crate::proto::algobowl::problemsupport::v1::SolveRequest,
        >,
    ) -> impl ::std::future::Future<
        Output = ::connectrpc::ServiceResult<
            impl ::connectrpc::Encodable<
                crate::proto::algobowl::problemsupport::v1::SolveResponse,
            > + Send + use<'a, Self>,
        >,
    > + Send;
}
/// Extension trait for registering a service implementation with a Router.
///
/// This trait is automatically implemented for all types that implement the service trait.
/// Prefer [`Router::add_service`](::connectrpc::Router::add_service) for
/// top-down registration; `register` remains available for compatibility
/// and cases where the service-first call shape is more convenient.
///
/// # Example
///
/// ```rust,ignore
/// use std::sync::Arc;
///
/// let service = Arc::new(MyServiceImpl);
/// let router = service.register(Router::new());
/// ```
pub trait ProblemSupportServiceExt: ProblemSupportService {
    /// Register this service implementation with a Router.
    ///
    /// Takes ownership of the `Arc<Self>` and returns a new Router with
    /// this service's methods registered.
    fn register(
        self: ::std::sync::Arc<Self>,
        router: ::connectrpc::Router,
    ) -> ::connectrpc::Router;
}
impl<S: ProblemSupportService> ProblemSupportServiceExt for S {
    fn register(
        self: ::std::sync::Arc<Self>,
        router: ::connectrpc::Router,
    ) -> ::connectrpc::Router {
        router
            .route_view(
                PROBLEM_SUPPORT_SERVICE_SERVICE_NAME,
                "GetProblemInfo",
                {
                    let svc = ::std::sync::Arc::clone(&self);
                    ::connectrpc::view_handler_fn(move |
                        ctx,
                        req: ::buffa::view::OwnedView<
                            crate::proto::algobowl::problemsupport::v1::__buffa::view::GetProblemInfoRequestView<
                                'static,
                            >,
                        >,
                        format|
                    {
                        let svc = ::std::sync::Arc::clone(&svc);
                        async move {
                            let sreq = ::connectrpc::ServiceRequest::<
                                crate::proto::algobowl::problemsupport::v1::GetProblemInfoRequest,
                            >::from_parts(req.reborrow(), req.bytes());
                            svc.get_problem_info(ctx, sreq)
                                .await?
                                .encode::<
                                    crate::proto::algobowl::problemsupport::v1::GetProblemInfoResponse,
                                >(format)
                        }
                    })
                },
            )
            .with_spec(PROBLEM_SUPPORT_SERVICE_GET_PROBLEM_INFO_SPEC)
            .route_view(
                PROBLEM_SUPPORT_SERVICE_SERVICE_NAME,
                "VerifyInput",
                {
                    let svc = ::std::sync::Arc::clone(&self);
                    ::connectrpc::view_handler_fn(move |
                        ctx,
                        req: ::buffa::view::OwnedView<
                            crate::proto::algobowl::problemsupport::v1::__buffa::view::VerifyInputRequestView<
                                'static,
                            >,
                        >,
                        format|
                    {
                        let svc = ::std::sync::Arc::clone(&svc);
                        async move {
                            let sreq = ::connectrpc::ServiceRequest::<
                                crate::proto::algobowl::problemsupport::v1::VerifyInputRequest,
                            >::from_parts(req.reborrow(), req.bytes());
                            svc.verify_input(ctx, sreq)
                                .await?
                                .encode::<
                                    crate::proto::algobowl::problemsupport::v1::VerifyInputResponse,
                                >(format)
                        }
                    })
                },
            )
            .with_spec(PROBLEM_SUPPORT_SERVICE_VERIFY_INPUT_SPEC)
            .route_view(
                PROBLEM_SUPPORT_SERVICE_SERVICE_NAME,
                "VerifyOutput",
                {
                    let svc = ::std::sync::Arc::clone(&self);
                    ::connectrpc::view_handler_fn(move |
                        ctx,
                        req: ::buffa::view::OwnedView<
                            crate::proto::algobowl::problemsupport::v1::__buffa::view::VerifyOutputRequestView<
                                'static,
                            >,
                        >,
                        format|
                    {
                        let svc = ::std::sync::Arc::clone(&svc);
                        async move {
                            let sreq = ::connectrpc::ServiceRequest::<
                                crate::proto::algobowl::problemsupport::v1::VerifyOutputRequest,
                            >::from_parts(req.reborrow(), req.bytes());
                            svc.verify_output(ctx, sreq)
                                .await?
                                .encode::<
                                    crate::proto::algobowl::problemsupport::v1::VerifyOutputResponse,
                                >(format)
                        }
                    })
                },
            )
            .with_spec(PROBLEM_SUPPORT_SERVICE_VERIFY_OUTPUT_SPEC)
            .route_view(
                PROBLEM_SUPPORT_SERVICE_SERVICE_NAME,
                "GenerateInput",
                {
                    let svc = ::std::sync::Arc::clone(&self);
                    ::connectrpc::view_handler_fn(move |
                        ctx,
                        req: ::buffa::view::OwnedView<
                            crate::proto::algobowl::problemsupport::v1::__buffa::view::GenerateInputRequestView<
                                'static,
                            >,
                        >,
                        format|
                    {
                        let svc = ::std::sync::Arc::clone(&svc);
                        async move {
                            let sreq = ::connectrpc::ServiceRequest::<
                                crate::proto::algobowl::problemsupport::v1::GenerateInputRequest,
                            >::from_parts(req.reborrow(), req.bytes());
                            svc.generate_input(ctx, sreq)
                                .await?
                                .encode::<
                                    crate::proto::algobowl::problemsupport::v1::GenerateInputResponse,
                                >(format)
                        }
                    })
                },
            )
            .with_spec(PROBLEM_SUPPORT_SERVICE_GENERATE_INPUT_SPEC)
            .route_view(
                PROBLEM_SUPPORT_SERVICE_SERVICE_NAME,
                "Solve",
                {
                    let svc = ::std::sync::Arc::clone(&self);
                    ::connectrpc::view_handler_fn(move |
                        ctx,
                        req: ::buffa::view::OwnedView<
                            crate::proto::algobowl::problemsupport::v1::__buffa::view::SolveRequestView<
                                'static,
                            >,
                        >,
                        format|
                    {
                        let svc = ::std::sync::Arc::clone(&svc);
                        async move {
                            let sreq = ::connectrpc::ServiceRequest::<
                                crate::proto::algobowl::problemsupport::v1::SolveRequest,
                            >::from_parts(req.reborrow(), req.bytes());
                            svc.solve(ctx, sreq)
                                .await?
                                .encode::<
                                    crate::proto::algobowl::problemsupport::v1::SolveResponse,
                                >(format)
                        }
                    })
                },
            )
            .with_spec(PROBLEM_SUPPORT_SERVICE_SOLVE_SPEC)
    }
}
/// Type-inference marker used by [`Router::add_service`](::connectrpc::Router::add_service).
#[doc(hidden)]
pub struct ProblemSupportServiceRegisterMarker;
impl<
    S: ProblemSupportService,
> ::connectrpc::ServiceRegister<ProblemSupportServiceRegisterMarker>
for ::std::sync::Arc<S> {
    fn register_service(self, router: ::connectrpc::Router) -> ::connectrpc::Router {
        <S as ProblemSupportServiceExt>::register(self, router)
    }
}
/// Monomorphic dispatcher for `ProblemSupportService`.
///
/// Unlike `.register(Router)` which type-erases each method into an `Arc<dyn ErasedHandler>` stored in a `HashMap`, this struct dispatches via a compile-time `match` on method name: no vtable, no hash lookup.
///
/// # Example
///
/// ```rust,ignore
/// use connectrpc::ConnectRpcService;
///
/// let server = ProblemSupportServiceServer::new(MyImpl);
/// let service = ConnectRpcService::new(server);
/// // hand `service` to axum/hyper as a fallback_service
/// ```
pub struct ProblemSupportServiceServer<T> {
    inner: ::std::sync::Arc<T>,
}
impl<T: ProblemSupportService> ProblemSupportServiceServer<T> {
    /// Wrap a service implementation in a monomorphic dispatcher.
    pub fn new(service: T) -> Self {
        Self {
            inner: ::std::sync::Arc::new(service),
        }
    }
    /// Wrap an already-`Arc`'d service implementation.
    pub fn from_arc(inner: ::std::sync::Arc<T>) -> Self {
        Self { inner }
    }
}
impl<T> Clone for ProblemSupportServiceServer<T> {
    fn clone(&self) -> Self {
        Self {
            inner: ::std::sync::Arc::clone(&self.inner),
        }
    }
}
impl<T: ProblemSupportService> ::connectrpc::Dispatcher
for ProblemSupportServiceServer<T> {
    #[inline]
    fn lookup(
        &self,
        path: &str,
    ) -> Option<::connectrpc::dispatcher::codegen::MethodDescriptor> {
        let method = path
            .strip_prefix("algobowl.problemsupport.v1.ProblemSupportService/")?;
        match method {
            "GetProblemInfo" => {
                Some(
                    ::connectrpc::dispatcher::codegen::MethodDescriptor::unary(false)
                        .with_spec(PROBLEM_SUPPORT_SERVICE_GET_PROBLEM_INFO_SPEC),
                )
            }
            "VerifyInput" => {
                Some(
                    ::connectrpc::dispatcher::codegen::MethodDescriptor::unary(false)
                        .with_spec(PROBLEM_SUPPORT_SERVICE_VERIFY_INPUT_SPEC),
                )
            }
            "VerifyOutput" => {
                Some(
                    ::connectrpc::dispatcher::codegen::MethodDescriptor::unary(false)
                        .with_spec(PROBLEM_SUPPORT_SERVICE_VERIFY_OUTPUT_SPEC),
                )
            }
            "GenerateInput" => {
                Some(
                    ::connectrpc::dispatcher::codegen::MethodDescriptor::unary(false)
                        .with_spec(PROBLEM_SUPPORT_SERVICE_GENERATE_INPUT_SPEC),
                )
            }
            "Solve" => {
                Some(
                    ::connectrpc::dispatcher::codegen::MethodDescriptor::unary(false)
                        .with_spec(PROBLEM_SUPPORT_SERVICE_SOLVE_SPEC),
                )
            }
            _ => None,
        }
    }
    fn call_unary(
        &self,
        path: &str,
        ctx: ::connectrpc::RequestContext,
        request: ::connectrpc::Payload,
        format: ::connectrpc::CodecFormat,
    ) -> ::connectrpc::dispatcher::codegen::UnaryResult {
        let Some(method) = path
            .strip_prefix("algobowl.problemsupport.v1.ProblemSupportService/") else {
            return ::connectrpc::dispatcher::codegen::unimplemented_unary(path);
        };
        let _ = (&ctx, &request, &format);
        match method {
            "GetProblemInfo" => {
                let svc = ::std::sync::Arc::clone(&self.inner);
                Box::pin(async move {
                    let body = ::connectrpc::dispatcher::codegen::request_proto_bytes::<
                        crate::proto::algobowl::problemsupport::v1::GetProblemInfoRequest,
                    >(request.encoded()?, format)?;
                    let req: crate::proto::algobowl::problemsupport::v1::__buffa::view::GetProblemInfoRequestView<
                        '_,
                    > = ::connectrpc::dispatcher::codegen::decode_borrowed_request_view(
                        &body,
                        ctx.decode_options(),
                    )?;
                    let req = ::connectrpc::ServiceRequest::<
                        crate::proto::algobowl::problemsupport::v1::GetProblemInfoRequest,
                    >::from_parts(&req, &body);
                    svc.get_problem_info(ctx, req)
                        .await?
                        .encode::<
                            crate::proto::algobowl::problemsupport::v1::GetProblemInfoResponse,
                        >(format)
                })
            }
            "VerifyInput" => {
                let svc = ::std::sync::Arc::clone(&self.inner);
                Box::pin(async move {
                    let body = ::connectrpc::dispatcher::codegen::request_proto_bytes::<
                        crate::proto::algobowl::problemsupport::v1::VerifyInputRequest,
                    >(request.encoded()?, format)?;
                    let req: crate::proto::algobowl::problemsupport::v1::__buffa::view::VerifyInputRequestView<
                        '_,
                    > = ::connectrpc::dispatcher::codegen::decode_borrowed_request_view(
                        &body,
                        ctx.decode_options(),
                    )?;
                    let req = ::connectrpc::ServiceRequest::<
                        crate::proto::algobowl::problemsupport::v1::VerifyInputRequest,
                    >::from_parts(&req, &body);
                    svc.verify_input(ctx, req)
                        .await?
                        .encode::<
                            crate::proto::algobowl::problemsupport::v1::VerifyInputResponse,
                        >(format)
                })
            }
            "VerifyOutput" => {
                let svc = ::std::sync::Arc::clone(&self.inner);
                Box::pin(async move {
                    let body = ::connectrpc::dispatcher::codegen::request_proto_bytes::<
                        crate::proto::algobowl::problemsupport::v1::VerifyOutputRequest,
                    >(request.encoded()?, format)?;
                    let req: crate::proto::algobowl::problemsupport::v1::__buffa::view::VerifyOutputRequestView<
                        '_,
                    > = ::connectrpc::dispatcher::codegen::decode_borrowed_request_view(
                        &body,
                        ctx.decode_options(),
                    )?;
                    let req = ::connectrpc::ServiceRequest::<
                        crate::proto::algobowl::problemsupport::v1::VerifyOutputRequest,
                    >::from_parts(&req, &body);
                    svc.verify_output(ctx, req)
                        .await?
                        .encode::<
                            crate::proto::algobowl::problemsupport::v1::VerifyOutputResponse,
                        >(format)
                })
            }
            "GenerateInput" => {
                let svc = ::std::sync::Arc::clone(&self.inner);
                Box::pin(async move {
                    let body = ::connectrpc::dispatcher::codegen::request_proto_bytes::<
                        crate::proto::algobowl::problemsupport::v1::GenerateInputRequest,
                    >(request.encoded()?, format)?;
                    let req: crate::proto::algobowl::problemsupport::v1::__buffa::view::GenerateInputRequestView<
                        '_,
                    > = ::connectrpc::dispatcher::codegen::decode_borrowed_request_view(
                        &body,
                        ctx.decode_options(),
                    )?;
                    let req = ::connectrpc::ServiceRequest::<
                        crate::proto::algobowl::problemsupport::v1::GenerateInputRequest,
                    >::from_parts(&req, &body);
                    svc.generate_input(ctx, req)
                        .await?
                        .encode::<
                            crate::proto::algobowl::problemsupport::v1::GenerateInputResponse,
                        >(format)
                })
            }
            "Solve" => {
                let svc = ::std::sync::Arc::clone(&self.inner);
                Box::pin(async move {
                    let body = ::connectrpc::dispatcher::codegen::request_proto_bytes::<
                        crate::proto::algobowl::problemsupport::v1::SolveRequest,
                    >(request.encoded()?, format)?;
                    let req: crate::proto::algobowl::problemsupport::v1::__buffa::view::SolveRequestView<
                        '_,
                    > = ::connectrpc::dispatcher::codegen::decode_borrowed_request_view(
                        &body,
                        ctx.decode_options(),
                    )?;
                    let req = ::connectrpc::ServiceRequest::<
                        crate::proto::algobowl::problemsupport::v1::SolveRequest,
                    >::from_parts(&req, &body);
                    svc.solve(ctx, req)
                        .await?
                        .encode::<
                            crate::proto::algobowl::problemsupport::v1::SolveResponse,
                        >(format)
                })
            }
            _ => ::connectrpc::dispatcher::codegen::unimplemented_unary(path),
        }
    }
    fn call_server_streaming(
        &self,
        path: &str,
        ctx: ::connectrpc::RequestContext,
        request: ::buffa::bytes::Bytes,
        format: ::connectrpc::CodecFormat,
    ) -> ::connectrpc::dispatcher::codegen::StreamingResult {
        let Some(method) = path
            .strip_prefix("algobowl.problemsupport.v1.ProblemSupportService/") else {
            return ::connectrpc::dispatcher::codegen::unimplemented_streaming(path);
        };
        let _ = (&ctx, &request, &format);
        match method {
            _ => ::connectrpc::dispatcher::codegen::unimplemented_streaming(path),
        }
    }
    fn call_client_streaming(
        &self,
        path: &str,
        ctx: ::connectrpc::RequestContext,
        requests: ::connectrpc::dispatcher::codegen::RequestStream,
        format: ::connectrpc::CodecFormat,
    ) -> ::connectrpc::dispatcher::codegen::UnaryResult {
        let Some(method) = path
            .strip_prefix("algobowl.problemsupport.v1.ProblemSupportService/") else {
            return ::connectrpc::dispatcher::codegen::unimplemented_unary(path);
        };
        let _ = (&ctx, &requests, &format);
        match method {
            _ => ::connectrpc::dispatcher::codegen::unimplemented_unary(path),
        }
    }
    fn call_bidi_streaming(
        &self,
        path: &str,
        ctx: ::connectrpc::RequestContext,
        requests: ::connectrpc::dispatcher::codegen::RequestStream,
        format: ::connectrpc::CodecFormat,
    ) -> ::connectrpc::dispatcher::codegen::StreamingResult {
        let Some(method) = path
            .strip_prefix("algobowl.problemsupport.v1.ProblemSupportService/") else {
            return ::connectrpc::dispatcher::codegen::unimplemented_streaming(path);
        };
        let _ = (&ctx, &requests, &format);
        match method {
            _ => ::connectrpc::dispatcher::codegen::unimplemented_streaming(path),
        }
    }
}
/// Client for this service.
///
/// Generic over `T: ClientTransport`. For **gRPC** (HTTP/2), use
/// `Http2Connection` — it has honest `poll_ready` and composes with
/// `tower::balance` for multi-connection load balancing. For **Connect
/// over HTTP/1.1** (or unknown protocol), use `HttpClient`.
///
/// # Example (gRPC / HTTP/2)
///
/// ```rust,ignore
/// use connectrpc::client::{Http2Connection, ClientConfig};
/// use connectrpc::Protocol;
///
/// let uri: http::Uri = "http://localhost:8080".parse()?;
/// let conn = Http2Connection::connect_plaintext(uri.clone()).await?.shared(1024);
/// let config = ClientConfig::new(uri).with_protocol(Protocol::Grpc);
///
/// let client = ProblemSupportServiceClient::new(conn, config);
/// let response = client.get_problem_info(request).await?;
/// ```
///
/// # Example (Connect / HTTP/1.1 or ALPN)
///
/// ```rust,ignore
/// use connectrpc::client::{HttpClient, ClientConfig};
///
/// let http = HttpClient::plaintext();  // cleartext http:// only
/// let config = ClientConfig::new("http://localhost:8080".parse()?);
///
/// let client = ProblemSupportServiceClient::new(http, config);
/// let response = client.get_problem_info(request).await?;
/// ```
///
/// # Working with the response
///
/// Unary calls return [`UnaryResponse<OwnedView<FooView>>`](::connectrpc::client::UnaryResponse).
/// [`view()`](::connectrpc::client::UnaryResponse::view) borrows the response
/// message, so field access is zero-copy:
///
/// ```rust,ignore
/// let resp = client.get_problem_info(request).await?;
/// let name: &str = resp.view().name;  // borrow into the response buffer
/// ```
///
/// If you need the owned struct (e.g. to store or pass by value), use
/// [`into_owned()`](::connectrpc::client::UnaryResponse::into_owned):
///
/// ```rust,ignore
/// let owned = client.get_problem_info(request).await?.into_owned();
/// ```
///
/// [`into_view()`](::connectrpc::client::UnaryResponse::into_view) keeps the
/// zero-copy decoded body (an `OwnedView`) without copying; field access on it
/// goes through `.reborrow()`. Streaming responses yield one
/// [`StreamMessage`](::connectrpc::StreamMessage) per received message from
/// `.message().await` — read fields zero-copy through the generated accessor
/// methods (`msg.name()`) or `.view()`, or convert with `.to_owned_message()`.
#[derive(Clone)]
pub struct ProblemSupportServiceClient<T> {
    transport: T,
    config: ::connectrpc::client::ClientConfig,
}
impl<T> ProblemSupportServiceClient<T>
where
    T: ::connectrpc::client::ClientTransport,
    <T::ResponseBody as ::connectrpc::http_body::Body>::Error: ::std::fmt::Display,
{
    /// Create a new client with the given transport and configuration.
    pub fn new(transport: T, config: ::connectrpc::client::ClientConfig) -> Self {
        Self { transport, config }
    }
    /// Get the client configuration.
    pub fn config(&self) -> &::connectrpc::client::ClientConfig {
        &self.config
    }
    /// Get a mutable reference to the client configuration.
    pub fn config_mut(&mut self) -> &mut ::connectrpc::client::ClientConfig {
        &mut self.config
    }
    /// Call the GetProblemInfo RPC. Sends a request to /algobowl.problemsupport.v1.ProblemSupportService/GetProblemInfo.
    pub async fn get_problem_info(
        &self,
        request: crate::proto::algobowl::problemsupport::v1::GetProblemInfoRequest,
    ) -> Result<
        ::connectrpc::client::UnaryResponse<
            ::buffa::view::OwnedView<
                crate::proto::algobowl::problemsupport::v1::__buffa::view::GetProblemInfoResponseView<
                    'static,
                >,
            >,
        >,
        ::connectrpc::ConnectError,
    > {
        self.get_problem_info_with_options(
                request,
                ::connectrpc::client::CallOptions::default(),
            )
            .await
    }
    /// Call the GetProblemInfo RPC with explicit per-call options. Options override [`ClientConfig`](::connectrpc::client::ClientConfig) defaults.
    pub async fn get_problem_info_with_options(
        &self,
        request: crate::proto::algobowl::problemsupport::v1::GetProblemInfoRequest,
        options: ::connectrpc::client::CallOptions,
    ) -> Result<
        ::connectrpc::client::UnaryResponse<
            ::buffa::view::OwnedView<
                crate::proto::algobowl::problemsupport::v1::__buffa::view::GetProblemInfoResponseView<
                    'static,
                >,
            >,
        >,
        ::connectrpc::ConnectError,
    > {
        ::connectrpc::client::call_unary(
                &self.transport,
                &self.config,
                PROBLEM_SUPPORT_SERVICE_GET_PROBLEM_INFO_SPEC
                    .with_origin(::connectrpc::SpecOrigin::Client),
                request,
                options,
            )
            .await
    }
    /// Call the VerifyInput RPC. Sends a request to /algobowl.problemsupport.v1.ProblemSupportService/VerifyInput.
    pub async fn verify_input(
        &self,
        request: crate::proto::algobowl::problemsupport::v1::VerifyInputRequest,
    ) -> Result<
        ::connectrpc::client::UnaryResponse<
            ::buffa::view::OwnedView<
                crate::proto::algobowl::problemsupport::v1::__buffa::view::VerifyInputResponseView<
                    'static,
                >,
            >,
        >,
        ::connectrpc::ConnectError,
    > {
        self.verify_input_with_options(
                request,
                ::connectrpc::client::CallOptions::default(),
            )
            .await
    }
    /// Call the VerifyInput RPC with explicit per-call options. Options override [`ClientConfig`](::connectrpc::client::ClientConfig) defaults.
    pub async fn verify_input_with_options(
        &self,
        request: crate::proto::algobowl::problemsupport::v1::VerifyInputRequest,
        options: ::connectrpc::client::CallOptions,
    ) -> Result<
        ::connectrpc::client::UnaryResponse<
            ::buffa::view::OwnedView<
                crate::proto::algobowl::problemsupport::v1::__buffa::view::VerifyInputResponseView<
                    'static,
                >,
            >,
        >,
        ::connectrpc::ConnectError,
    > {
        ::connectrpc::client::call_unary(
                &self.transport,
                &self.config,
                PROBLEM_SUPPORT_SERVICE_VERIFY_INPUT_SPEC
                    .with_origin(::connectrpc::SpecOrigin::Client),
                request,
                options,
            )
            .await
    }
    /// Call the VerifyOutput RPC. Sends a request to /algobowl.problemsupport.v1.ProblemSupportService/VerifyOutput.
    pub async fn verify_output(
        &self,
        request: crate::proto::algobowl::problemsupport::v1::VerifyOutputRequest,
    ) -> Result<
        ::connectrpc::client::UnaryResponse<
            ::buffa::view::OwnedView<
                crate::proto::algobowl::problemsupport::v1::__buffa::view::VerifyOutputResponseView<
                    'static,
                >,
            >,
        >,
        ::connectrpc::ConnectError,
    > {
        self.verify_output_with_options(
                request,
                ::connectrpc::client::CallOptions::default(),
            )
            .await
    }
    /// Call the VerifyOutput RPC with explicit per-call options. Options override [`ClientConfig`](::connectrpc::client::ClientConfig) defaults.
    pub async fn verify_output_with_options(
        &self,
        request: crate::proto::algobowl::problemsupport::v1::VerifyOutputRequest,
        options: ::connectrpc::client::CallOptions,
    ) -> Result<
        ::connectrpc::client::UnaryResponse<
            ::buffa::view::OwnedView<
                crate::proto::algobowl::problemsupport::v1::__buffa::view::VerifyOutputResponseView<
                    'static,
                >,
            >,
        >,
        ::connectrpc::ConnectError,
    > {
        ::connectrpc::client::call_unary(
                &self.transport,
                &self.config,
                PROBLEM_SUPPORT_SERVICE_VERIFY_OUTPUT_SPEC
                    .with_origin(::connectrpc::SpecOrigin::Client),
                request,
                options,
            )
            .await
    }
    /// Call the GenerateInput RPC. Sends a request to /algobowl.problemsupport.v1.ProblemSupportService/GenerateInput.
    pub async fn generate_input(
        &self,
        request: crate::proto::algobowl::problemsupport::v1::GenerateInputRequest,
    ) -> Result<
        ::connectrpc::client::UnaryResponse<
            ::buffa::view::OwnedView<
                crate::proto::algobowl::problemsupport::v1::__buffa::view::GenerateInputResponseView<
                    'static,
                >,
            >,
        >,
        ::connectrpc::ConnectError,
    > {
        self.generate_input_with_options(
                request,
                ::connectrpc::client::CallOptions::default(),
            )
            .await
    }
    /// Call the GenerateInput RPC with explicit per-call options. Options override [`ClientConfig`](::connectrpc::client::ClientConfig) defaults.
    pub async fn generate_input_with_options(
        &self,
        request: crate::proto::algobowl::problemsupport::v1::GenerateInputRequest,
        options: ::connectrpc::client::CallOptions,
    ) -> Result<
        ::connectrpc::client::UnaryResponse<
            ::buffa::view::OwnedView<
                crate::proto::algobowl::problemsupport::v1::__buffa::view::GenerateInputResponseView<
                    'static,
                >,
            >,
        >,
        ::connectrpc::ConnectError,
    > {
        ::connectrpc::client::call_unary(
                &self.transport,
                &self.config,
                PROBLEM_SUPPORT_SERVICE_GENERATE_INPUT_SPEC
                    .with_origin(::connectrpc::SpecOrigin::Client),
                request,
                options,
            )
            .await
    }
    /// Call the Solve RPC. Sends a request to /algobowl.problemsupport.v1.ProblemSupportService/Solve.
    pub async fn solve(
        &self,
        request: crate::proto::algobowl::problemsupport::v1::SolveRequest,
    ) -> Result<
        ::connectrpc::client::UnaryResponse<
            ::buffa::view::OwnedView<
                crate::proto::algobowl::problemsupport::v1::__buffa::view::SolveResponseView<
                    'static,
                >,
            >,
        >,
        ::connectrpc::ConnectError,
    > {
        self.solve_with_options(request, ::connectrpc::client::CallOptions::default())
            .await
    }
    /// Call the Solve RPC with explicit per-call options. Options override [`ClientConfig`](::connectrpc::client::ClientConfig) defaults.
    pub async fn solve_with_options(
        &self,
        request: crate::proto::algobowl::problemsupport::v1::SolveRequest,
        options: ::connectrpc::client::CallOptions,
    ) -> Result<
        ::connectrpc::client::UnaryResponse<
            ::buffa::view::OwnedView<
                crate::proto::algobowl::problemsupport::v1::__buffa::view::SolveResponseView<
                    'static,
                >,
            >,
        >,
        ::connectrpc::ConnectError,
    > {
        ::connectrpc::client::call_unary(
                &self.transport,
                &self.config,
                PROBLEM_SUPPORT_SERVICE_SOLVE_SPEC
                    .with_origin(::connectrpc::SpecOrigin::Client),
                request,
                options,
            )
            .await
    }
}
