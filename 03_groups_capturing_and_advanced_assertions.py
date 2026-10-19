"""
================================================================================
Day 24: Python Regular Expressions (re) - Groups, Captures & Assertions
================================================================================
While simple regex searches tell you IF a string matches, Groups and Assertions
allow you to extract structured components, enforce complex grammatical rules,
and assert contextual conditions without consuming characters.

Key Topics Covered in this Script:
1. Capturing Groups `(...)`: Nested Numbering & Left-Parenthesis Rule
2. Non-Capturing Groups `(?:...)`: Performance & Zero-Overhead Clustering
3. Named Capturing Groups `(?P<name>...)` & `.groupdict()` Extraction
4. Backreferences: Numbered `\\1` and Named `(?P=name)` in Search & `\\g<name>` in Sub
5. Lookahead Assertions: Positive `(?=...)` and Negative `(?!...)`
6. Lookbehind Assertions: Positive `(?<=...)` and Negative `(?<!...)`
7. The Python Fixed-Width Lookbehind Constraint & Architectural Workarounds
8. Production Demonstration: Enterprise Secret Key Scanner & Password Policy Enforcer
================================================================================
"""

import re
import sys
from typing import Dict, Any, List, Optional

# Ensure UTF-8 output across all operating systems
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def print_separator(title: str) -> None:
    """Utility helper to print structured visual headers for each demonstration."""
    print("\n" + "=" * 78)
    print(f" {title}")
    print("=" * 78)


# ==============================================================================
# 1. CAPTURING GROUPS & THE LEFT-PARENTHESIS NUMBERING RULE
# ==============================================================================
# Parentheses `(...)` fulfill two purposes:
# 1. Grouping: Treating multiple characters/sub-patterns as a single unit for quantifiers.
# 2. Capturing: Isolating and saving matched substrings for subsequent extraction.
#
# Group Numbering Rule:
# Groups are indexed 1, 2, 3... based on the order of their OPENING parenthesis `(`,
# from left to right, regardless of nesting depth.
# Group 0 is always the ENTIRE matched pattern.

print_separator("1. Capturing Groups & Nested Parentheses Numbering")

date_string = "Incident Date: 2026-10-19 14:35:50 UTC"

# Pattern with nested groups:
# Group 1: Full Date (2026-10-19)
#   Group 2: Year (2026)
#   Group 3: Month (10)
#   Group 4: Day (19)
# Group 5: Full Time (14:35:50)
#   Group 6: Hour (14)
#   Group 7: Minute (35)
#   Group 8: Second (50)
nested_pattern = re.compile(
    r"((\d{4})-(\d{2})-(\d{2}))\s+((\d{2}):(\d{2}):(\d{2}))"
)

match = nested_pattern.search(date_string)
if match:
    print(f"Target: '{date_string}'")
    print(f" Group 0 (Entire Match): '{match.group(0)}'")
    print(f" Group 1 (Full Date)   : '{match.group(1)}'")
    print(f" Group 2 (Year)        : '{match.group(2)}'")
    print(f" Group 3 (Month)       : '{match.group(3)}'")
    print(f" Group 4 (Day)         : '{match.group(4)}'")
    print(f" Group 5 (Full Time)   : '{match.group(5)}'")
    print(f" Group 6 (Hour)        : '{match.group(6)}'")
    print(f" Group 7 (Minute)      : '{match.group(7)}'")
    print(f" Group 8 (Second)      : '{match.group(8)}'")
    print(f" All groups tuple      : {match.groups()}")


# ==============================================================================
# 2. NON-CAPTURING GROUPS: (?:...)
# ==============================================================================
# Often, you need parentheses ONLY for applying a quantifier or alternation,
# but you DO NOT want to save the captured content:
#
# Disadvantages of unnecessary capturing groups:
# 1. Memory Overhead: The engine allocates memory buffers for each captured slice.
# 2. Clutters `.groups()`: Pollutes returned extraction tuples.
# 3. Breaks `re.findall()`: findall returns only groups when present!
#
# Solution: Use non-capturing syntax `(?:...)`!

print_separator("2. Non-Capturing Groups (?:...) for Clean Extraction")

ipv4_corpus = "DNS Server: 192.168.1.1, Gateway: 10.0.0.254, Netmask: 255.255.255.0"

# Anti-pattern: Accidental capturing group around the octet repetition
buggy_ip_pattern = re.compile(r"(\d{1,3}\.){3}\d{1,3}")
buggy_matches = buggy_ip_pattern.findall(ipv4_corpus)
print(f"Buggy findall with standard capturing group: {buggy_matches}")
print(" -> Returned ONLY the 3rd octet because '(\\d{1,3}\\.)' captured last iteration!")

# Clean solution: Non-capturing group (?:...)
clean_ip_pattern = re.compile(r"(?:\d{1,3}\.){3}\d{1,3}")
clean_matches = clean_ip_pattern.findall(ipv4_corpus)
print(f"Clean findall with non-capturing group (?:...): {clean_matches}")


# ==============================================================================
# 3. NAMED CAPTURING GROUPS: (?P<name>...)
# ==============================================================================
# When regex patterns grow complex, numeric group indices (group(1), group(4))
# make code fragile and unreadable. Inserting a new group shifts all indices!
#
# Syntax: `(?P<group_name>pattern)`
# Access: `match.group('group_name')` or dictionary `match.groupdict()`

print_separator("3. Named Capturing Groups (?P<name>...) & groupdict()")

url_sample = "https://developer.mozilla.org:8080/en-US/docs/Web/HTTP?query=regex#spec"

url_pattern = re.compile(
    r"^(?P<scheme>https?)://"
    r"(?P<host>[a-zA-Z0-9.-]+)"
    r"(?::(?P<port>\d+))?"
    r"(?P<path>/[a-zA-Z0-9_./-]*)?"
    r"(?:\?(?P<query>[^#\s]*))?"
    r"(?:#(?P<fragment>\S*))?$"
)

url_match = url_pattern.match(url_sample)
if url_match:
    print(f"Parsing URL: '{url_sample}'")
    url_data = url_match.groupdict()
    for key, value in url_data.items():
        print(f" - {key:10}: {value}")


# ==============================================================================
# 4. BACKREFERENCES: \1, (?P=name), AND \g<name>
# ==============================================================================
# Backreferences match the EXACT text that was previously matched by a capturing group.
#
# Use Cases:
# 1. Matching paired quotes: `'test'` or `"test"`, but not `'test"`!
# 2. Finding accidental duplicate words: "the the", "in in".
# 3. Matching XML/HTML opening and closing tags.
#
# In re.sub(): Use `\g<name>` or `\g<1>` to reference captured groups in replacements.

print_separator("4. Backreferences: Search (\\1, (?P=name)) & Replace (\\g<name>)")

# 1. Enforcing Paired Quotes with numbered backreference \1:
quoted_text = """Valid: 'single quotes' and "double quotes" | Invalid: 'mismatched" """
quote_pattern = re.compile(r"(['\"])(.*?)\1")
for m in quote_pattern.finditer(quoted_text):
    print(f" - Matched quote type {m.group(1)}: '{m.group(2)}'")

# 2. Named Backreference (?P=name) to catch repeated words:
prose_with_typos = "Paris in the the spring is is wonderful."
duplicate_word_pattern = re.compile(r"\b(?P<word>[a-zA-Z]+)\s+(?P=word)\b", re.IGNORECASE)

detected_dupes = [m.group("word") for m in duplicate_word_pattern.finditer(prose_with_typos)]
print(f"\nDetected duplicate words with (?P=name): {detected_dupes}")

# Remove duplicate words using re.sub with \g<word>:
deduped = duplicate_word_pattern.sub(r"\g<word>", prose_with_typos)
print(f"Deduplicated text: '{deduped}'")

# 3. Date Reformatting with \g<name>:
iso_date = "Created on 2026-10-19 and released on 2026-12-25."
reformatted_dates = re.sub(
    r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})",
    r"\g<day>/\g<month>/\g<year>",
    iso_date
)
print(f"ISO to European date format: '{reformatted_dates}'")


# ==============================================================================
# 5. LOOKAHEAD ASSERTIONS: (?=...) AND (?!...)
# ==============================================================================
# Lookaheads are zero-width assertions looking FORWARD in the string.
# They inspect what comes next without consuming any characters.
#
# - Positive Lookahead `(?=pattern)`: Matches only if `pattern` matches ahead.
# - Negative Lookahead `(?!pattern)`: Matches only if `pattern` does NOT match ahead.

print_separator("5. Lookahead Assertions: Positive (?=...) & Negative (?!...)")

# 1. Positive Lookahead: Password Policy Verification
# Password Requirements:
# - At least 8 characters
# - At least one uppercase letter: (?=.*[A-Z])
# - At least one lowercase letter: (?=.*[a-z])
# - At least one digit:            (?=.*\d)
# - At least one special symbol:   (?=.*[@$!%*?&])
password_regex = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
)

test_passwords = [
    ("SecurePass123!", True),
    ("weakpass", False),         # Missing upper, digit, symbol
    ("Valid@2026", True),
    ("NoSpecialChar99", False),  # Missing symbol
]

print("Lookahead Password Compliance Verification:")
for pwd, expected in test_passwords:
    valid = bool(password_regex.fullmatch(pwd))
    status = "PASS" if valid == expected else "FAIL"
    print(f" [{status}] '{pwd:18}' -> Compliant: {valid}")

# 2. Negative Lookahead: File Extension Filter
# Match filenames that do NOT end in .exe, .bat, or .dll
file_list = ["app.py", "malware.exe", "script.sh", "setup.bat", "data.json", "driver.dll"]
safe_file_pattern = re.compile(r"^[a-zA-Z0-9_-]+\.(?!(?:exe|bat|dll)$)[a-zA-Z0-9]+$")

safe_files = [f for f in file_list if safe_file_pattern.match(f)]
print(f"\nFiltered safe files (excluding .exe, .bat, .dll): {safe_files}")


# ==============================================================================
# 6. LOOKBEHIND ASSERTIONS: (?<=...) AND (?<!...)
# ==============================================================================
# Lookbehinds are zero-width assertions looking BACKWARD in the string.
#
# - Positive Lookbehind `(?<=pattern)`: Matches only if preceded by `pattern`.
# - Negative Lookbehind `(?<!pattern)`: Matches only if NOT preceded by `pattern`.
#
# Critical Python Engine Restriction:
# In Python's built-in `re` module, lookbehinds MUST have a FIXED, KNOWN WIDTH!
# Expressions like `(?<=https?://)` or `(?<=\d+)` will raise `re.error: look-behind requires fixed-width pattern`.
# Quantifiers like `*`, `+`, `?`, `{1,3}` are prohibited inside lookbehinds!

print_separator("6. Lookbehind Assertions & The Fixed-Width Constraint")

# 1. Positive Lookbehind: Extracting amounts without the currency symbol
financial_statement = "Revenue: $15400.00, Expenses: €8200.50, Profit: $7199.50"
dollar_amounts = re.findall(r"(?<=\$)\d+(?:\.\d{2})?", financial_statement)
print(f"Extracted dollar amounts (excluding '$'): {dollar_amounts}")

# 2. Negative Lookbehind: Matching unescaped quotation marks
# Matches `"` ONLY if it is not preceded by an escape backslash `\`
escaped_json_like = r'He said, "Hello \"World\", welcome back!"'
unescaped_quotes_pattern = re.compile(r'(?<!\\)"')

# Let's find spans of unescaped quotes
quote_positions = [m.start() for m in unescaped_quotes_pattern.finditer(escaped_json_like)]
print(f"Positions of unescaped double quotes: {quote_positions}")

# 3. Overcoming the Fixed-Width Constraint:
# In Python's standard re, even an alternation INSIDE a lookbehind fails if lengths differ:
# e.g., r'(?<=(?:http://|https://))' fails because 7 != 8 chars!
#
# Working Solution: Put the alternation OUTSIDE the lookbehind so each lookbehind is fixed-width!
# r'(?:(?<=http://)|(?<=https://))[a-zA-Z0-9.-]+'
try:
    # This demonstrates the engine exception:
    invalid_lookbehind = re.compile(r"(?<=(?:http://|https://))[a-zA-Z0-9.-]+")
except re.error as err:
    print(f"Expected engine exception for unequal branch lengths: {err}")

# Now the robust working solution:
working_lookbehind = re.compile(r"(?:(?<=http://)|(?<=https://))[a-zA-Z0-9.-]+")
domains = working_lookbehind.findall("Links: http://example.com and https://python.org")
print(f"Working multi-length lookbehind domains: {domains}")


# ==============================================================================
# 7. PRODUCTION DEMONSTRATION: ENTERPRISE SECRET SCANNER & POLICY ENFORCER
# ==============================================================================
# Build an automated enterprise DevSecOps scanner detecting:
# 1. AWS Access Key IDs (AKIA prefix, 20 alphanumeric chars)
# 2. GitHub Personal Access Tokens (ghp_ prefix, 36 characters)
# 3. JWT Authentication Tokens (three base64url segments separated by dots)
# 4. High-entropy API keys assigned in environment files

print_separator("7. Production Demonstration: Enterprise Secret Key Scanner")

sample_source_code = """
# Production Configuration File (DO NOT COMMIT SECRETS!)
AWS_REGION = "us-east-1"
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

GITHUB_SYNC_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyzAB"
SESSION_BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4ifQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
NORMAL_VARIABLE = "development_mode_active"
"""

class SecretKeyScanner:
    """Security audit scanner utilizing named groups and lookarounds."""

    SECRET_SIGNATURES: Dict[str, re.Pattern] = {
        "AWS Access Key ID": re.compile(r"\b(?P<secret>AKIA[0-9A-Z]{16})\b"),
        "GitHub Personal Access Token": re.compile(r"\b(?P<secret>ghp_[a-zA-Z0-9]{36})\b"),
        "JSON Web Token (JWT)": re.compile(
            r"\b(?P<secret>eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+)\b"
        ),
        "Generic Secret Variable Assignment": re.compile(
            r"(?i)(?:SECRET|PASSWORD|TOKEN|API_KEY)\s*=\s*['\"](?P<secret>[^'\"]{12,})['\"]"
        ),
    }

    @classmethod
    def scan_codebase(cls, source_code: str) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        for line_num, line in enumerate(source_code.splitlines(), start=1):
            for secret_type, pattern in cls.SECRET_SIGNATURES.items():
                for match in pattern.finditer(line):
                    raw_secret = match.group("secret")
                    # Mask secret for safe audit log display (keep first 4 and last 4 chars)
                    if len(raw_secret) > 8:
                        masked = f"{raw_secret[:4]}...{raw_secret[-4:]}"
                    else:
                        masked = "****"
                    findings.append({
                        "type": secret_type,
                        "line": line_num,
                        "span": match.span(),
                        "masked_value": masked
                    })
        return findings


detected_secrets = SecretKeyScanner.scan_codebase(sample_source_code)
print(f"DevSecOps Audit Complete: Found {len(detected_secrets)} exposed secrets!")
for finding in detected_secrets:
    print(
        f" [VULNERABILITY] Line {finding['line']:2d}: {finding['type']:35} "
        f"-> Masked: {finding['masked_value']}"
    )

print("\n" + "=" * 78)
print(" End of Day 24 - Script 03: Groups, Captures & Assertions Complete")
print("=" * 78)
