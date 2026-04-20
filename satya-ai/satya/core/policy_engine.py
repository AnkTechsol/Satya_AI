import re
import uuid
import time
import copy
from typing import Dict, Any, List, Optional
from ..schemas.evaluate import EvaluateResult, EvaluateViolation
from ..schemas.policy import PolicyRead
from .agent_registry import AgentRegistry

class PolicyEngine:
    """
    Evaluates agent actions against registered governance policies.
    """
    def __init__(self, agent_registry: AgentRegistry):
        self.agent_registry = agent_registry

    async def evaluate(
        self,
        agent_id: str,
        payload: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> EvaluateResult:
        """
        Evaluate payload against all active policies for this agent.

        Args:
            agent_id: Registered agent identifier
            payload: The raw request dict (prompt, messages, tool_calls, etc.)
            context: Optional metadata (user_id, session_id, ip, timestamp)

        Returns:
            EvaluateResult with decision, matched_policies, violations, and
            optionally a redacted_payload if any REDACT rules triggered.
        """
        start_time = time.perf_counter()
        event_id = f"evt_{uuid.uuid4().hex}"
        context = context or {}

        # 1. Check if agent is registered
        agent = await self.agent_registry.get_agent(agent_id)
        if not agent:
            latency = (time.perf_counter() - start_time) * 1000
            violation = EvaluateViolation(
                rule_id="builtin_agent_not_registered",
                policy_id="system",
                reason=f"Agent '{agent_id}' is not registered.",
                severity="CRITICAL"
            )
            return EvaluateResult(
                decision="DENY",
                event_id=event_id,
                latency_ms=latency,
                matched_policies=["system"],
                violations=[violation],
                payload=None
            )

        # 2. Fetch policies for this agent
        policies = await self.agent_registry.get_policies_for_agent(agent_id)

        decision = "ALLOW"
        matched_policies = []
        violations = []
        redacted_fields = []
        working_payload = copy.deepcopy(payload)

        # 3. Evaluate rules sequentially
        for policy in policies:
            if not policy.is_active:
                continue

            policy_matched = False
            for rule in policy.rules:
                is_match, extract = self._evaluate_rule(rule, working_payload)

                if is_match:
                    policy_matched = True
                    rule_id = rule.rule_id or f"rule_{uuid.uuid4().hex[:8]}"

                    if rule.action == "DENY":
                        violations.append(EvaluateViolation(
                            rule_id=rule_id,
                            policy_id=policy.id,
                            reason=rule.message,
                            severity=rule.severity
                        ))
                        decision = "DENY"
                        # Short circuit on DENY
                        break

                    elif rule.action == "REDACT":
                        if decision != "DENY": # Only redact if we aren't already denying
                            decision = "REDACT"
                            self._apply_redaction(working_payload, rule, extract)
                            redacted_fields.append(rule.field or "unknown_field")
                            violations.append(EvaluateViolation(
                                rule_id=rule_id,
                                policy_id=policy.id,
                                reason=rule.message,
                                severity=rule.severity
                            ))

                    elif rule.action in ["FLAG", "ALERT"]:
                        if decision not in ["DENY", "REDACT"]:
                            decision = rule.action
                        violations.append(EvaluateViolation(
                            rule_id=rule_id,
                            policy_id=policy.id,
                            reason=rule.message,
                            severity=rule.severity
                        ))

            if policy_matched:
                matched_policies.append(policy.id)

            if decision == "DENY":
                break

        latency = (time.perf_counter() - start_time) * 1000

        # Construct result based on decision
        if decision == "DENY":
            return EvaluateResult(
                decision=decision,
                event_id=event_id,
                latency_ms=latency,
                matched_policies=matched_policies,
                violations=violations,
                payload=None
            )
        elif decision == "REDACT":
            return EvaluateResult(
                decision=decision,
                event_id=event_id,
                latency_ms=latency,
                matched_policies=matched_policies,
                violations=violations,
                redacted_fields=redacted_fields,
                payload=working_payload
            )
        else:
            return EvaluateResult(
                decision=decision,
                event_id=event_id,
                latency_ms=latency,
                matched_policies=matched_policies,
                violations=violations if violations else None,
                payload=payload
            )

    def _evaluate_rule(self, rule, payload: Dict[str, Any]) -> tuple[bool, Any]:
        """Returns (is_match, extraction_context)"""
        if rule.condition == "contains_keyword":
            # Extract text from payload (simplified for v0.1)
            text = str(payload).lower()
            for kw in (rule.keywords or []):
                if kw.lower() in text:
                    return True, kw

        elif rule.condition == "exceeds_token_estimate":
            # Naive heuristic: ~4 chars per token
            text = str(payload)
            est_tokens = len(text) // 4
            if rule.threshold and est_tokens > rule.threshold:
                return True, est_tokens

        elif rule.condition == "missing_field":
            if rule.field:
                parts = rule.field.split('.')
                curr = payload
                for part in parts:
                    if isinstance(curr, dict) and part in curr:
                        curr = curr[part]
                    else:
                        return True, None

        elif rule.condition == "custom_regex":
            if rule.pattern:
                text_to_search = self._extract_field(payload, rule.field) if rule.field else str(payload)
                if isinstance(text_to_search, str) and re.search(rule.pattern, text_to_search):
                    return True, None

        return False, None

    def _extract_field(self, payload: Dict[str, Any], field_path: str) -> Any:
        """Simplified field extraction (handles basic dot notation and [*] arrays)."""
        if "[*]" in field_path:
            base, rest = field_path.split("[*]", 1)
            rest = rest.lstrip(".")

            # Navigate to base array
            curr = payload
            for part in base.split("."):
                if part and isinstance(curr, dict):
                    curr = curr.get(part, [])

            if isinstance(curr, list) and len(curr) > 0:
                # Just return a concatenated string of the nested fields for regex checking
                extracted = []
                for item in curr:
                    if rest and isinstance(item, dict):
                        extracted.append(str(item.get(rest, "")))
                    else:
                        extracted.append(str(item))
                return " ".join(extracted)
        else:
            curr = payload
            for part in field_path.split("."):
                if isinstance(curr, dict):
                    curr = curr.get(part)
                else:
                    return None
            return curr
        return str(payload)

    def _apply_redaction(self, payload: Dict[str, Any], rule, context: Any):
        """Applies redaction in-place to the payload."""
        if not rule.field:
            return

        # Very simplified redaction for v0.1
        if "[*]" in rule.field:
            base, rest = rule.field.split("[*]", 1)
            rest = rest.lstrip(".")

            curr = payload
            for part in base.split("."):
                if part and isinstance(curr, dict):
                    curr = curr.get(part, [])

            if isinstance(curr, list):
                for item in curr:
                    if rest and isinstance(item, dict) and rest in item:
                        if rule.condition == "custom_regex" and rule.pattern:
                            item[rest] = re.sub(rule.pattern, "[REDACTED]", str(item[rest]))
                        else:
                            item[rest] = "[REDACTED]"
        else:
            parts = rule.field.split(".")
            curr = payload
            for i, part in enumerate(parts):
                if i == len(parts) - 1 and isinstance(curr, dict) and part in curr:
                     if rule.condition == "custom_regex" and rule.pattern:
                         curr[part] = re.sub(rule.pattern, "[REDACTED]", str(curr[part]))
                     else:
                         curr[part] = "[REDACTED]"
                elif isinstance(curr, dict):
                    curr = curr.get(part, {})
