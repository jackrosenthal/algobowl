# AlgoBOWL Problem Format

If you're reading this document, you've likely been tasked with implementing the
support code for an AlgoBOWL problem.  This code provides problem-specific
support to the AlgoBOWL website.  The website uses it to do all of the
following:

* Determine if the problem is a minimization or maximization problem.
* Validate input files are of correct format.
* Re-format and normalize input files so they are presented in a consistent
  manner to everyone.
* Generate random inputs for groups that do not upload one.
* Validate output files are of correct format.
* Re-format and normalize output files so they are presented in a consistent
  manner to everyone.
* Determine an integer score from output files.
* Verify outputs, which is used behind the scenes to provide the instructor a
  view of verification accuracy (and reduce the grade of groups with inaccurate
  verifications).
* Serve the problem statement.

Each problem is a Rust program that runs as a [Cloudflare
Worker](https://developers.cloudflare.com/workers/), using the `algops` crate in
the `algobowl-rust-problem-server` directory of this repository.  The website
talks to it using the problem support service defined in
`proto/algobowl/problemsupport/v1/problem_support.proto`.

## Get access to the private problems repository

With the exception of the example problem (located at
`example_problems/number_in_range` in this repository), all problems are stored
in a private repository located here:

https://github.com/jackrosenthal/algobowl-problems

The reason the problems are in a private repository is because they provide an
implementation of the verifier, which is something that current students are
required to implement on their own.

Validate you have access (requesting it from Jack if necessary).  This is where
you are going to push your problem implementation.

## Set up your tools

You'll need:

* [rustup](https://rustup.rs/).  Each problem pins its Rust version in
  `rust-toolchain.toml`, and rustup installs it automatically.
* [Node.js](https://nodejs.org/), to run `wrangler`, the Cloudflare Workers
  tool.  Problems are built and served with `npx wrangler@4.151.0`.
* The AlgoBOWL CLI, which runs the problem tester.  Set it up by following
  [these instructions](./cli.md).

Validate you can run the problem tester on the example problem.  In one
terminal, serve the example problem:

```shellsession
$ cd example_problems/number_in_range
$ npx wrangler@4.151.0 dev --local
```

The first build takes a few minutes.  Then, in another terminal, run the
problem tester against it:

```shellsession
$ algobowl problem http://127.0.0.1:8787 test example_problems/number_in_range/test_data
```

## Writing a new problem

A problem is a directory containing:

* `Cargo.toml`, `rust-toolchain.toml`, and `wrangler.jsonc`, which describe how
  to build and serve the problem.
* `src/lib.rs`, containing the problem support code.
* `public/statement.pdf`, which has the problem statement.  You may also
  provide `public/statement.md`.  Everything in `public` is served alongside the
  problem.
* `test_data`, a directory containing sample inputs and outputs (explained
  further later).

Start by copying the example problem into the private problems repository.  By
convention, please use `snake_case` for the directory name.  Then copy in the
problem statement, and clear out the example's test data:

```shellsession
$ cp -r ~/algobowl/example_problems/number_in_range ~/algobowl-problems/my_problem
$ cd ~/algobowl-problems/my_problem
$ cp ~/Downloads/AlgoBOWL.pdf public/statement.pdf
$ rm -rf public/statement.md Cargo.lock test_data/*/*/*
```

Then update the following:

* In `Cargo.toml`, rename the package to `algobowl-problem-my-problem`, and
  change the `algops` dependency from a path to a git revision, the same way as
  the other problems.  Use the latest commit that changed
  `algobowl-rust-problem-server`.
* In `wrangler.jsonc`, rename the worker to `my-problem`.  Worker names may only
  contain lowercase letters, numbers, and dashes.

Keep `"workers_dev": false` and `"preview_urls": true` in `wrangler.jsonc`.  This
makes the problem reachable only through version URLs (explained later).

## `src/lib.rs` essentials

`src/lib.rs` describes the problem with a `Problem`, and serves it from the
Worker's `fetch` handler:

```rust
use std::fmt::Write;

use algops::problemlib::{self, FileFormatError, VerificationError};
use algops::rand::prelude::*;
use algops::{Problem, RankSort, Statement};
use worker::{Context, Env, Request, Response, event};

static PROBLEM: Problem<Input, Output> = Problem {
    rank_sort: RankSort::Minimization,
    score_decimal_places: 0,
    statements: &[Statement::pdf("/statement.pdf")],
    generate: Some(Input::generate),
    trivial_solve: Some(Input::trivial_solve),
};

#[event(fetch)]
async fn fetch(req: Request, _env: Env, _ctx: Context) -> worker::Result<Response> {
    PROBLEM.serve(req).await
}
```

* `rank_sort` is `RankSort::Minimization` if lower scores are better, or
  `RankSort::Maximization` if higher scores are better.
* `score_decimal_places` controls how scores are displayed.  Scores are always
  integers, so a problem with scores like `23.25` stores them in hundredths
  (`2325`), and sets this to `2`.
* `statements` lists the problem statements.  URLs starting with `/` are served
  from `public`.
* `generate` and `trivial_solve` are optional (`None` if not implemented), and
  are explained below.

You then implement the `algops::Input` trait for your `Input` type, and the
`algops::Output<Input>` trait for your `Output` type.

## Implementing the `Input` type

The `read` function receives the lines of the input file, and returns an
`Input`:

```rust
impl algops::Input for Input {
    fn read(mut lines: Vec<&str>) -> Result<Self, FileFormatError> {
        ...
    }
}
```

Lines are split with `str::lines`, so they do not include their line endings.
Windows (`\r\n`) and old Mac (`\r`) line endings are both handled.

If the input does not conform to the specifications, `read` should return a
`FileFormatError`.  Make sure to use a good error message.  This is what students
will see when they get an error during upload.

While you could do all the input parsing yourself, `problemlib` provides a
number of helpers that will make this easier.  The typical pattern is:

```rust
// Assert the input has a valid number of lines.  Below, we say we need at least
// 3 lines, and no more than 20 lines.
problemlib::assert_linecount(&mut lines, 3..21)?;

// Read an integer from the first line.
let n = problemlib::parse_line_int(&lines, 0, 0..101)?;

// Read n integers from the second line.
let list_of_ints = problemlib::parse_line_ints(&lines, 1, 0..n, n)?;

...

Ok(Input { n, list_of_ints, ... })
```

The above code doesn't make much sense, but hopefully it provides for a source
of inspiration.  You can also read other problems for further inspiration.

The `Input` type should also implement `write`, which writes a normalized input:

```rust
fn write(&self, out: &mut String) {
    writeln!(out, "{}", self.n).unwrap();
    ...
}
```

The `Input` type should also provide a `generate` function to generate a random
input.  This will be used to create default inputs for each group should they
fail to upload an input.  It takes a seeded `StdRng` from the
[`rand`](https://docs.rs/rand/0.10) crate, which `algops` re-exports as
`algops::rand`.  *You should not use random numbers except from this object.*
The tests use a fixed set of seeds so they are reproducible.

For example:

```rust
fn generate(rng: &mut StdRng) -> Self {
    let list_of_ints = (0..20).map(|_| rng.random_range(0..=100)).collect();
    Input { list_of_ints, ... }
}
```

## Writing example inputs

Now that you've written the `Input` type, it's time to write example inputs.

You should write two kinds of inputs:

* `test_data/inputs/good/*.in`, with examples of good inputs.
* `test_data/inputs/bad/*.in`, with examples of inputs that should cause errors
  during upload.

Typically, the example input from the problem statement should be put
in `test_data/inputs/good/example.in`.  You should write more inputs as well
(for example, inputs which are at the bounds of the problem).

Once you've written some example inputs, serve your problem with
`npx wrangler@4.151.0 dev --local`, and run the problem tester to test them:

```shellsession
$ algobowl problem http://127.0.0.1:8787 test test_data
```

`wrangler dev` rebuilds the problem when you change `src`.

## Implementing the `Output` type

The `read` function receives the input and the lines of the output file, and
returns an `Output`:

```rust
impl algops::Output<Input> for Output {
    fn read(input: &Input, mut lines: Vec<&str>) -> Result<Self, FileFormatError> {
        ...
    }
}
```

Make good use of the helpers in `problemlib` to help you with the parsing here,
similar to what you did for the `Input` type.

Your `read` function should return a `FileFormatError` if there's an error in
the file format.  **Note:** `read` is not the right place to point out
verification errors.  Simply parse the output, even if there's verification
issues.

Similar to the `Input` type, you should also implement `write`.

`score` returns the score the student reported in the output, not the actual
score of the output.

Finally, you need to implement `verify`, which returns the actual score of the
output (which may not be what `score` returns).  If the scores differ, this will
result in a verification issue.

```rust
fn verify(&self, input: &Input) -> Result<Option<i64>, VerificationError> {
    ...
    Ok(Some(score))
}
```

`verify` may also return a `VerificationError` if there's a verification issue
that's not the score differing from the reported value.  As with file format
errors, your error message should be descriptive, however, it will not be seen
by students.  The message will be logged in the backend for the instructor's
viewing purposes.

If the reported score cannot be wrong (for example, if the score is the number
of lines in the output), `verify` may check validity only, and return
`Ok(None)`.

## Writing example outputs

Now that you've implemented the `Output` type, you're nearly done.  It's time to
make test data.

Populate the following files:

* `test_data/outputs/good/*.{in,out}` should be input/output pairs for good
  outputs.
* `test_data/outputs/bad/*.{in,out}` should be input/output pairs for outputs
  with file formatting errors.
* `test_data/outputs/rejected/*.{in,out}` should be input/output pairs for
  outputs that should lead to a verification error.

Your `*.in` files should always be a relative symlink to a file in the
`test_data/inputs/good` directory:

```shellsession
$ readlink test_data/outputs/good/example_opt.in
../../inputs/good/example.in
```

**Tip:** The `cp` command will dereference the symlink by default when doing a
copy.  If you're writing multiple outputs with the same input, using the `-P`
flag to `cp` will preserve the symlink.

Once you've created sufficient examples, run the tester again and watch your new
test cases pass!

## Optional: Implement a trivial solver

While it's not required, it's highly recommended to implement a trivial solver
for the problem.  This solver will be used by tests to provide a little fuzz
coverage when coupled with `generate`.

You should implement the absolute most trivial solution for the problem
possible.  Think: *how can I make the answer as bad as possible?*

```rust
fn trivial_solve(&self) -> Output {
    Output { ... }
}
```

## Performance

Cloudflare limits the CPU time each request may use, and the limit is small on
the free plan.  Inputs and outputs can be large, so keep the support code
efficient:

* Parse lines with a fixed number of integers using `parse_line_ints_array` or
  `parse_line_ints_each`, which do not allocate.
* Prefer flat `Vec`s indexed by position over maps and sets.
* Use the [`itoa`](https://docs.rs/itoa) crate instead of `write!` when writing
  many integers.

Test your problem with the largest possible inputs on Cloudflare itself by
serving it with `npx wrangler@4.151.0 dev --remote` and running the problem
tester against it.  Look for `Worker exceeded CPU time limit` in the output.

## Uploading for review

Create a new branch and commit your changes (including `Cargo.lock`):

```shellsession
$ git checkout -b problem_id
$ git add .
$ git commit -m "Add new problem problem_id"
$ git push -u origin problem_id
```

Then, open a pull request in the GitHub UI.  CI will build your problem and run
the problem tester on it.

When changes are requested, please amend/rebase your commits instead of creating
"fixup commits".  You'll need to use `--force` when updating your PR for review.

## Deploying

When changes to a problem are merged to `main`, CI deploys a new version of the
problem.  Each version is only reachable at its own version URL:

```
https://<version>-<worker name>.<subdomain>.workers.dev
```

where `<version>` is the first eight characters of the version ID.  List the
versions of a problem with `npx wrangler@4.151.0 versions list --name <worker
name>`.

A competition's problem is the version URL, so a competition keeps using the
same version even when the problem is changed later.

## Reference: problemlib helpers

Here's what `problemlib` provides to you to help you with parsing.  Line numbers
passed to these functions are zero-based, and error messages show them
one-based.

### `Bound`

The allowed values for an integer or a line count.  Most functions take
`impl Into<Bound>`, so you can pass an integer for an exact value, or a range
like `1..101` for values from 1 to 100.

* `Bound::Any`: any value is allowed.
* `Bound::Exact(value)`: only this value is allowed.
* `Bound::Range(start, end)`: values from `start` (inclusive) to `end`
  (exclusive) are allowed.
* `Bound::RangeExcluding(start, end, excluded)`: like `Range`, but `excluded` is
  not allowed.

### `assert_linecount`

```rust
assert_linecount(lines: &mut Vec<&str>, bound: impl Into<Bound>)
```

Asserts the number of lines in the file is within the bound.  If not, blank
lines at the end of the file are removed until it is.

### `check_bound`

```rust
check_bound(lineno: usize, bound: impl Into<Bound>, value: i64)
```

Asserts a value found on a line is within the bound.

### `parse_int`

```rust
parse_int(lineno: usize, value: &str, bound: impl Into<Bound>) -> i64
```

Parses an integer with `str::parse` and checks its bound.  Normally you should
use the line parsing functions below instead.

### `parse_line_ints`

```rust
parse_line_ints(lines: &[&str], lineno: usize, bound: impl Into<Bound>, count: impl Into<Bound>) -> Vec<i64>
```

Parses the whitespace-separated integers on a line.  `count` bounds the number
of integers on the line.

### `parse_line_int`

```rust
parse_line_int(lines: &[&str], lineno: usize, bound: impl Into<Bound>) -> i64
```

Parses a line containing exactly one integer.

### `parse_line_ints_array`

```rust
parse_line_ints_array::<N>(lines: &[&str], lineno: usize, bound: impl Into<Bound>) -> [i64; N]
```

Parses a line containing exactly `N` integers, without allocating.  Errors are
the same as `parse_line_ints`.

### `parse_line_ints_each`

```rust
parse_line_ints_each::<N>(lines: &[&str], lineno: usize, bounds: [Bound; N]) -> [i64; N]
```

Like `parse_line_ints_array`, but with a separate bound for each integer.

### Everything else

Use the standard library for anything else.  For example, `str::split_whitespace`
splits a line into values, and formatting a character or string with `{:?}`
quotes it for an error message.
