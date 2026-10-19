"""
================================================================================
Day 24: Python Regular Expressions (re) - Metacharacters, Sets & Quantifiers
================================================================================
At the heart of regular expressions lies a powerful grammar of symbols:
metacharacters, character classes (sets), boundaries, and quantifiers.

Mastering these building blocks is essential for writing precise, performant
patterns without falling into greedy traps or accidental false matches.

Key Topics Covered in this Script:
1. Core Metacharacters: `.`, `^`, `$`, `|`, and Escape `\`
2. Custom Character Classes: `[...]`, Negation `[^...]`, and Escape Rules Inside Sets
3. Shorthand Character Sequences: `\d`/`\D`, `\w`/`\W`, `\s`/`\S` (Unicode vs ASCII)
4. Positional Boundaries & Anchors: `^`/`$`, `\A`/`\Z`, and Word Boundaries `\b`/`\B`
5. Quantifier Mechanics: Fixed `{n}`, Unbounded `{n,}`, and Ranges `{n,m}`
6. The Greedy vs. Lazy (Reluctant) Dilemma: The Classic HTML Tag Trap
7. Production Demonstration: Developer Tooling Validator (SemVer, Hex Colors & Commits)
================================================================================
"""

import re
import sys
from typing import List, Dict, Tuple

# Ensure Windows stdout handles Unicode characters seamlessly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def print_separator(title: str) -> None:
    """Utility helper to print structured visual headers for each demonstration."""
    print("\n" + "=" * 78)
    print(f" {title}")
    print("=" * 78)


# ==============================================================================
# 1. CORE METACHARACTERS: ., ^, $, |, AND \
# ==============================================================================
# Metacharacters are characters with special syntactic meaning to the regex engine:
# - `.` (Dot): Matches ANY character EXCEPT a newline `\n` (unless re.DOTALL is used).
# - `^` (Caret): Asserts the start of the string (or line in MULTILINE mode).
# - `$` (Dollar): Asserts the end of the string (or line in MULTILINE mode).
# - `|` (Pipe): Logical alternation (OR operator). Evaluates left-to-right.
# - `\` (Backslash): Escapes metacharacters to treat them as literal characters.

print_separator("1. Core Metacharacters: ., ^, $, |, and Escape \\")

text_corpus = "cat cut cot c9t c.t c\nt"

# Dot wildcard matching:
dot_matches = re.findall(r"c.t", text_corpus)
print(f"Pattern r'c.t' matches: {dot_matches}")
print(" -> Notice 'c\\nt' was NOT matched because '.' excludes newline '\\n' by default!")

# Escaping the dot to match a literal period:
literal_dot = re.findall(r"c\.t", text_corpus)
print(f"Pattern r'c\\.t' (literal period) matches: {literal_dot}")

# Alternation with Pipe (|):
# CAUTION: Alternation has low precedence. `cat|dog food` matches 'cat' OR 'dog food',
# NOT 'cat food' OR 'dog food'. Use non-capturing groups `(?:cat|dog) food` to group!
phrase = "I love python and rust backend services"
found_languages = re.findall(r"\b(?:python|rust|golang|typescript)\b", phrase)
print(f"Alternation matches: {found_languages}")


# ==============================================================================
# 2. CUSTOM CHARACTER CLASSES / SETS: [...] AND [^...]
# ==============================================================================
# Square brackets define a character class (set). The engine matches EXACTLY ONE
# character from the set.
#
# Rules inside brackets:
# - `[aeiou]`: Matches any lowercase vowel.
# - `[a-z]`: Hyphen `-` defines an ASCII character range from 'a' through 'z'.
# - `[^0-9]`: Caret `^` immediately after `[` negates the set (matches any character NOT in set).
# - Special characters inside `[...]`:
#   Most metacharacters LOSE their special meaning inside brackets!
#   `[.]` matches a literal dot! `[*]` matches a literal asterisk!
#   Hyphen `-` is literal if placed at the VERY START `[-abc]` or VERY END `[abc-]`.
#   Right bracket `]` must be escaped `[abc\]]` or placed first `[]abc]`.

print_separator("2. Custom Character Sets [...] & Negation [^...]")

sample_words = "bat bit bot but b@t b.t b1t b-t"

# Matching specific vowels:
vowels_only = re.findall(r"b[aeiou]t", sample_words)
print(f"Vowel set r'b[aeiou]t': {vowels_only}")

# Negated set (anything EXCEPT vowels):
non_vowels = re.findall(r"b[^aeiou]t", sample_words)
print(f"Negated set r'b[^aeiou]t': {non_vowels}")

# Special characters inside sets (literal dot, literal hyphen):
# Placing hyphen at the very end makes it literal rather than a range
punct_set = re.findall(r"b[.-]t", sample_words)
print(f"Literal dot and hyphen r'b[.-]t': {punct_set}")


# ==============================================================================
# 3. SHORTHAND CHARACTER CLASSES & UNICODE AWARENESS
# ==============================================================================
# Python provides convenient shorthand escape sequences:
# - `\d`: Any digit. Default in Python 3 includes Unicode digits (e.g., Persian, Devanagari)!
#         Use `re.ASCII` or `[0-9]` to restrict to ASCII 0-9.
# - `\D`: Any non-digit (`[^0-9]` in ASCII mode).
# - `\w`: Any word character: letters, digits, and underscore `_`.
# - `\W`: Any non-word character (spaces, punctuation, symbols).
# - `\s`: Any whitespace character: space, `\t`, `\n`, `\r`, `\f`, `\v`.
# - `\S`: Any non-whitespace character.

print_separator("3. Shorthand Sequences: \\d, \\w, \\s & Unicode Awareness")

test_unicode = "Price: $45 in US, ۴۲ in Persian, and 50 in UK."

# Standard \d matches both ASCII and Unicode digits in Python 3!
all_digits = re.findall(r"\d+", test_unicode)
ascii_only_digits = re.findall(r"\d+", test_unicode, re.ASCII)
print(f"Standard \\d+ (Unicode-aware) : {all_digits}")
print(f"ASCII-only \\d+ (re.ASCII)    : {ascii_only_digits}")

# Word vs Non-Word:
code_identifier = "user_auth_v2.process_payment(tax_rate=0.08);"
identifiers = re.findall(r"\b\w+\b", code_identifier)
print(f"Extracted identifiers with \\w+: {identifiers}")

# Whitespace normalization with \s+:
messy_spacing = "Clean    up\t\t\nthis   uneven    \r\ntext."
cleaned = re.sub(r"\s+", " ", messy_spacing).strip()
print(f"Whitespace normalization: '{cleaned}'")


# ==============================================================================
# 4. POSITIONAL BOUNDARIES & ANCHORS: ^, $, \A, \Z, \b, \B
# ==============================================================================
# Boundaries are zero-width assertions. They don't consume characters; they verify
# position.
#
# - `^`: Asserts position at start of string (or line in MULTILINE).
# - `$`: Asserts position at end of string (or line in MULTILINE).
# - `\A`: Strictly the start of the string (IGNORES MULTILINE flag!).
# - `\Z`: Strictly the end of the string (IGNORES MULTILINE flag!).
# - `\b`: Word boundary. Asserts a transition between a word character `\w` and a
#         non-word character `\W` (or string edge).
# - `\B`: Non-word boundary. Asserts that current position is NOT a word boundary.

print_separator("4. Positional Boundaries & Anchors: ^, $, \\A, \\Z, \\b, \\B")

multiline_code = """import os
import sys
import json"""

print("Testing ^ in default vs MULTILINE mode:")
print(f"Default r'^import': {re.findall(r'^import', multiline_code)}")
print(f"MULTILINE r'^import': {re.findall(r'^import', multiline_code, re.MULTILINE)}")
abs_matches = re.findall(r"\Aimport", multiline_code, re.MULTILINE)
print(f"Absolute \\A r'\\Aimport': {abs_matches}")

# The Word Boundary (\b) Superpower:
# Problem: Matching 'cat' in 'The catalog of cats is scattered.'
sentence = "The catalog of cats is scattered."

search_without_boundary = re.findall(r"cat", sentence)
search_with_boundary = re.findall(r"\bcat\b", sentence)
search_plural = re.findall(r"\bcats?\b", sentence)

print(f"\nTarget sentence: '{sentence}'")
print(f"Without boundaries r'cat'   : {search_without_boundary} (Matches inside catalog, scattered!)")
print(f"Exact word boundary r'\\bcat\\b': {search_with_boundary} (Matches ONLY standalone word 'cat' - 0 matches)")
print(f"Singular/Plural r'\\bcats?\\b' : {search_plural} (Matches 'cats' accurately!)")

# Non-word boundary (\B):
# Matches 'cat' ONLY when it is embedded INSIDE another word:
inside_word = re.findall(r"\Bcat\w*", sentence)
print(f"Non-word boundary r'\\Bcat\\w*': {inside_word} (Found inside 'scattered')")


# ==============================================================================
# 5. QUANTIFIERS: GREEDY VS. LAZY (RELUCTANT)
# ==============================================================================
# Quantifiers specify how many times the preceding element may repeat:
#
# Standard (Greedy) Quantifiers:
# - `*`     : 0 or more times (Match as many as possible)
# - `+`     : 1 or more times (Match as many as possible)
# - `?`     : 0 or 1 time (Optional match)
# - `{n}`   : Exactly n times
# - `{n,}`  : At least n times
# - `{n,m}` : Between n and m times (inclusive)
#
# Lazy / Reluctant Quantifiers (append `?`):
# - `*?`    : 0 or more times (Match as FEW as possible)
# - `+?`    : 1 or more times (Match as FEW as possible)
# - `??`    : 0 or 1 time (Prefer 0 if possible)
# - `{n,m}?`: Between n and m times (Match as FEW as possible)

print_separator("5. The Greedy vs. Lazy Dilemma: The Classic HTML Tag Trap")

html_snippet = "<div>First Section</div><p>Paragraph</p><div>Second Section</div>"

# THE FATAL GREEDY MISTAKE:
# `r"<.*>"` matches '<' followed by ANY character as much as possible until the LAST '>'!
greedy_match = re.findall(r"<.*>", html_snippet)
print("Greedy r'<.*>':")
print(f" -> Result: {greedy_match}")
print(f" -> Swallowed the ENTIRE document into one match of length {len(greedy_match[0])}!")

# THE LAZY CORRECTION:
# `r"<.*?>"` matches '<' followed by as few characters as possible until the FIRST '>'!
lazy_matches = re.findall(r"<.*?>", html_snippet)
print("\nLazy r'<.*?>':")
print(f" -> Result: {lazy_matches}")
print(f" -> Extracted all {len(lazy_matches)} distinct HTML tags correctly!")

# Extracting content between tags cleanly:
tag_contents = re.findall(r"<div>(.*?)</div>", html_snippet)
print(f"\nExtracted div contents with lazy group r'<div>(.*?)</div>': {tag_contents}")


# ==============================================================================
# 6. EXACT & BOUNDED QUANTIFIER EXAMPLES
# ==============================================================================
print_separator("6. Bounded Quantifiers: Phone Numbers, Dates & Codes")

contact_card = """
John Doe | Tel: (555) 234-5678 | Cell: 555-876-5432 | Alt: 555.999.0000
Invalid: 123-45 | 555-12345678 | 00-1111-2222
"""

# Regex matching phone formats:
# (Optional area code in parentheses or digits) -> 3 digits -> separator -> 3 digits -> separator -> 4 digits
phone_pattern = re.compile(r"(?:\(\d{3}\)\s*|\b\d{3}[.-])\d{3}[.-]\d{4}\b")
extracted_phones = phone_pattern.findall(contact_card)
print(f"Extracted valid phone numbers: {extracted_phones}")


# ==============================================================================
# 7. PRODUCTION DEMONSTRATION: DEVELOPER TOOLING VALIDATOR
# ==============================================================================
# Build a comprehensive production validator for:
# 1. Semantic Versioning (SemVer 2.0.0 specification compliant pattern)
# 2. Hexadecimal Color Codes (#RGB, #RGBA, #RRGGBB, #RRGGBBAA)
# 3. Conventional Commit Messages (e.g., 'feat(auth): add OAuth2 provider')

print_separator("7. Production Demonstration: Developer Tooling Validator")

class DevToolValidator:
    """Production validator using pre-compiled regex with boundaries and sets."""

    # SemVer 2.0.0 official regex pattern
    SEMVER_PATTERN = re.compile(
        r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
        r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
        r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
        r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
    )

    # Hex Color pattern supporting 3, 4, 6, and 8 hex digits
    HEX_COLOR_PATTERN = re.compile(
        r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$"
    )

    # Conventional Commit specification pattern
    CONVENTIONAL_COMMIT_PATTERN = re.compile(
        r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
        r"(?:\([a-zA-Z0-9_-]+\))?"
        r"!?"
        r":\s+"
        r"[a-zA-Z0-9].{2,72}$"
    )

    @classmethod
    def validate_semver(cls, version: str) -> bool:
        return bool(cls.SEMVER_PATTERN.fullmatch(version))

    @classmethod
    def validate_hex_color(cls, color: str) -> bool:
        return bool(cls.HEX_COLOR_PATTERN.fullmatch(color))

    @classmethod
    def validate_commit_message(cls, message: str) -> bool:
        return bool(cls.CONVENTIONAL_COMMIT_PATTERN.fullmatch(message))


# Test SemVer
test_versions = [
    ("1.0.0", True),
    ("2.14.7-rc.1+build.482", True),
    ("0.0.1-alpha", True),
    ("01.2.3", False),  # Leading zeroes prohibited in major/minor/patch
    ("v1.0.0", False),  # Prefix 'v' is not pure SemVer
    ("1.2", False),     # Incomplete
]

print("Semantic Version Validation:")
for ver, expected in test_versions:
    res = DevToolValidator.validate_semver(ver)
    status = "PASS" if res == expected else "FAIL"
    print(f" [{status}] '{ver:25}' -> Valid: {res}")

# Test Hex Colors
test_colors = [
    ("#FFF", True),
    ("#1a2b3c", True),
    ("#1A2B3CFF", True),
    ("#GG1234", False),  # 'G' is not a valid hex digit
    ("#12345", False),   # 5 digits invalid
    ("123456", False),   # Missing '#' anchor
]

print("\nHex Color Validation:")
for col, expected in test_colors:
    res = DevToolValidator.validate_hex_color(col)
    status = "PASS" if res == expected else "FAIL"
    print(f" [{status}] '{col:12}' -> Valid: {res}")

# Test Conventional Commits
test_commits = [
    ("feat(auth): implement biometric WebAuthn support", True),
    ("fix!: drop deprecated legacy Python 2 runtime endpoints", True),
    ("docs: update masterclass architectural handbook", True),
    ("random commit message with no conventional prefix", False),
    ("feat(): missing scope content", False),
]

print("\nConventional Commit Validation:")
for msg, expected in test_commits:
    res = DevToolValidator.validate_commit_message(msg)
    status = "PASS" if res == expected else "FAIL"
    print(f" [{status}] '{msg[:48]:50}' -> Valid: {res}")

print("\n" + "=" * 78)
print(" End of Day 24 - Script 02: Metacharacters, Sets & Quantifiers Complete")
print("=" * 78)
