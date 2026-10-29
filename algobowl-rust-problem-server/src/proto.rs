//! Protobuf messages and Connect service stubs for the problem support service.
//!
//! The code in `generated/` is produced by `buf generate` from the repository
//! root.

#![allow(clippy::all)]

pub mod algobowl {
    pub mod problemsupport {
        pub mod v1 {
            include!("generated/buffa/algobowl.problemsupport.v1.mod.rs");
            include!("generated/connect/algobowl.problemsupport.v1.mod.rs");
        }
    }
}
