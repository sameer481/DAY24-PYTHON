# Day 24: Python Regular Expressions (re) Masterclass 🔍⚡

Welcome to **Day 24** of the Python Mastery Series! Today's masterclass focuses on **Regular Expressions (Regex)** using Python's standard `re` module. Regular expressions are a formal, domain-specific grammar for high-performance pattern matching, tokenization, data extraction, validation, and text transformation.

```
       Pattern String (r"^USER_(?P<id>\d+)$")
                         │
                         ▼
        ┌─────────────────────────────────┐
        │       re.compile(..., flags)    │  (Lexing & Opcode Generation)
        └─────────────────────────────────┘
                         │
                         ▼
        ┌─────────────────────────────────┐
        │   Python NFA Backtracking Engine│  (C-accelerated state traversal)
        └─────────────────────────────────┘
          │                             │
    [ Match Found ]              [ No Match ]
          │                             │
          ▼                             ▼
   re.Match Object                    None
   ├── .group() / .groups()
   ├── .groupdict()
   └── .span() / .start() / .end()
```

---

## 📁 Repository Structure

```text
DAY24-PYTHON/
│
├── 01_regex_fundamentals_and_re_module.py       # Core philosophy, raw strings (r"..."), re.search/match/fullmatch/findall/finditer/sub/split, re.compile & Match anatomy
├── 02_metacharacters_quantifiers_and_character_classes.py # Metacharacters (., ^, $, |, \), sets [...], [^...], shorthands (\d, \w, \s), boundaries (\b, \B, \A, \Z), greedy vs lazy traps
├── 03_groups_capturing_and_advanced_assertions.py # Numbered & named groups (?P<name>), backreferences (\1, (?P=name), \g<name>), lookahead (?=, ?!), lookbehind (?<=, ?<!), fixed-width solutions
├── 04_regex_flags_compilation_and_pitfalls.py   # Flags (IGNORECASE, MULTILINE, DOTALL, VERBOSE, ASCII), inline (?imsx), ReDoS catastrophic backtracking, String vs Regex benchmarks
├── 05_practical_projects.py                     # 3 Industrial systems: SIEM Web Attack Detector, HIPAA/GDPR PII Sanitizer & Markdown-to-HTML Transpiler
├── .gitignore                                   # Standard Python bytecode, cache, venv, and IDE exclusions
└── README.md                                    # Architectural handbook, visual diagrams, tables & complete regex cheat-sheet
```

---

## 🧭 Why Regular Expressions Matter

In modern software development, raw text is messy, unstructured, and noisy. Whether you are parsing server logs, validating international phone numbers, sanitizing Personally Identifiable Information (PII) for GDPR/HIPAA compliance, or compiling markup languages into HTML, regular expressions provide a declarative syntax that replaces hundreds of lines of fragile procedural string slicing.

### The Problem: Fragile Procedural String Parsing

```python
# Procedural string slicing anti-pattern:
def extract_port(url: str) -> int:
    if "://" in url:
        url = url.split("://")[1]
    if "/" in url:
        url = url.split("/")[0]
    if ":" in url:
        parts = url.split(":")
        if parts[1].isdigit():
            return int(parts[1])
    return 80  # Fragile, fails on IPv6, query parameters, authentication, etc.
```

### The Solution: Declarative Regex Grammar

```python
import re

URL_PATTERN = re.compile(r"^[a-zA-Z]+://[^:/]+(?::(?P<port>\d+))?(?:/|$)")

def extract_port(url: str) -> int:
    match = URL_PATTERN.match(url)
    return int(match.group("port")) if match and match.group("port") else 80
```

---

## 📚 Core Concepts & Deep-Dive Breakdown

### 1. The Raw String (`r"..."`) Crux

In standard Python strings, the backslash `\` is an escape character for string literals (`\n`, `\t`, `\b`). In regular expressions, `\` is ALSO an escape character (`\d`, `\s`, `\b`).

Without raw strings (`r""`):
* `\b` is interpreted by Python as ASCII Backspace (`chr(8)`), **breaking** word boundary matching!
* Passing a literal backslash `\` to the regex engine requires four backslashes: `\\\\`.

Always prefix regex pattern literals with `r`:

```python
# BUGGY: Python turns \b into backspace before re module sees it!
buggy_boundary = "\bword\b" 

# CORRECT: Passed as raw characters into the regex engine
correct_boundary = r"\bword\b"
```

---

### 2. Matching Functions Comparison Matrix

| Function | Scan Scope | Match Position | Return Value (Success) | Return Value (Failure) | Typical Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `re.search()` | Entire string | First occurrence anywhere | `re.Match` | `None` | Finding a pattern anywhere in text |
| `re.match()` | Beginning only | Index `0` strictly | `re.Match` | `None` | Verifying command prefixes or lines |
| `re.fullmatch()`| Entire string | Start to End (`^...$`) | `re.Match` | `None` | Form validations (UUIDs, Emails, SemVer) |
| `re.findall()` | Entire string | All non-overlapping | `list` of strings/tuples| Empty `[]` | Quick batch extraction into memory |
| `re.finditer()`| Entire string | All non-overlapping | Iterator of `re.Match` | Empty iterator | Large files, streaming, span tracking |
| `re.split()` | Entire string | Delimiter occurrences | `list` of tokens | `[original_string]` | Tokenizing variable punctuation |
| `re.sub()` | Entire string | All occurrences | Transformed `str` | `original_string` | Redaction, template rendering |
| `re.subn()` | Entire string | All occurrences | `(new_str, count)` | `(original_str, 0)`| Substitution with count metrics |

---

### 3. Metacharacter & Character Class Quick Reference

```text
┌──────────────┬────────────────────────────────────────────────────────┐
│ Symbol       │ Description & Match Rule                               │
├──────────────┼────────────────────────────────────────────────────────┤
│ .            │ Wildcard: matches any character except newline (\n)    │
│ ^            │ Anchor: matches start of string (or line in MULTILINE) │
│ $            │ Anchor: matches end of string (or line in MULTILINE)   │
│ \A           │ Absolute string start (unaffected by MULTILINE)        │
│ \Z           │ Absolute string end (unaffected by MULTILINE)          │
│ \b           │ Word boundary: zero-width transition between \w and \W │
│ \B           │ Non-word boundary: position NOT at a word edge         │
│ \d / \D      │ Digit [0-9] / Non-digit [^0-9]                         │
│ \w / \W      │ Word char [a-zA-Z0-9_] / Non-word char                 │
│ \s / \S      │ Whitespace [ \t\n\r\f\v] / Non-whitespace              │
│ [abc]        │ Character class: matches either 'a', 'b', or 'c'       │
│ [^abc]       │ Negated character class: matches anything EXCEPT a,b,c │
│ [a-z]        │ Range: matches any ASCII character from 'a' to 'z'     │
│ a|b          │ Alternation: matches 'a' OR 'b'                        │
└──────────────┴────────────────────────────────────────────────────────┘
```

---

### 4. Quantifiers: Greedy vs. Lazy (Reluctant)

By default, quantifiers in Python are **greedy**—they consume as much input as possible and backtrack only when necessary:

| Quantifier | Greedy Type | Lazy Type | Description |
| :--- | :--- | :--- | :--- |
| `*` | `*` (0 to $\infty$) | `*?` (0 to $\infty$, minimum) | Match zero or more times |
| `+` | `+` (1 to $\infty$) | `+?` (1 to $\infty$, minimum) | Match one or more times |
| `?` | `?` (0 or 1) | `??` (0 or 1, prefer 0) | Match optional item |
| `{n}` | `{n}` (exactly $n$) | `{n}?` (exactly $n$) | Match exactly $n$ occurrences |
| `{n,}` | `{n,}` ($n$ to $\infty$) | `{n,}?` ($n$ to $\infty$, minimum)| Match at least $n$ occurrences |
| `{n,m}` | `{n,m}` ($n$ to $m$) | `{n,m}?` ($n$ to $m$, minimum) | Match between $n$ and $m$ times |

#### The Classic HTML Tag Trap

```python
snippet = "<div>First</div><div>Second</div>"

# Greedy trap: Swallows from the first '<' to the LAST '>'!
re.findall(r"<.*>", snippet)
# -> ['<div>First</div><div>Second</div>'] (1 match)

# Lazy solution: Stops at the FIRST closing '>'!
re.findall(r"<.*?>", snippet)
# -> ['<div>', '</div>', '<div>', '</div>'] (4 matches)
```

---

### 5. Grouping, Captures & Assertions

```text
┌───────────────────────┬───────────────────────────────────────────────────────────┐
│ Syntax                │ Type & Meaning                                            │
├───────────────────────┼───────────────────────────────────────────────────────────┤
│ (abc)                 │ Capturing group (indexed 1, 2, 3... left-to-right)        │
│ (?:abc)               │ Non-capturing group (groups without memory allocation)   │
│ (?P<name>abc)         │ Named capturing group (accessed via .group('name'))       │
│ \1, \2                │ Numbered backreference (matches exact text from group n)  │
│ (?P=name)             │ Named backreference inside pattern                        │
│ \g<name>, \g<1>       │ Backreference in replacement string of re.sub()           │
│ (?=abc)               │ Positive Lookahead: asserts 'abc' immediately follows     │
│ (?!abc)               │ Negative Lookahead: asserts 'abc' does NOT follow         │
│ (?<=abc)              │ Positive Lookbehind: asserts 'abc' immediately precedes   │
│ (?<!abc)              │ Negative Lookbehind: asserts 'abc' does NOT precede       │
└───────────────────────┴───────────────────────────────────────────────────────────┘
```

#### The Python Lookbehind Fixed-Width Constraint

In Python's standard `re` module, lookbehind assertions (`(?<=...)`, `(?<!...)`) must have a **fixed width**. Variable-length quantifiers (`*`, `+`, `?`) and alternations of unequal length fail:

```python
# FAILS with re.error: look-behind requires fixed-width pattern:
# r'(?<=(?:http://|https://))\w+'  (http:// is 7 chars, https:// is 8 chars)

# ARCHITECTURAL FIX: Alternation of multiple fixed-width lookbehinds:
r'(?:(?<=http://)|(?<=https://))[a-zA-Z0-9.-]+'
```

---

### 6. Compilation Flags Reference

Flags can be specified either via `re.compile(..., flags)` or via inline flag prefixes:

| Flag Name | Short Alias | Inline Prefix | Effect |
| :--- | :--- | :--- | :--- |
| `re.IGNORECASE` | `re.I` | `(?i)` | Case-insensitive matching |
| `re.MULTILINE` | `re.M` | `(?m)` | `^` and `$` match per line (`\n`) rather than whole string |
| `re.DOTALL` | `re.S` | `(?s)` | Dot `.` matches all characters including newline `\n` |
| `re.VERBOSE` | `re.X` | `(?x)` | Whitespace ignored; multi-line formatting with `#` comments |
| `re.ASCII` | `re.A` | `(?a)` | Restricts `\w`, `\b`, `\s`, `\d` to ASCII-only |

#### Writing Enterprise Patterns with `re.VERBOSE`

```python
SEMVER_REGEX = re.compile(
    r"""
    ^
    (?P<major>0|[1-9]\d*)       # Major version (no leading zeroes)
    \.
    (?P<minor>0|[1-9]\d*)       # Minor version
    \.
    (?P<patch>0|[1-9]\d*)       # Patch version
    (?:-(?P<prerelease>[\w.-]+))? # Optional pre-release tag (-rc.1)
    (?:\+(?P<build>[\w.-]+))?     # Optional build metadata (+build.2026)
    $
    """,
    re.VERBOSE
)
```

---

### 7. Performance & ReDoS (Catastrophic Backtracking)

Python uses an **NFA (Nondeterministic Finite Automaton)** engine with backtracking. When an expression contains nested quantifiers over overlapping character classes (e.g. `(a+)+$`), testing non-matching strings causes combinatorial explosion ($O(2^n)$):

```text
Pattern: ^(a+)+$  Target: "aaaaaaaaaaaaaaaaaaaa!"

Path 1: (a)(a)(a)...! -> Fail
Path 2: (aa)(a)(a)...! -> Fail
Path 3: (a)(aa)(a)...! -> Fail
...
Combinations: 2^20 = 1,048,576 backtracking steps for just 20 characters!
```

#### ReDoS Prevention Rules
1. **Never nest unbounded quantifiers**: Avoid `(a+)+`, `(x*)*`, `([a-zA-Z]+)*`.
2. **Make alternation branches mutually exclusive**: Avoid `(a|ab)+`.
3. **Anchor patterns early**: Use `^` and `$` to terminate failed searches immediately.
4. **Use String Methods when possible**: Python's `str.startswith()` and `str.endswith()` are **2.8x to 10x faster** than regex for simple prefix/suffix checks.

---

## 🛠️ Practical Projects Overview

### Project 1: Enterprise Multi-Tier SIEM Threat Analyzer (`05_practical_projects.py`)
* Analyzes raw HTTP access and authentication log streams.
* Detects **SQL Injection (SQLi)**, **Path Traversal / LFI (`../../etc/passwd`)**, **Cross-Site Scripting (XSS)**, and **Environment Probes (`.env`, `.git`)**.
* Decodes URL parameters (`urllib.parse.unquote_plus`) before signature evaluation.
* Outputs structured `SecurityIncident` reports with threat severity levels (`CRITICAL`, `HIGH`, `MEDIUM`).

### Project 2: HIPAA & GDPR Compliance PII Redactor (`05_practical_projects.py`)
* Audits unstructured patient/customer transcripts.
* Detects and dynamically redacts:
  * **Credit Card Numbers** with **Luhn Checksum Validation** (`************0007`).
  * **US Social Security Numbers (SSN)** (`***-**-6789`).
  * **Email Addresses** (`a***h@domain.com`).
  * **Phone Numbers** (`***-***-8765`).
  * **JWT Authentication Tokens** (`[JWT_REDACTED_eyJhbGci...]`).
* Employs callable replacement transforms in `re.sub()`.

### Project 3: Markdown-to-HTML Transpiler & Syntax Lexer (`05_practical_projects.py`)
* Converts Markdown documents into semantic HTML5 without external third-party dependencies.
* **Code Block Isolation**: Stashes fenced code blocks (` ```python `) before processing inline formatting, ensuring code contents are never corrupted.
* Renders headers (`#` to `######`), blockquotes (`>`), bold/italics (`**`, `*`), links (`[text](url)`), images, and unordered lists.

---

## 🚀 How to Run the Scripts

Clone or navigate to the repository directory and execute any script using Python 3:

```bash
# 1. Regex Fundamentals & The re Module
python 01_regex_fundamentals_and_re_module.py

# 2. Metacharacters, Character Classes & Quantifiers
python 02_metacharacters_quantifiers_and_character_classes.py

# 3. Groups, Backreferences & Assertions
python 03_groups_capturing_and_advanced_assertions.py

# 4. Flags, Performance Benchmarks & ReDoS Pitfalls
python 04_regex_flags_compilation_and_pitfalls.py

# 5. Production Systems (SIEM, PII Redactor, Markdown Transpiler)
python 05_practical_projects.py
```

---

## 📝 Best Practices Summary

1. **Always use raw strings (`r"..."`)** for regex pattern literals.
2. **Pre-compile repeated patterns** using `re.compile()` at module or class scope.
3. **Prefer `re.finditer()` over `re.findall()`** when streaming large datasets or when spans are required.
4. **Use Non-Capturing Groups `(?:...)`** unless you explicitly intend to extract captured data.
5. **Use Named Groups `(?P<name>...)`** for complex patterns to decouple code from group ordering.
6. **Self-document enterprise expressions** with `re.VERBOSE` (`re.X`) and inline comments.
7. **Beware of ReDoS**: Avoid nested quantifiers and overlapping alternations on untrusted user inputs.
8. **Know when NOT to use regex**: Leverage built-in string methods (`startswith`, `endswith`, `in`, `split`) for simple operations.
