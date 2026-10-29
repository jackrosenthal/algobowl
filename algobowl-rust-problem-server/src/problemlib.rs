//! Helpers for parsing problem files.

use std::borrow::Cow;
use std::fmt;
use std::num::IntErrorKind;

/// An input or output file is malformed.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct FileFormatError(pub String);

impl fmt::Display for FileFormatError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.0)
    }
}

impl std::error::Error for FileFormatError {}

/// An output file is well-formed, but is not a valid solution.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct VerificationError(pub String);

impl fmt::Display for VerificationError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.0)
    }
}

impl std::error::Error for VerificationError {}

/// The allowed values for a parsed integer or a line count.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Bound {
    /// Any value is allowed.
    Any,
    /// Only this value is allowed.
    Exact(i64),
    /// Values in the half-open range `[start, end)` are allowed.
    Range(i64, i64),
    /// Values in the half-open range `[start, end)` are allowed, except for
    /// the third value.
    RangeExcluding(i64, i64, i64),
}

impl Bound {
    fn contains(self, value: i64) -> bool {
        match self {
            Bound::Any => true,
            Bound::Exact(expected) => value == expected,
            Bound::Range(start, end) => (start..end).contains(&value),
            Bound::RangeExcluding(start, end, excluded) => {
                (start..end).contains(&value) && value != excluded
            }
        }
    }
}

impl From<i64> for Bound {
    fn from(value: i64) -> Self {
        Bound::Exact(value)
    }
}

impl From<std::ops::Range<i64>> for Bound {
    fn from(range: std::ops::Range<i64>) -> Self {
        Bound::Range(range.start, range.end)
    }
}

/// Decodes file content as text.
///
/// Old Mac (`\r`) line endings are translated to `\n`, so that
/// [`str::lines`] splits them.  The content is only copied if it contains a
/// `\r`.
///
/// # Errors
///
/// Returns an error if the content is not valid UTF-8.
pub fn decode_text(content: &[u8]) -> Result<Cow<'_, str>, FileFormatError> {
    let text = std::str::from_utf8(content)
        .map_err(|_| FileFormatError("File is not valid UTF-8 text".to_owned()))?;
    if text.contains('\r') {
        Ok(Cow::Owned(text.replace("\r\n", "\n").replace('\r', "\n")))
    } else {
        Ok(Cow::Borrowed(text))
    }
}

/// Checks whether an integer value is inside a bound.
///
/// `lineno` is the zero-based line number of the value, for the error
/// message.
///
/// # Errors
///
/// Returns an error if the value is outside the bound.
pub fn check_bound(
    lineno: usize,
    bound: impl Into<Bound>,
    value: i64,
) -> Result<(), FileFormatError> {
    if bound.into().contains(value) {
        return Ok(());
    }
    Err(FileFormatError(format!(
        "Line #{}: Value {value} out of expected bounds",
        lineno + 1
    )))
}

/// Checks the number of lines in a file.
///
/// If the line count is out of bounds, trailing blank lines are removed one at
/// a time until it is in bounds.
///
/// # Errors
///
/// Returns an error if the file has an invalid number of lines.
pub fn assert_linecount(
    lines: &mut Vec<&str>,
    bound: impl Into<Bound>,
) -> Result<(), FileFormatError> {
    let bound = bound.into();
    let in_bounds = |lines: &Vec<&str>| i64::try_from(lines.len()).is_ok_and(|n| bound.contains(n));
    if in_bounds(lines) {
        return Ok(());
    }
    while lines.last().is_some_and(|line| line.trim().is_empty()) {
        lines.pop();
        if in_bounds(lines) {
            return Ok(());
        }
    }
    Err(FileFormatError(
        "File has invalid number of lines".to_owned(),
    ))
}

/// Parses an integer and checks its bounds.
///
/// # Errors
///
/// Returns an error if the value cannot be parsed or is out of bounds.
pub fn parse_int(
    lineno: usize,
    value: &str,
    bound: impl Into<Bound>,
) -> Result<i64, FileFormatError> {
    match value.parse() {
        Ok(parsed) => {
            check_bound(lineno, bound, parsed)?;
            Ok(parsed)
        }
        Err(e)
            if matches!(
                e.kind(),
                IntErrorKind::PosOverflow | IntErrorKind::NegOverflow
            ) =>
        {
            Err(FileFormatError(format!(
                "Line #{}: Value {value} out of expected bounds",
                lineno + 1
            )))
        }
        Err(_) => Err(FileFormatError(format!(
            "Line #{}: Unable to interpret {value:?} as integer",
            lineno + 1
        ))),
    }
}

fn get_line<'a>(lines: &[&'a str], lineno: usize) -> Result<&'a str, FileFormatError> {
    lines
        .get(lineno)
        .copied()
        .ok_or_else(|| FileFormatError(format!("Line #{}: Missing line", lineno + 1)))
}

/// Checks the number of whitespace-separated values on a line.
fn check_value_count(lineno: usize, line: &str, count: Bound) -> Result<(), FileFormatError> {
    let num_values = line.split_whitespace().count();
    if i64::try_from(num_values).is_ok_and(|n| count.contains(n)) {
        return Ok(());
    }
    Err(FileFormatError(format!(
        "Line #{}: Number of values ({num_values}) is out of expected bounds",
        lineno + 1,
    )))
}

/// Parses whitespace-separated integers from a line.
///
/// # Errors
///
/// Returns an error if the line is missing, has the wrong number of values,
/// or has an invalid value.
pub fn parse_line_ints(
    lines: &[&str],
    lineno: usize,
    bound: impl Into<Bound>,
    count: impl Into<Bound>,
) -> Result<Vec<i64>, FileFormatError> {
    let bound = bound.into();
    let line = get_line(lines, lineno)?;
    check_value_count(lineno, line, count.into())?;
    line.split_whitespace()
        .map(|value| parse_int(lineno, value, bound))
        .collect()
}

/// Parses exactly `N` whitespace-separated integers from a line.
///
/// This is equivalent to [`parse_line_ints`] with a count of `N`, but does not
/// allocate, for parsing large files.
///
/// # Errors
///
/// Returns an error if the line is missing, has the wrong number of values,
/// or has an invalid value.
pub fn parse_line_ints_array<const N: usize>(
    lines: &[&str],
    lineno: usize,
    bound: impl Into<Bound>,
) -> Result<[i64; N], FileFormatError> {
    parse_line_ints_each(lines, lineno, [bound.into(); N])
}

/// Parses exactly `N` whitespace-separated integers from a line, each with
/// its own bound.
///
/// This does not allocate, for parsing large files.
///
/// # Errors
///
/// Returns an error if the line is missing, has the wrong number of values,
/// or has an invalid value.
pub fn parse_line_ints_each<const N: usize>(
    lines: &[&str],
    lineno: usize,
    bounds: [Bound; N],
) -> Result<[i64; N], FileFormatError> {
    let line = get_line(lines, lineno)?;
    let mut values = [0; N];

    // Parse in a single pass, which is all that valid lines need.
    let mut tokens = line.split_whitespace();
    let valid = values.iter_mut().zip(bounds).all(|(value, bound)| {
        let parsed = tokens.next().and_then(|token| token.parse().ok());
        parsed
            .filter(|&parsed| bound.contains(parsed))
            .map(|parsed| *value = parsed)
            .is_some()
    });
    if valid && tokens.next().is_none() {
        return Ok(values);
    }

    // Report the error, checking the count before the values.
    check_value_count(lineno, line, Bound::Exact(N as i64))?;
    for (value, (token, bound)) in values.iter_mut().zip(line.split_whitespace().zip(bounds)) {
        *value = parse_int(lineno, token, bound)?;
    }
    Ok(values)
}

/// Parses one integer from a line.
///
/// # Errors
///
/// Returns an error if the line does not contain exactly one valid integer.
pub fn parse_line_int(
    lines: &[&str],
    lineno: usize,
    bound: impl Into<Bound>,
) -> Result<i64, FileFormatError> {
    let [value] = parse_line_ints_array(lines, lineno, bound)?;
    Ok(value)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn error(message: &str) -> FileFormatError {
        FileFormatError(message.to_owned())
    }

    #[test]
    fn decode_text_translates_old_mac_newlines() {
        let text = decode_text(b"a\r\nb\rc\n").unwrap();
        assert_eq!(text.lines().collect::<Vec<_>>(), ["a", "b", "c"]);
        assert!(matches!(decode_text(b"a\nb").unwrap(), Cow::Borrowed(_)));
    }

    #[test]
    fn decode_text_rejects_invalid_utf8() {
        assert_eq!(
            decode_text(b"\xff"),
            Err(error("File is not valid UTF-8 text"))
        );
    }

    #[test]
    fn assert_linecount_drops_trailing_blank_lines() {
        let mut file: Vec<&str> = "1\n2\n\n  \n".lines().collect();
        assert_linecount(&mut file, 2).unwrap();
        assert_eq!(file, ["1", "2"]);

        let mut file: Vec<&str> = "1\n2\n".lines().collect();
        assert!(assert_linecount(&mut file, 3).is_err());
    }

    #[test]
    fn parse_int_errors() {
        assert_eq!(parse_int(0, "+1000", Bound::Any), Ok(1000));
        assert_eq!(
            parse_int(2, "1_000", Bound::Any),
            Err(error("Line #3: Unable to interpret \"1_000\" as integer"))
        );
        assert_eq!(
            parse_int(0, "5", 1..5),
            Err(error("Line #1: Value 5 out of expected bounds"))
        );
        assert_eq!(
            parse_int(0, "99999999999999999999", Bound::Any),
            Err(error(
                "Line #1: Value 99999999999999999999 out of expected bounds"
            ))
        );
    }

    #[test]
    fn parse_line_ints_checks_count_before_values() {
        let file: Vec<&str> = "1 2 3\n1 x\n".lines().collect();
        assert_eq!(parse_line_ints(&file, 0, Bound::Any, 3), Ok(vec![1, 2, 3]));
        assert_eq!(
            parse_line_ints(&file, 0, Bound::Any, 2),
            Err(error(
                "Line #1: Number of values (3) is out of expected bounds"
            ))
        );
        assert_eq!(
            parse_line_ints_array::<3>(&file, 1, Bound::Any),
            Err(error(
                "Line #2: Number of values (2) is out of expected bounds"
            ))
        );
    }

    #[test]
    fn parse_line_ints_each_checks_each_bound_in_order() {
        let bounds = [Bound::Range(1, 9), Bound::Range(2, 5), Bound::Any];
        let file: Vec<&str> = "1 4 100\n9 x 1\n".lines().collect();
        assert_eq!(parse_line_ints_each(&file, 0, bounds), Ok([1, 4, 100]));
        assert_eq!(
            parse_line_ints_each(&file, 1, bounds),
            Err(error("Line #2: Value 9 out of expected bounds"))
        );
    }

    #[test]
    fn range_excluding_bound() {
        let bound = Bound::RangeExcluding(-3, 4, 0);
        assert!(bound.contains(-3) && bound.contains(3));
        assert!(!bound.contains(0) && !bound.contains(4));
    }
}
