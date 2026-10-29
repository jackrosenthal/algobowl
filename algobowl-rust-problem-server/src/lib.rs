//! Framework for AlgoBOWL problem support services on Cloudflare Workers.
//!
//! A problem implements [`Input`] and [`Output`], describes itself with a
//! [`Problem`], and serves requests with [`Problem::serve`].

pub mod problemlib;
pub mod proto;
mod service;

pub use proto::algobowl::problemsupport::v1::RankSort;
pub use rand;
pub use service::{Input, Output, Problem, Statement};
