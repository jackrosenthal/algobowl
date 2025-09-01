# AlgoBOWL Problem Format

If you're reading this document, you've likely been tasked with implementing the
support code for an AlgoBOWL problem.  This code provides problem-specific
support to the AlgoBOWL website.  The website uses it to do all of the
following:

* Determine if problem is a minimization or maximization problem.
* Validate input files are of correct format.
* Re-format and normalize input files so they are presented in a consistent
  manner to everyone.
* Validate output files are of correct format.
* Re-format and normalize output files so they are presented in a consistent
  manner to everyone.
* Determine an integer score from output files.
* Verify outputs, which is used behind the scenes to provide the instructor a
  view of verification accuracy (and reduce the grade of groups with inaccurate
  verifications).

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

## Set up the AlgoBOWL CLI

The AlgoBOWL CLI is used to run the problem tester.  Set it up by following
[these instructions](./cli.md).

Clone this repository, and create a new Python virtual environment:

```shellsession
$ git clone https://github.com/jackrosenthal/algobowl
$ cd algobowl
$ python -m venv venv
```

Source the virtual environment:

```shellsession
$ . venv/bin/activate
```

Install using pip:

```shellsession
$ pip install .
```

Finally, validate you can now run the problem tester on the example problem:

```shellsession
$ algobowl problem example_problems/number_in_range test
```

## Writing a new problem

A problem is a directory containing:

* `problem.py` containing the problem support code.
* `statement.pdf`, which has the problem statement.
* `test_data`, a directory containing sample inputs and outputs (explained
  further later).

Go ahead and create a new directory in the private problems repository.  By
convention, please use `snake_case` for the directory name.  In this directory,
copy in the problem statement under `statement.pdf`, add an empty `problem.py`,
and create the empty `test_data` directory and subdirectories.

```shellsession
$ cd ~/algobowl-problems
$ mkdir my_problem
$ cd my_problem
$ cp ~/Downloads/AlgoBOWL.pdf statement.pdf
$ touch problem.py
$ mkdir -p test_data/inputs/{good,bad} test_data/outputs/{good,bad,rejected}
```

## `problem.py` essentials

The AlgoBOWL application expects `problem.py` to be a Python module containing:

- A dataclass named `Input`, which provides the input implementation.  This
  should subclass from `algobowl.lib.problem.BaseInput`.
- A dataclass named `Output`, which provides the output implementation.  This
  should subclass from `algobowl.lib.problem.BaseOutput`.

You may create other members in this module (e.g., helper functions), but
AlgoBOWL only looks at the `Input` and `Output` members.

Besides the base classes you subclass, the `algobowl.lib.problem`
module also provides you with many other convenient helpers.  By
convention, this module is typically imported under the name
`problemlib`.

You can copy-paste this into your `problem.py` to start out:

```python
import dataclasses

import algobowl.lib.problem as problemlib


@dataclasses.dataclass
class Input(problemlib.BaseInput):
    ...


@dataclasses.dataclass
class Output(problemlib.BaseOutput):
    ...
```

## Implementing the `Input` class

The `Input` class should provide a `classmethod` named `read`, which takes a
file-like object and returns an `Input`.

```python
def read(cls, f):
    ...
    return cls(...)
```

If the input does not conform to the specifications, `read` should raise a
`problemlib.FileFormatError`.  Make sure to use a good exception message.
This is what students will see when they get an error during upload.

While you could do all the input parsing yourself, `problemlib` provides a
number of helpers that will make this easier.  Most of these helpers
take a list of lines as input, so it's advised to do a `lines = f.readlines()`
at the top of your function.

The typical pattern is:

```python
# Read lines into an array.
lines = f.readlines()

# Assert the input has a valid number of lines.  Below, we say we need at least
# 3 lines, and no more than 20 lines.
problemlib.assert_linecount(lines, range(3, 21))

# Read an integer from the first line.
n = problemlib.parse_line_int(lines, 0, bounds=range(0, 101))

# Read n integers from the second line.
list_of_ints = problemlib.parse_line_ints(lines, 1, count=n, bounds=range(0, n))

...

return cls(n=n, list_of_ints=list_of_ints, ...)
```

The above code doesn't make much sense, but hopefully it provides for a source
of inspiration.  You can also read other problems for further inspiration.

The `Input` class should also provide a method named `write`, which prints a
normalized input to a file.

```python
def write(self, f):
    print(..., file=f)
```

For example:

```python
def write(self, f):
    print(self.n, file=f)
    print(*self.list_of_ints, file=f)
```

The `Input` class should also provide a `generate` method to generate a random
input.  This will be used to create default inputs for each group should they
fail to upload an input.

The `generate` method takes a pre-seeded
[`random.Random`](https://docs.python.org/3/library/random.html#random.Random)
object to generate random numbers.  *You should not use random numbers except
from this object.*  The tests use a fixed-set of seeds so they are reproducible.

For example:

```python
@classmethod
def generate(cls, rng):
    return cls(list_of_ints=[rng.randint(0, 100) for _ in range(20)], ...)
```

## Writing example inputs

Now that you've written the `Input` class, it's time to write example inputs.

You should write two kinds of inputs:

* `test_data/inputs/good/*.in`, with examples of good inputs.
* `test_data/inputs/bad/*.in`, with examples of inputs that should cause errors
  during upload.

Typically, the example input from the problem statement should be put
in `test_data/inputs/good/example.in`.  You should write more inputs as well
(for example, inputs which are at the bounds of the problem).

Once you've written some example inputs, you can run the problem tester and to
test them on your `Input` class:

```shellsession
$ algobowl problem . test
```

## Implementing the `Output` class

The output class should provide a `classmethod` called `read`, which takes an
`Input` and a file-like object and produces an `Output`:

```python
@classmethod
def read(cls, input, f):
    ...
    return cls(input=input, score=score, ...)
```

Make good use of the helpers in `problemlib` to help you with the parsing here,
similar to what you did in the `Input` class.

Your `read` method should raise a `problemlib.FileFormatError` if there's an
error in the file format.  **Note:** the `read` method is not the right place to
point out verification errors.  Simply parse the input and create your object,
even if there's verification issues.

**Note:** the `score` attribute should be the score the student reported in the
output, not the actual score of the output.

Similar to the `Input` class, you should also implement a `write` method:

```python
def write(self, f):
    print(..., file=f)
```

Finally, you need to implement a verification method.  This is named
`compute_actual_score`, and it should return the actual score of the output
(which may not be what the `score` attribute is).  If the `score` attribute
differs from what your method returns, this will result in a verification issue.

Your `compute_actual_score` method may also raise a
`problemlib.VerificationError` if there's a verification issue that's not the
score differing from the reported value.  As with file format errors, your
exception message should be descriptive, however, it will not be seen by
students.  The message will be logged in the backend for the instructor's
viewing purposes.

For example:

```python
def compute_actual_score(self):
    ...
    return score
```

There's one more `staticmethod` you may optionally implement (and is only
required by some quite special problems), `repr_score`.  The default is:

```python
@staticmethod
def repr_score(score):
    return str(score)
```

If the score is non-integer, you'll want to implement this method.  Internally,
the `score` attribute, as well as what you return from `compute_actual_score`
should be an integer.  However, if you want the score to show differently in the
leaderboard, you can implement this.  For example, to show as a decimal number
with two digits:

```python
@staticmethod
def repr_score(score):
    whole_part, decimal_part = divmod(score, 100)
    return f"{whole_part}.{decimal_part:>02}"
```

## Writing example outputs

Now that you've implemented the `Output` class, you're nearly done.
It's time to make test data.

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

## Test Coverage

Ideally, you want to bring your module to 100% test coverage, as then you know
that each edge case students may hit is tested.  Keep adding example inputs and
outputs until you've reached 100% test coverage.

## Optional: Implement a trivial solver

While it's not required, it's highly recommended to implement a trivial solver
for the problem.  This solver will be used by tests to provide a little fuzz
coverage when coupled with `Input.generate()`.

You should implement the absolute most trivial solution for the problem
possible.  Think: *how can I make the answer as bad as possible?*

The method is called `trivial_solve` on your `Input` class, and returns
an `Output` object.

For example:

```python
def trivial_solve(self):
    return Output(...)
```

## Uploading for review

Create a new branch and commit your changes:

```shellsession
$ git checkout -b problem_id
$ git add .
$ git commit -m "Add new problem problem_id"
$ git push -u origin problem_id
```

Then, open a pull request in the GitHub UI.

When changes are requested, please amend/rebase your commits instead of creating
"fixup commits".  You'll need to use `--force` when updating your PR for review.

## Reference: problemlib helpers

Here's what `problemlib` provides to you to help you with parsing:

### `check_bound`

```
check_bound(lineno, bound, value)
```

Assert a value is within certain bounds.

Arguments:

* `lineno`: The line number (zero indexed) the value was found on.
* `bound`: May be an integer, a callable, or a container (e.g., list).  If an
  integer, this will assert that `value` is exactly equal to `bound`.  If a
  callable, this will assert `bound(value)` returns true.  If a container, this
  will assert `value in bound`.
* `value` is the integer value to check.

### `assert_linecount`

```
assert_linecount(lines, bounds)
```

This takes a list of all lines in the file, and asserts the number of lines in
the file is within certain bounds.

Arguments:

* `lines`: The list of lines in the file.  Note: this will be modified to remove
  empty lines at the end of the file if the list of lines is not within the
  bounds.
* `bounds`: See the documentation for `check_bound`.

### `parse_int`

```
parse_int(lineno, value, bound=None)
```

Parse an integer value and return it.  **Note:** normally you do not need call
this function directly.  Instead, you should probably use `parse_line_int` or
`parse_line_ints`.

Arguments:

* `lineno`: The zero-indexed line number the integer was found on.
* `value`: The string to convert to an integer.
* `bound`: An optional bound, see `check_bound`.

### `parse_line_ints`

```
parse_line_ints(lines, lineno, bounds=None, count=None)
```

Parse a certain line from a file, asserting it contains space-separated
integers.  Return the parsed list of integers.

Note: when `count` is an integer, and `bounds` is a list of length `count`, each
bound in `bounds` will be used for the corresponding element on the line.

Arguments:

* `lines`: The list of all lines in the file.
* `lineno`: The zero-indexed line number to parse.
* `bounds`: An optional bound for all integers, see `check_bound`.
* `count`: The expected number of integers on the line (this is also a `bound`
   parsed by `check_bound`).

## `parse_line_int`

```
parse_line_int(lines, lineno, bounds=None)
```

Convenience version of `parse_line_ints` with `count=1`, and returns an integer
instead of a list.

Arguments:

* `lines`: The list of all lines in the file.
* `lineno`: The zero-indexed line number to parse.
* `bounds`: An optional bound for the integer, see `check_bound`.
