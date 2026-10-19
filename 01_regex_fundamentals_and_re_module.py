"""
================================================================================
Day 24: Python Regular Expressions (re) - Fundamentals & The re Module
================================================================================
Regular Expressions (commonly known as RegEx or RegExp) are specialized sequences
of characters that define a formal search pattern. They are a universal language
for pattern matching, data extraction, validation, and string manipulation.

Theoretical Background:
Regular expressions originate from formal language theory and theoretical computer
science (introduced by American mathematician Stephen Cole Kleene in the 1950s).
Modern regex engines typically implement either:
  1. DFA (Deterministic Finite Automaton): Linear time guarantees, no backtracking.
  2. NFA (Nondeterministic Finite Automaton): Uses backtracking, supporting advanced
     features like backreferences, lookarounds, and lazy matching.
Python's standard `re` module employs an advanced NFA engine written in C.

Key Topics Covered in this Script:
1. The Mental Model of Regular Expressions & Pattern Engines
2. The Raw String (`r"..."`) Crux: Escaping & The Leaning Toothpick Syndrome
3. The Big Three Matching Functions: `re.search()`, `re.match()`, `re.fullmatch()`
4. Extraction Functions: `re.findall()` vs. `re.finditer()` (Streaming & Memory)
5. Transformation & Tokenization: `re.split()`, `re.sub()`, and `re.subn()`
6. Pre-compilation with `re.compile()`: Engine Internals, Caching & Performance
7. The Anatomy of the `re.Match` Object: Spans, Indices & Safe Access
8. Production Demonstration: High-Throughput HTTP Access Log Line Parser
================================================================================
"""

import re
import time
from typing import Optional, List, Dict, Any


def print_separator(title: str) -> None:
    """Utility helper to print structured visual headers for each demonstration."""
    print("\n" + "=" * 78)
    print(f" {title}")
    print("=" * 78)


# ==============================================================================
# 1. THE MENTAL MODEL & RAW STRINGS (r"...")
# ==============================================================================
# Why do we always use raw strings (prefix 'r') when writing Regular Expressions?
#
# Python strings interpret escape sequences like \n (newline), \t (tab), \b (backspace).
# Regex engines ALSO interpret escape sequences like \d (digit), \w (word), \b (word boundary).
#
# If you don't use raw strings:
# - Python's string parser parses the backslash FIRST before the regex engine sees it.
# - To pass a literal backslash `\` to regex, you'd need `\\\\` in a regular Python string!
#   (2 backslashes for Python string -> 1 backslash to regex -> escaped literal backslash).
# - `\b` in standard Python string is ASCII Backspace (chr(8)), NOT a regex word boundary!
#
# Using raw strings `r"..."` disables Python string-level escape processing, passing
# backslashes directly and untouched into the regex engine.

print_separator("1. The Raw String Crux: Python Escape vs. Regex Escape")

raw_pattern = r"\bword\b"
normal_pattern = "\\bword\\b"  # Notice the cumbersome double backslashes needed!

test_text = "A single word in a sentence."
print(f"Testing raw string pattern: {raw_pattern}")
match_raw = re.search(raw_pattern, test_text)
print(f"Raw pattern match found: {match_raw.group() if match_raw else 'No match'}")

# Danger of forgetting 'r' with \b:
buggy_pattern = "\bword\b"  # Python replaces \b with ASCII 8 (backspace)
match_buggy = re.search(buggy_pattern, test_text)
print(f"Non-raw pattern with \\b result: {match_buggy} (Failed because '\\b' was backspace!)")


# ==============================================================================
# 2. THE BIG THREE: re.search() vs re.match() vs re.fullmatch()
# ==============================================================================
# Beginners frequently confuse these three functions:
# 1. re.search(pattern, string):
#    Scans THROUGHOUT the entire string, returning the FIRST location where pattern matches.
# 2. re.match(pattern, string):
#    Matches ONLY at the exact beginning (index 0) of the string.
#    (Equivalent to re.search(r"^pattern", string) in single-line mode).
# 3. re.fullmatch(pattern, string):
#    Matches ONLY if the ENTIRE string matches the pattern from start to finish.
#    (Equivalent to re.search(r"^pattern$", string)).

print_separator("2. re.search() vs. re.match() vs. re.fullmatch()")

sample_data = "Order-ID #94821 confirmed on 2026-10-19"

# 1. Searching anywhere in text:
search_res = re.search(r"\d{5}", sample_data)
print(f"re.search(r'\\d{{5}}'): Found -> {search_res.group() if search_res else None}")

# 2. Matching at the beginning:
match_res_order = re.match(r"Order-ID", sample_data)
match_res_digits = re.match(r"\d{5}", sample_data)  # Digits are not at index 0!
print(f"re.match(r'Order-ID'): Found -> {match_res_order.group() if match_res_order else None}")
print(f"re.match(r'\\d{{5}}'): Found -> {match_res_digits} (None because digits aren't at start)")

# 3. Matching the whole string:
exact_target = "USER_48291"
full_res_ok = re.fullmatch(r"USER_\d+", exact_target)
full_res_fail = re.fullmatch(r"USER_\d+", "USER_48291 extra trailing characters")
print(f"re.fullmatch('USER_\\d+', '{exact_target}'): -> {full_res_ok.group() if full_res_ok else None}")
print(f"re.fullmatch with trailing chars: -> {full_res_fail} (Must match 100% of the input)")


# ==============================================================================
# 3. EXTRACTION: re.findall() vs. re.finditer()
# ==============================================================================
# When you need all occurrences in a corpus:
# - re.findall():
#   Returns a Python list of all matching substrings.
#   CAUTION: If the pattern contains capturing groups `()`, findall returns tuples
#   of groups rather than full matches!
#   MEMORY CAUTION: Eagerly creates the entire list in RAM.
# - re.finditer():
#   Returns an iterator yielding `Match` objects lazily.
#   Extremely memory-efficient for multi-gigabyte log files and streams.
#   Provides match indices (.start(), .end(), .span()) which findall discards.

print_separator("3. Extraction: re.findall() vs. re.finditer()")

corpus = "Sensors: SENSOR-A12 at 42.5C, SENSOR-B99 at 68.1C, SENSOR-C04 at 55.0C."

# Using findall (Eager list of matches):
sensor_ids = re.findall(r"SENSOR-[A-Z]\d{2}", corpus)
print(f"re.findall list of sensor IDs: {sensor_ids}")

# Warning about groups in findall:
# If you use capturing groups, findall returns only the grouped contents!
grouped_findall = re.findall(r"(SENSOR-[A-Z]\d{2})\s+at\s+(\d+\.\d+)C", corpus)
print(f"re.findall with groups returns list of tuples: {grouped_findall}")

# Using finditer (Lazy Match objects with metadata):
print("\nIterating with re.finditer() [Memory-Efficient Stream]:")
for match in re.finditer(r"(SENSOR-[A-Z]\d{2})\s+at\s+(\d+\.\d+)C", corpus):
    full_text = match.group(0)
    sensor = match.group(1)
    temp = float(match.group(2))
    start_pos, end_pos = match.span()
    print(f" - Found '{sensor}' reading {temp}C at position [{start_pos}:{end_pos}]")


# ==============================================================================
# 4. TOKENIZATION & SUBSTITUTION: re.split(), re.sub(), re.subn()
# ==============================================================================
# String manipulation tools:
# - re.split(pattern, string, maxsplit=0):
#   Splits text using regex separators (e.g., splitting on commas, semicolons, whitespace).
#   NOTE: If pattern uses capturing parentheses `(...)`, the delimiters are retained!
# - re.sub(pattern, repl, string, count=0):
#   Replaces matched patterns. `repl` can be a string or a Python callable function!
# - re.subn(pattern, repl, string, count=0):
#   Performs substitution and returns a tuple: `(new_string, number_of_substitutions_made)`.

print_separator("4. Tokenization & Substitution: re.split(), re.sub(), re.subn()")

# 1. Advanced Splitting:
delimited_text = "Apple, Banana; Orange | Mango   Pineapple"
tokens = re.split(r"[,;|\s]+", delimited_text)
print(f"Splitting on variable punctuation/whitespace: {tokens}")

# Retaining delimiters using capturing group in re.split():
math_expr = "15 + 24 - 8 * 3"
split_with_delimiters = re.split(r"\s*([+\-*])\s*", math_expr)
print(f"Split with delimiter retention: {split_with_delimiters}")

# 2. Basic Substitution with re.sub():
raw_notes = "Contact support at help@company.com or sales@company.com for info."
redacted = re.sub(r"[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}", "[EMAIL REDACTED]", raw_notes)
print(f"Masked text: {redacted}")

# 3. Dynamic Replacement using a Callable Function in re.sub():
# If `repl` is a function, Python passes the `Match` object to it for dynamic evaluation!
temperatures_f = "Today: 77F in Miami, 50F in New York, and 104F in Phoenix."

def fahrenheit_to_celsius(match: re.Match) -> str:
    f_val = int(match.group(1))
    c_val = round((f_val - 32) * 5 / 9, 1)
    return f"{c_val}C ({f_val}F)"

converted_report = re.sub(r"(\d+)F", fahrenheit_to_celsius, temperatures_f)
print(f"Dynamic conversion using sub callable:\n -> {converted_report}")

# 4. re.subn() - Counting replacements:
code_snippet = "var x = 10; var y = 20; var total = x + y;"
modernized, replacement_count = re.subn(r"\bvar\b", "let", code_snippet)
print(f"re.subn() result: {modernized}")
print(f"Total occurrences replaced: {replacement_count}")


# ==============================================================================
# 5. PRE-COMPILATION WITH re.compile() & BENCHMARKING
# ==============================================================================
# When should you use re.compile()?
#
# Python internally caches compiled regex patterns (in `re._cache`, typically up
# to 512 entries). So for one-off calls, `re.search(pat, s)` is virtually as fast
# as pre-compiling.
#
# HOWEVER, explicit pre-compilation with `re.compile()` is standard industry best practice:
# 1. Readability: Declares the pattern cleanly at module or class level.
# 2. Maintenance: Modifying a pattern requires updating a single variable.
# 3. Guaranteed zero cache-miss overhead in tight computational loops.
# 4. Enables pattern reuse across multiple methods with flags pre-configured.

print_separator("5. Pre-compilation with re.compile() & Microbenchmark")

compiled_uuid_pattern = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE
)

test_uuid = "123e4567-e89b-12d3-a456-426614174000"
is_valid_uuid = bool(compiled_uuid_pattern.fullmatch(test_uuid))
print(f"UUID '{test_uuid}' valid: {is_valid_uuid}")

# Microbenchmark: 100,000 iterations comparing re.search() string vs compiled pattern
iterations = 100_000
test_str = "Status: 200 OK | Latency: 42ms"

# Loop with string-based re.search:
t0 = time.perf_counter()
for _ in range(iterations):
    _ = re.search(r"Latency:\s+(\d+)ms", test_str)
time_uncompiled = time.perf_counter() - t0

# Loop with pre-compiled pattern:
compiled_latency = re.compile(r"Latency:\s+(\d+)ms")
t1 = time.perf_counter()
for _ in range(iterations):
    _ = compiled_latency.search(test_str)
time_compiled = time.perf_counter() - t1

print(f"Performance for {iterations:,} iterations:")
print(f" - Uncompiled re.search() : {time_uncompiled:.4f}s (relies on internal cache)")
print(f" - Pre-compiled .search()  : {time_compiled:.4f}s (direct C pattern pointer)")
print(f" -> Compiled pattern is {(time_uncompiled / time_compiled - 1) * 100:.1f}% faster!")


# ==============================================================================
# 6. ANATOMY OF THE re.Match OBJECT
# ==============================================================================
# When a regex function finds a match, it returns an instance of `re.Match`.
# Understanding all its attributes avoids silent indexing bugs:
#
# - match.group(0) or match.group(): The entire matched substring.
# - match.group(n): The n-th capturing group (1-indexed).
# - match.groups(): A tuple of all capturing groups.
# - match.start([group]): Starting index in the original string.
# - match.end([group]): Ending index in the original string.
# - match.span([group]): Tuple of (start, end) indices.
# - match.string: The original string passed to the regex engine.
# - match.re: The compiled regex pattern object used.

print_separator("6. Anatomy of the re.Match Object")

transaction_text = "TXN_20261019_9872: Transfer $1,450.00 to ACCT_88192"
txn_pattern = re.compile(r"TXN_(\d{8})_(\d+):\s+Transfer\s+\$([\d,]+\.\d{2})\s+to\s+ACCT_(\d+)")

match_obj: Optional[re.Match] = txn_pattern.search(transaction_text)

if match_obj:
    print(f"Full Match (group 0) : '{match_obj.group(0)}'")
    print(f"Date Group (group 1) : '{match_obj.group(1)}'")
    print(f"ID Group (group 2)   : '{match_obj.group(2)}'")
    print(f"Amount (group 3)     : '{match_obj.group(3)}'")
    print(f"Target Acct (group 4): '{match_obj.group(4)}'")
    print(f"All Groups tuple     : {match_obj.groups()}")
    print(f"Full Match Span      : {match_obj.span()} -> slice: text[{match_obj.start()}:{match_obj.end()}]")
    print(f"Amount Sub-Span      : {match_obj.span(3)} -> slice: '{transaction_text[slice(*match_obj.span(3))]}'")
    print(f"Original Text        : '{match_obj.string}'")


# ==============================================================================
# 7. PRODUCTION DEMONSTRATION: HIGH-THROUGHPUT HTTP LOG PARSER
# ==============================================================================
# Let's build a robust, production-grade parser for HTTP server access logs.
# Combines compiled patterns, finditer streaming, group unpacking, and validation.

print_separator("7. Production Demonstration: HTTP Access Log Parser")

raw_log_stream = """
192.168.1.105 - - [19/Oct/2026:08:14:22 +0000] "GET /api/v1/users HTTP/1.1" 200 4523 0.045
10.0.0.42 - admin [19/Oct/2026:08:14:23 +0000] "POST /api/v1/auth/login HTTP/1.1" 401 128 0.120
203.0.113.195 - - [19/Oct/2026:08:14:25 +0000] "GET /static/css/main.css HTTP/2.0" 304 0 0.008
198.51.100.88 - - [19/Oct/2026:08:14:29 +0000] "DELETE /api/v1/records/99 HTTP/1.1" 500 892 1.450
"""

class HTTPLogRecord:
    """Represents a structured, validated HTTP server log entry."""
    def __init__(
        self,
        ip: str,
        user: str,
        timestamp: str,
        method: str,
        endpoint: str,
        protocol: str,
        status_code: int,
        bytes_sent: int,
        duration_sec: float
    ) -> None:
        self.ip = ip
        self.user = user if user != "-" else "anonymous"
        self.timestamp = timestamp
        self.method = method
        self.endpoint = endpoint
        self.protocol = protocol
        self.status_code = status_code
        self.bytes_sent = bytes_sent
        self.duration_sec = duration_sec

    def __repr__(self) -> str:
        return (
            f"LogEntry({self.method} {self.endpoint} -> {self.status_code} "
            f"[{self.duration_sec}s] by {self.user}@{self.ip})"
        )


class AccessLogParser:
    """High-performance parser utilizing compiled regex with finditer streaming."""

    # Pre-compile the regex pattern once at class-load time
    LOG_PATTERN = re.compile(
        r"^([0-9a-fA-F.:]+)\s+-\s+(\S+)\s+\[([^\]]+)\]\s+\"([A-Z]+)\s+(\S+)\s+([^\"]+)\"\s+(\d{3})\s+(\d+)\s+([\d.]+)",
        re.MULTILINE
    )

    @classmethod
    def parse_stream(cls, log_text: str) -> List[HTTPLogRecord]:
        records: List[HTTPLogRecord] = []
        for match in cls.LOG_PATTERN.finditer(log_text.strip()):
            record = HTTPLogRecord(
                ip=match.group(1),
                user=match.group(2),
                timestamp=match.group(3),
                method=match.group(4),
                endpoint=match.group(5),
                protocol=match.group(6),
                status_code=int(match.group(7)),
                bytes_sent=int(match.group(8)),
                duration_sec=float(match.group(9))
            )
            records.append(record)
        return records


# Parse and inspect results
parsed_records = AccessLogParser.parse_stream(raw_log_stream)
print(f"Successfully parsed {len(parsed_records)} log records:")
for record in parsed_records:
    status_indicator = "OK" if record.status_code < 400 else "ALERT"
    print(f" [{status_indicator}] {record}")

print("\n" + "=" * 78)
print(" End of Day 24 - Script 01: Fundamentals & The re Module Complete")
print("=" * 78)
