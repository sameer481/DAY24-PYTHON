"""
================================================================================
Day 24: Python Regular Expressions (re) - Flags, Performance & Pitfalls
================================================================================
While simple regex works out-of-the-box, enterprise systems demand patterns that
are readable, maintainable, resilient against algorithmic denial-of-service,
and configured with appropriate engine flags.

Key Topics Covered in this Script:
1. Compilation Flags in Depth: IGNORECASE, MULTILINE, DOTALL, VERBOSE, ASCII
2. Combining Flags via Bitwise OR (`|`) & Embedded Inline Flags (`(?imsx)`)
3. The Elegance of `re.VERBOSE` (`re.X`): Readable, Self-Documenting Regex
4. Critical Antipatterns: When NOT to Use Regex (Built-in String Superiority)
5. The Unescaped Dot (`.`) & Boundary Trap
6. Catastrophic Backtracking & ReDoS (Regular Expression Denial of Service)
7. Production Demonstration: Multi-Format Timestamp Normalizer with re.VERBOSE
================================================================================
"""

import re
import sys
import time
from typing import List, Dict, Tuple

# Ensure UTF-8 output across all operating systems
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def print_separator(title: str) -> None:
    """Utility helper to print structured visual headers for each demonstration."""
    print("\n" + "=" * 78)
    print(f" {title}")
    print("=" * 78)


# ==============================================================================
# 1. REGEX COMPILATION FLAGS IN DEPTH
# ==============================================================================
# Python provides flags to alter the regex engine's core matching rules:
#
# - `re.IGNORECASE` (`re.I`): Case-insensitive matching.
# - `re.MULTILINE`  (`re.M`): `^` matches start of string AND start of each line (`\n`).
#                             `$` matches end of string AND end of each line (`\n`).
# - `re.DOTALL`     (`re.S`): Dot `.` matches ANY character, INCLUDING newline `\n`.
# - `re.VERBOSE`    (`re.X`): Allows whitespace, formatting, and comments `#` inside pattern.
# - `re.ASCII`      (`re.A`): Restricts `\w`, `\W`, `\b`, `\B`, `\d`, `\D`, `\s`, `\S` to ASCII.
#
# Flags can be combined using the bitwise OR operator `|`:
# `pattern = re.compile(r"...", re.IGNORECASE | re.MULTILINE | re.VERBOSE)`

print_separator("1. Regex Compilation Flags: IGNORECASE, MULTILINE, DOTALL")

document = """Header: Security Audit
Status: PENDING
Note: Inspection requires
immediate follow-up.
Status: RESOLVED"""

# 1. Case-Insensitive Matching (re.I)
pending_match = re.search(r"status:\s*pending", document, re.IGNORECASE)
print(f"re.IGNORECASE search found: '{pending_match.group() if pending_match else None}'")

# 2. Multiline Anchor Matching (re.M)
all_statuses = re.findall(r"^Status:\s*(\w+)", document, re.MULTILINE)
print(f"re.MULTILINE anchors found all statuses: {all_statuses}")

# 3. Dot Matching Across Newlines (re.S / re.DOTALL)
note_single_line = re.search(r"Note:\s*(.*)", document)
note_dotall = re.search(r"Note:\s*(.*?)Status:", document, re.DOTALL)
print(f"Without DOTALL (stops at newline): '{note_single_line.group(1) if note_single_line else None}'")
print(f"With re.DOTALL (crosses newlines)  : '{note_dotall.group(1).strip() if note_dotall else None}'")


# ==============================================================================
# 2. EMBEDDED INLINE FLAGS: (?i), (?m), (?s), (?x)
# ==============================================================================
# In addition to passing flag arguments to `re.compile()`, Python supports embedding
# flags directly inside the pattern string at the very start:
# - `(?i)`: Case insensitive
# - `(?m)`: Multiline
# - `(?s)`: Dotall
# - `(?x)`: Verbose
#
# Or scoped to a specific group: `(?i:pattern)` applies only to that sub-group!

print_separator("2. Embedded Inline Flags: Global (?imsx) & Scoped (?i:...)")

mixed_input = "Error: timeout occurred. warning: disk threshold reached."

# Global inline flag:
inline_match = re.findall(r"(?i)\b(?:error|warning)\b", mixed_input)
print(f"Global inline flag (?i) matches: {inline_match}")

# Scoped inline flag (Only 'Error' is case-insensitive, 'Disk' is strictly case-sensitive):
scoped_pattern = re.compile(r"(?i:error):\s+.*?\s+(?-i:disk)")
print(f"Scoped flag match: '{scoped_pattern.search('ERROR: memory low on disk').group()}'")


# ==============================================================================
# 3. THE ELEGANCE OF re.VERBOSE (re.X)
# ==============================================================================
# In enterprise code, dense, one-line regex strings are write-only, unmaintainable,
# and high-risk.
#
# With `re.VERBOSE` (`re.X`):
# 1. Whitespace inside the regex is completely ignored (unless escaped or in character class).
# 2. You can span the regex across multiple lines.
# 3. You can add Python comments `#` explaining each section of the pattern.

print_separator("3. The Elegance of re.VERBOSE: Self-Documenting Regex")

# Anti-pattern: Dense, unreadable regex
unreadable_email = r"^[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"

# Enterprise clean pattern with re.VERBOSE:
readable_email = re.compile(
    r"""
    ^
    # Local part (username before @)
    [\w!#$%&'*+/=?^_`{|}~-]+
    (?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*
    
    @                           # Mandatory at-symbol separator
    
    # Domain host part
    (?:
        [a-zA-Z0-9]             # Must start with alphanumeric
        (?:[a-zA-Z0-9-]*[a-zA-Z0-9])?  # Middle hyphens/alphanumerics
        \.                      # Domain dot separator
    )+
    
    # Top-Level Domain (TLD) - at least 2 alpha characters
    [a-zA-Z]{2,}
    $
    """,
    re.VERBOSE
)

test_email = "dev.lead+audit@enterprise.cloud.internal"
is_valid_email = bool(readable_email.match(test_email))
print(f"Testing enterprise email '{test_email}': Valid = {is_valid_email}")


# ==============================================================================
# 4. ANTIPATTERN: WHEN NOT TO USE REGEX
# ==============================================================================
# "When all you have is a hammer, everything looks like a nail."
# Python's built-in `str` methods are written in optimized C and are frequently
# 5x to 10x faster and infinitely easier to read than regex for simple checks.
#
# Rule of Thumb:
# - Simple prefix check?    -> Use `str.startswith()`
# - Simple suffix check?    -> Use `str.endswith()`
# - Exact substring search? -> Use `in` operator
# - Single delimiter split? -> Use `str.split()`
# - Simple replacement?     -> Use `str.replace()`

print_separator("4. Antipattern: String Methods vs. Regex Benchmark")

filename = "financial_report_q4_2026.pdf"
benchmark_runs = 200_000

# Benchmark: Checking file extension with regex vs str.endswith
t0 = time.perf_counter()
re_ext = re.compile(r"\.pdf$")
for _ in range(benchmark_runs):
    _ = bool(re_ext.search(filename))
time_regex = time.perf_counter() - t0

t1 = time.perf_counter()
for _ in range(benchmark_runs):
    _ = filename.endswith(".pdf")
time_builtin = time.perf_counter() - t1

print(f"Checking '.pdf' extension over {benchmark_runs:,} iterations:")
print(f" - re.search() with compiled pattern : {time_regex:.4f}s")
print(f" - Built-in str.endswith('.pdf')     : {time_builtin:.4f}s")
print(f" -> Built-in method is {time_regex / time_builtin:.1f}x faster and zero-overhead!")


# ==============================================================================
# 5. THE UNESCAPED DOT TRAP
# ==============================================================================
# A common security bug in URL/domain filtering:
# Developer writes: `r"google.com"`
# But `.` matches ANY character! So `googleXcom` or `google-com` or `google1com`
# will also match! Always escape literal periods: `r"google\.com"`.

print_separator("5. The Unescaped Dot Trap in Domain Filtering")

buggy_domain = re.compile(r"google.com")
safe_domain = re.compile(r"^google\.com$")

phishing_url = "googleXcom"
print(f"Target: '{phishing_url}'")
print(f" - Buggy pattern r'google.com' match: {bool(buggy_domain.search(phishing_url))} (SECURITY RISK!)")
print(f" - Safe pattern r'^google\\.com$' match: {bool(safe_domain.search(phishing_url))} (Safely Rejected)")


# ==============================================================================
# 6. CATASTROPHIC BACKTRACKING & REDOS
# ==============================================================================
# Python's `re` module uses a backtracking NFA engine.
# If a regex has nested quantifiers with overlapping options, such as:
# `(a+)+$` or `(x+x+)+y`
#
# When given an input string that matches ALMOST everything except the final character,
# the engine attempts every permutation of grouping before failing.
#
# Permutations grow EXPONENTIALLY: O(2^n). An input of 30 characters can cause
# hundreds of millions of backtracks, freezing the Python process (CPU at 100%)!
# This vulnerability is called ReDoS (Regular Expression Denial of Service).

print_separator("6. Catastrophic Backtracking & ReDoS Prevention")

print("Understanding Exponential Backtracking:")
vulnerable_pattern = re.compile(r"^(a+)+$")

# Demonstrate with small string lengths:
for length in [16, 18, 20, 22]:
    evil_string = "a" * length + "!"  # Fails at the exclamation mark!
    start_t = time.perf_counter()
    vulnerable_pattern.search(evil_string)
    elapsed = time.perf_counter() - start_t
    print(f" - Input length {length:2d}: time = {elapsed:.6f} seconds")

print("\nNotice how execution time roughly doubles with every additional character!")
print("Input length 35 would freeze the server for hours!")

# Prevention Principles:
# 1. Eliminate nested quantifiers on identical character classes:
#    Bad : r"^(a+)+$"
#    Good: r"^a+$"
# 2. Make alternatives mutually exclusive:
#    Bad : r"(a|a)+"
#    Good: r"a+"
# 3. Anchor your expressions to reduce starting position searches.


# ==============================================================================
# 7. PRODUCTION DEMONSTRATION: MULTI-FORMAT TIMESTAMP NORMALIZER
# ==============================================================================
# Real-world enterprise systems receive timestamps in multiple inconsistent formats:
# 1. ISO 8601: `2026-10-19T08:14:22Z` or `2026-10-19 08:14:22`
# 2. US Slash format: `10/19/2026 08:14:22 AM`
# 3. Syslog format: `Oct 19 08:14:22`
# 4. Unix Epoch: `1760861662`
#
# We will build a production normalizer using clean `re.VERBOSE` pattern matching.

print_separator("7. Production Demonstration: Multi-Format Timestamp Normalizer")

class TimestampNormalizer:
    """Enterprise parser standardizing varied timestamp formats into UTC ISO-8601."""

    MONTH_MAP = {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
        "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
    }

    ISO_PATTERN = re.compile(
        r"""
        ^
        (?P<year>\d{4})
        -
        (?P<month>\d{2})
        -
        (?P<day>\d{2})
        [T\s]
        (?P<hour>\d{2})
        :
        (?P<minute>\d{2})
        :
        (?P<second>\d{2})
        (?:\.\d+)?
        (?:Z|[+-]\d{2}:\d{2})?
        $
        """,
        re.VERBOSE
    )

    US_PATTERN = re.compile(
        r"""
        ^
        (?P<month>\d{1,2})
        /
        (?P<day>\d{1,2})
        /
        (?P<year>\d{4})
        \s+
        (?P<hour>\d{1,2})
        :
        (?P<minute>\d{2})
        :
        (?P<second>\d{2})
        \s*
        (?P<meridiem>AM|PM)?
        $
        """,
        re.VERBOSE | re.IGNORECASE
    )

    SYSLOG_PATTERN = re.compile(
        r"""
        ^
        (?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)
        \s+
        (?P<day>\d{1,2})
        \s+
        (?P<hour>\d{2})
        :
        (?P<minute>\d{2})
        :
        (?P<second>\d{2})
        $
        """,
        re.VERBOSE
    )

    @classmethod
    def normalize_to_iso(cls, raw_ts: str, default_year: int = 2026) -> str:
        raw_ts = raw_ts.strip()

        # Check ISO
        m = cls.ISO_PATTERN.match(raw_ts)
        if m:
            d = m.groupdict()
            return f"{d['year']}-{d['month']}-{d['day']}T{d['hour']}:{d['minute']}:{d['second']}Z"

        # Check US
        m = cls.US_PATTERN.match(raw_ts)
        if m:
            d = m.groupdict()
            hour = int(d["hour"])
            if d.get("meridiem"):
                if d["meridiem"].upper() == "PM" and hour < 12:
                    hour += 12
                elif d["meridiem"].upper() == "AM" and hour == 12:
                    hour = 0
            return (
                f"{d['year']}-{int(d['month']):02d}-{int(d['day']):02d}"
                f"T{hour:02d}:{d['minute']}:{d['second']}Z"
            )

        # Check Syslog
        m = cls.SYSLOG_PATTERN.match(raw_ts)
        if m:
            d = m.groupdict()
            month_num = cls.MONTH_MAP[d["month"]]
            return (
                f"{default_year}-{month_num}-{int(d['day']):02d}"
                f"T{d['hour']}:{d['minute']}:{d['second']}Z"
            )

        raise ValueError(f"Unrecognized timestamp format: '{raw_ts}'")


sample_timestamps = [
    "2026-10-19T08:14:22Z",
    "2026-10-19 14:30:00",
    "10/19/2026 02:45:10 PM",
    "3/5/2026 09:15:00 AM",
    "Oct 19 08:14:22",
]

print("Normalizing Varied Enterprise Timestamps to Standard ISO UTC:")
for raw in sample_timestamps:
    standardized = TimestampNormalizer.normalize_to_iso(raw)
    print(f" Input: '{raw:24}' -> Standardized: '{standardized}'")

print("\n" + "=" * 78)
print(" End of Day 24 - Script 04: Flags, Performance & Pitfalls Complete")
print("=" * 78)
