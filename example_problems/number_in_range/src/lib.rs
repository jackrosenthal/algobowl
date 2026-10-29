//! Example problem: report a number in a range.
//!
//! An input is two lines, `low` and `high`.  An output is a single number
//! between `low` and `high`, which is its score.

use std::fmt::Write;

use algops::problemlib::{self, FileFormatError, Rng, VerificationError};
use algops::{Problem, RankSort, Statement};
use worker::{Context, Env, Request, Response, event};

static PROBLEM: Problem<Input, Output> = Problem {
    rank_sort: RankSort::Minimization,
    score_decimal_places: 0,
    statements: &[
        Statement::pdf("/statement.pdf"),
        Statement::markdown("/statement.md"),
    ],
    generate: Some(Input::generate),
    trivial_solve: Some(Input::trivial_solve),
};

#[event(fetch)]
async fn fetch(req: Request, _env: Env, _ctx: Context) -> worker::Result<Response> {
    PROBLEM.serve(req).await
}

pub struct Input {
    low: i64,
    high: i64,
}

impl Input {
    fn generate(rng: &mut Rng) -> Self {
        let low = 1 + rng.below(100) as i64;
        let high = low + rng.below((101 - low) as u64) as i64;
        Input { low, high }
    }

    fn trivial_solve(&self) -> Output {
        Output { score: self.high }
    }
}

impl algops::Input for Input {
    fn read(mut lines: Vec<&str>) -> Result<Self, FileFormatError> {
        problemlib::assert_linecount(&mut lines, 2)?;
        let low = problemlib::parse_line_int(&lines, 0, 1..101)?;
        let high = problemlib::parse_line_int(&lines, 1, 1..101)?;
        if low > high {
            return Err(FileFormatError(
                "low must be less than or equal to high".to_owned(),
            ));
        }
        Ok(Input { low, high })
    }

    fn write(&self, out: &mut String) {
        writeln!(out, "{}", self.low).unwrap();
        writeln!(out, "{}", self.high).unwrap();
    }
}

pub struct Output {
    score: i64,
}

impl algops::Output<Input> for Output {
    fn read(_input: &Input, mut lines: Vec<&str>) -> Result<Self, FileFormatError> {
        problemlib::assert_linecount(&mut lines, 1)?;
        let score = problemlib::parse_line_int(&lines, 0, 1..101)?;
        Ok(Output { score })
    }

    fn write(&self, out: &mut String) {
        writeln!(out, "{}", self.score).unwrap();
    }

    fn score(&self) -> i64 {
        self.score
    }

    fn verify(&self, input: &Input) -> Result<Option<i64>, VerificationError> {
        if self.score > input.high {
            return Err(VerificationError("Score is too high".to_owned()));
        }
        if self.score < input.low {
            return Err(VerificationError("Score is too low".to_owned()));
        }
        Ok(Some(self.score))
    }
}
