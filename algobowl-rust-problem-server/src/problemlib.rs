//! Helpers for parsing problem files.
//!
//! These match the behavior and error messages of the Python `algops.problemlib`
//! module, so a problem behaves the same regardless of which implementation
//! serves it.

use std::fmt;

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
}

impl Bound {
    fn contains(self, value: i128) -> bool {
        match self {
            Bound::Any => true,
            Bound::Exact(expected) => value == i128::from(expected),
            Bound::Range(start, end) => i128::from(start) <= value && value < i128::from(end),
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

/// Splits file content into lines, like `readlines()` on a Python text stream.
///
/// Newlines are translated the same way as Python's universal newlines mode:
/// `\r\n` and `\r` both become `\n`.  Each line keeps its trailing newline.
///
/// # Errors
///
/// Returns an error if the content is not valid UTF-8.
pub fn read_lines(content: &[u8]) -> Result<Vec<String>, FileFormatError> {
    let text = std::str::from_utf8(content)
        .map_err(|_| FileFormatError("File is not valid UTF-8 text".to_owned()))?;
    let text = text.replace("\r\n", "\n").replace('\r', "\n");
    Ok(text.split_inclusive('\n').map(str::to_owned).collect())
}

/// Checks whether an integer value is inside a bound.
///
/// # Errors
///
/// Returns an error if the value is outside the bound.
fn check_bound(lineno: i64, bound: Bound, value: i128) -> Result<(), FileFormatError> {
    if bound.contains(value) {
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
    lines: &mut Vec<String>,
    bound: impl Into<Bound>,
) -> Result<(), FileFormatError> {
    let bound = bound.into();
    if bound.contains(lines.len() as i128) {
        return Ok(());
    }
    while lines.last().is_some_and(|line| line.trim_end().is_empty()) {
        lines.pop();
        if bound.contains(lines.len() as i128) {
            return Ok(());
        }
    }
    Err(FileFormatError(
        "File has invalid number of lines".to_owned(),
    ))
}

/// Parses an integer the way Python's `int()` does.
///
/// Returns `None` if the value is not an integer, and `Some(Err(_))` with the
/// normalized digits if the value is too large to represent.
fn parse_python_int(value: &str) -> Option<Result<i128, String>> {
    let (negative, digits) = match value.as_bytes().first() {
        Some(b'+') => (false, &value[1..]),
        Some(b'-') => (true, &value[1..]),
        _ => (false, value),
    };
    if digits.is_empty()
        || digits.starts_with('_')
        || digits.ends_with('_')
        || digits.contains("__")
        || !digits.bytes().all(|b| b.is_ascii_digit() || b == b'_')
    {
        return None;
    }
    let digits: String = digits.chars().filter(|&c| c != '_').collect();
    let sign = if negative { "-" } else { "" };
    Some(match digits.parse::<i128>() {
        Ok(parsed) => Ok(if negative { -parsed } else { parsed }),
        Err(_) => Err(format!("{sign}{}", digits.trim_start_matches('0'))),
    })
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
    let out_of_bounds = |value: &dyn fmt::Display| {
        FileFormatError(format!(
            "Line #{}: Value {value} out of expected bounds",
            lineno + 1
        ))
    };
    match parse_python_int(value) {
        None => Err(FileFormatError(format!(
            "Line #{}: Unable to interpret {} as integer",
            lineno + 1,
            python_repr(value)
        ))),
        Some(Err(digits)) => Err(out_of_bounds(&digits)),
        Some(Ok(parsed)) => {
            check_bound(lineno as i64, bound.into(), parsed)?;
            i64::try_from(parsed).map_err(|_| out_of_bounds(&parsed))
        }
    }
}

/// Parses whitespace-separated integers from a line.
///
/// # Errors
///
/// Returns an error if the line is missing, has the wrong number of values,
/// or has an invalid value.
pub fn parse_line_ints(
    lines: &[String],
    lineno: usize,
    bound: impl Into<Bound>,
    count: impl Into<Bound>,
) -> Result<Vec<i64>, FileFormatError> {
    let bound = bound.into();
    let line = lines
        .get(lineno)
        .ok_or_else(|| FileFormatError(format!("Line #{}: Missing line", lineno + 1)))?;
    let values: Vec<&str> = line.split_whitespace().collect();
    if !count.into().contains(values.len() as i128) {
        return Err(FileFormatError(format!(
            "Line #{}: Number of values ({}) is out of expected bounds",
            lineno + 1,
            values.len()
        )));
    }
    values
        .into_iter()
        .map(|value| parse_int(lineno, value, bound))
        .collect()
}

/// Parses one integer from a line.
///
/// # Errors
///
/// Returns an error if the line does not contain exactly one valid integer.
pub fn parse_line_int(
    lines: &[String],
    lineno: usize,
    bound: impl Into<Bound>,
) -> Result<i64, FileFormatError> {
    Ok(parse_line_ints(lines, lineno, bound, 1)?[0])
}

/// Formats a string the way Python's `repr()` does, for error messages.
pub fn python_repr(value: &str) -> String {
    let quote = if value.contains('\'') && !value.contains('"') {
        '"'
    } else {
        '\''
    };
    let mut repr = String::from(quote);
    for c in value.chars() {
        match c {
            '\\' => repr.push_str("\\\\"),
            '\t' => repr.push_str("\\t"),
            '\n' => repr.push_str("\\n"),
            '\r' => repr.push_str("\\r"),
            c if c == quote => {
                repr.push('\\');
                repr.push(c);
            }
            c if is_printable(c) => repr.push(c),
            c if u32::from(c) < 0x100 => repr.push_str(&format!("\\x{:02x}", u32::from(c))),
            c if u32::from(c) < 0x10000 => repr.push_str(&format!("\\u{:04x}", u32::from(c))),
            c => repr.push_str(&format!("\\U{:08x}", u32::from(c))),
        }
    }
    repr.push(quote);
    repr
}

/// Approximates Python's `str.isprintable()` for a single character.
fn is_printable(c: char) -> bool {
    if c == ' ' {
        return true;
    }
    !(c.is_control()
        || c.is_whitespace()
        || matches!(
            c,
            '\u{ad}' | '\u{200b}'..='\u{200f}' | '\u{202a}'..='\u{202e}' | '\u{2060}'..='\u{2064}' | '\u{feff}'
        ))
}

/// A deterministic pseudo-random number generator (SplitMix64).
pub struct Rng(u64);

impl Rng {
    /// Creates a generator from a seed.
    pub fn new(seed: u64) -> Self {
        Rng(seed)
    }

    /// Returns the next pseudo-random 64-bit value.
    pub fn next_u64(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9e37_79b9_7f4a_7c15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xbf58_476d_1ce4_e5b9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94d0_49bb_1331_11eb);
        z ^ (z >> 31)
    }

    /// Returns a uniformly distributed integer in `[0, n)`.
    ///
    /// # Panics
    ///
    /// Panics if `n` is zero.
    pub fn below(&mut self, n: u64) -> u64 {
        assert!(n > 0, "n must be positive");
        // Reject values in the final partial block to avoid modulo bias.
        let limit = u64::MAX - u64::MAX % n;
        loop {
            let value = self.next_u64();
            if value < limit {
                return value % n;
            }
        }
    }

    /// Returns a uniformly chosen element of a non-empty slice.
    ///
    /// # Panics
    ///
    /// Panics if `items` is empty.
    pub fn choice<'a, T>(&mut self, items: &'a [T]) -> &'a T {
        &items[self.below(items.len() as u64) as usize]
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn lines(text: &str) -> Vec<String> {
        read_lines(text.as_bytes()).unwrap()
    }

    #[test]
    fn read_lines_translates_newlines() {
        assert_eq!(lines("a\r\nb\rc\n"), ["a\n", "b\n", "c\n"]);
        assert_eq!(lines("a\nb"), ["a\n", "b"]);
        assert!(lines("").is_empty());
    }

    #[test]
    fn read_lines_rejects_invalid_utf8() {
        assert_eq!(
            read_lines(b"\xff"),
            Err(FileFormatError("File is not valid UTF-8 text".to_owned()))
        );
    }

    #[test]
    fn assert_linecount_drops_trailing_blank_lines() {
        let mut file = lines("1\n2\n\n  \n");
        assert_linecount(&mut file, 2).unwrap();
        assert_eq!(file, ["1\n", "2\n"]);

        let mut file = lines("1\n2\n");
        assert!(assert_linecount(&mut file, 3).is_err());
    }

    #[test]
    fn parse_int_matches_python() {
        assert_eq!(parse_int(0, "+1_000", Bound::Any), Ok(1000));
        assert_eq!(parse_int(0, "-007", Bound::Any), Ok(-7));
        assert_eq!(
            parse_int(2, "1__0", Bound::Any),
            Err(FileFormatError(
                "Line #3: Unable to interpret '1__0' as integer".to_owned()
            ))
        );
        assert_eq!(
            parse_int(0, "5", 1..5),
            Err(FileFormatError(
                "Line #1: Value 5 out of expected bounds".to_owned()
            ))
        );
        assert_eq!(
            parse_int(0, "99999999999999999999999999999999999999999", Bound::Any),
            Err(FileFormatError(
                "Line #1: Value 99999999999999999999999999999999999999999 out of expected bounds"
                    .to_owned()
            ))
        );
    }

    #[test]
    fn parse_line_ints_checks_count() {
        let file = lines("1 2 3\n");
        assert_eq!(parse_line_ints(&file, 0, Bound::Any, 3), Ok(vec![1, 2, 3]));
        assert_eq!(
            parse_line_ints(&file, 0, Bound::Any, 2),
            Err(FileFormatError(
                "Line #1: Number of values (3) is out of expected bounds".to_owned()
            ))
        );
    }

    #[test]
    fn python_repr_matches_python() {
        assert_eq!(python_repr("a"), "'a'");
        assert_eq!(python_repr("'"), "\"'\"");
        assert_eq!(python_repr("\t\u{7f}é"), "'\\t\\x7fé'");
    }

    #[test]
    fn rng_is_deterministic() {
        let mut a = Rng::new(42);
        let mut b = Rng::new(42);
        for _ in 0..100 {
            assert_eq!(a.below(7), b.below(7));
        }
    }
}
