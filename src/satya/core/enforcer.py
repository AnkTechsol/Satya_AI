import re

class RuntimeEnforcer:
    """
    Lightweight, fast, regex and heuristic based policy enforcement layer.
    Zero tokens, zero APIs.
    """
    def __init__(self):
        # Compile PII patterns for fast execution
        self.pii_patterns = [
            # Email (basic)
            (re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'), '[EMAIL MASKED]'),
            # SSN (AAA-GG-SSSS)
            (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), '[SSN MASKED]'),
            # Credit Card (16 digits, optional dashes/spaces)
            (re.compile(r'\b(?:\d[ -]*?){13,16}\b'), '[CC MASKED]'),
            # Phone numbers (US/Intl loose format)
            (re.compile(r'\+?(?:\b\d{1,3}[-.\s]?)?\(?\b\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'), '[PHONE MASKED]'),
        ]

        # Jailbreak / Drift detection patterns
        # We compile these to avoid re-compilation overhead during execution.
        self.drift_patterns = [
            re.compile(r'ignore (all )?previous instructions', re.IGNORECASE),
            re.compile(r'you are now', re.IGNORECASE),
            re.compile(r'system prompt', re.IGNORECASE),
            re.compile(r'developer mode', re.IGNORECASE),
            re.compile(r'bypass (security|policy)', re.IGNORECASE),
            re.compile(r'DAN mode', re.IGNORECASE),
            re.compile(r'evil AI', re.IGNORECASE),
            re.compile(r'forget (your )?rules', re.IGNORECASE),
            re.compile(r'print your initial prompt', re.IGNORECASE),
            re.compile(r'disregard previous', re.IGNORECASE),
            re.compile(r'hypothetical scenario', re.IGNORECASE),
        ]

    def process_text(self, text: str) -> str:
        """
        Masks PII in the given text.
        """
        if not text:
            return text

        masked_text = text
        for pattern, replacement in self.pii_patterns:
            masked_text = pattern.sub(replacement, masked_text)

        return masked_text

    def check_drift(self, text: str) -> list[str]:
        """
        Checks if the given text contains any known jailbreak or drift phrases.
        Returns a list of matched phrases (empty if clean).
        """
        if not text:
            return []

        violations = []
        for pattern in self.drift_patterns:
            match = pattern.search(text)
            if match:
                violations.append(match.group(0))

        return violations
