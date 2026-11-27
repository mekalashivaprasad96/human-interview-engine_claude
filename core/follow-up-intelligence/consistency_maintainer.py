"""
Consistency Maintainer - Ensures consistency across extended interview sessions.
"""

from dataclasses import dataclass, field
from typing import Optional
from ..experience_enrichment.scenario_generator import Scenario
from ..experience_enrichment.project_modeler import ProjectModel
from ..numerical_intelligence.ledger import NumericalLedger


@dataclass
class ConsistencyCheck:
    check_name: str
    passed: bool
    message: str
    severity: str  # error, warning, info
    involved_elements: list = field(default_factory=list)


class ConsistencyMaintainer:
    """Maintains consistency across interview session."""

    def __init__(self):
        self.session_facts = {}  # Established facts during session
        self.numerical_values = {}  # Established numerical values
        self.architectures = {}  # Established architectures
        self.ownership_claims = {}  # Established ownership claims
        self.decisions = {}  # Established decisions
        self.timeline_events = {}  # Established timeline

    def register_fact(self, category: str, key: str, value: any, source: str = "answer"):
        """Register a fact established during the interview."""
        if category not in self.session_facts:
            self.session_facts[category] = {}
        self.session_facts[category][key] = {
            "value": value,
            "source": source,
            "timestamp": len(self.session_facts.get(category, {})),
        }

    def register_numerical(self, quantity: str, value: float, unit: str, context: str = ""):
        """Register a numerical value."""
        key = f"{quantity}_{context}" if context else quantity
        self.numerical_values[key] = {
            "value": value,
            "unit": unit,
            "quantity": quantity,
            "context": context,
        }

    def register_architecture(self, project_id: str, architecture: dict):
        """Register an architecture."""
        self.architectures[project_id] = architecture

    def register_ownership(self, project_id: str, component: str, ownership: str):
        """Register an ownership claim."""
        if project_id not in self.ownership_claims:
            self.ownership_claims[project_id] = {}
        self.ownership_claims[project_id][component] = ownership

    def register_decision(self, project_id: str, decision: str, rationale: str):
        """Register a decision."""
        if project_id not in self.decisions:
            self.decisions[project_id] = []
        self.decisions[project_id].append({
            "decision": decision,
            "rationale": rationale,
        })

    def register_timeline(self, project_id: str, event: str, timing: str):
        """Register a timeline event."""
        if project_id not in self.timeline_events:
            self.timeline_events[project_id] = []
        self.timeline_events[project_id].append({
            "event": event,
            "timing": timing,
        })

    def check_consistency(self, new_answer: dict, context: dict) -> list[ConsistencyCheck]:
        """Check new answer against established facts."""
        checks = []

        # Check numerical consistency
        checks.extend(self._check_numerical_consistency(new_answer, context))

        # Check architecture consistency
        checks.extend(self._check_architecture_consistency(new_answer, context))

        # Check ownership consistency
        checks.extend(self._check_ownership_consistency(new_answer, context))

        # Check decision consistency
        checks.extend(self._check_decision_consistency(new_answer, context))

        # Check timeline consistency
        checks.extend(self._check_timeline_consistency(new_answer, context))

        return checks

    def _check_numerical_consistency(self, answer: dict, context: dict) -> list[ConsistencyCheck]:
        """Check numerical values for consistency."""
        checks = []

        # Extract numerical claims from answer
        numerical_claims = answer.get("numerical_claims", [])

        for claim in numerical_claims:
            quantity = claim.get("quantity")
            value = claim.get("value")
            unit = claim.get("unit")
            proj_context = claim.get("context", "")

            key = f"{quantity}_{proj_context}" if proj_context else quantity

            if key in self.numerical_values:
                established = self.numerical_values[key]
                if abs(established["value"] - value) > 0.01 * max(abs(established["value"]), abs(value)):
                    checks.append(ConsistencyCheck(
                        check_name="numerical_consistency",
                        passed=False,
                        message=f"Numerical inconsistency: {quantity} claimed as {value} {unit}, previously established as {established['value']} {established['unit']}",
                        severity="error",
                        involved_elements=[key],
                    ))
                else:
                    checks.append(ConsistencyCheck(
                        check_name="numerical_consistency",
                        passed=True,
                        message=f"Numerical consistent: {quantity} = {value} {unit}",
                        severity="info",
                        involved_elements=[key],
                    ))
            else:
                # Register new value
                self.register_numerical(quantity, value, unit, proj_context)
                checks.append(ConsistencyCheck(
                    check_name="numerical_consistency",
                    passed=True,
                    message=f"New numerical value registered: {quantity} = {value} {unit}",
                    severity="info",
                    involved_elements=[key],
                ))

        return checks

    def _check_architecture_consistency(self, answer: dict, context: dict) -> list[ConsistencyCheck]:
        """Check architecture claims for consistency."""
        checks = []

        arch_claims = answer.get("architecture_claims", [])

        for claim in arch_claims:
            project_id = claim.get("project_id")
            component = claim.get("component")
            property_name = claim.get("property")
            value = claim.get("value")

            if project_id in self.architectures:
                established = self.architectures[project_id]
                components = established.get("components", [])

                for comp in components:
                    if comp.get("name") == component:
                        if property_name in comp and comp[property_name] != value:
                            checks.append(ConsistencyCheck(
                                check_name="architecture_consistency",
                                passed=False,
                                message=f"Architecture inconsistency: {component}.{property_name} claimed as {value}, previously {comp[property_name]}",
                                severity="error",
                                involved_elements=[f"{project_id}.{component}.{property_name}"],
                            ))
                        else:
                            checks.append(ConsistencyCheck(
                                check_name="architecture_consistency",
                                passed=True,
                                message=f"Architecture consistent: {component}.{property_name} = {value}",
                                severity="info",
                                involved_elements=[f"{project_id}.{component}.{property_name}"],
                            ))
                        break
            else:
                # Register new architecture
                if "architecture" in answer:
                    self.register_architecture(project_id, answer["architecture"])

        return checks

    def _check_ownership_consistency(self, answer: dict, context: dict) -> list[ConsistencyCheck]:
        """Check ownership claims for consistency."""
        checks = []

        ownership_claims = answer.get("ownership_claims", [])

        for claim in ownership_claims:
            project_id = claim.get("project_id")
            component = claim.get("component")
            ownership = claim.get("ownership")

            if project_id in self.ownership_claims:
                established = self.ownership_claims[project_id]
                if component in established:
                    if established[component] != ownership:
                        checks.append(ConsistencyCheck(
                            check_name="ownership_consistency",
                            passed=False,
                            message=f"Ownership inconsistency: {component} claimed as {ownership}, previously {established[component]}",
                            severity="warning",
                            involved_elements=[f"{project_id}.{component}"],
                        ))
                    else:
                        checks.append(ConsistencyCheck(
                            check_name="ownership_consistency",
                            passed=True,
                            message=f"Ownership consistent: {component} = {ownership}",
                            severity="info",
                            involved_elements=[f"{project_id}.{component}"],
                        ))
                else:
                    self.register_ownership(project_id, component, ownership)
            else:
                self.register_ownership(project_id, component, ownership)

        return checks

    def _check_decision_consistency(self, answer: dict, context: dict) -> list[ConsistencyCheck]:
        """Check decision claims for consistency."""
        checks = []

        decisions = answer.get("decisions", [])

        for decision in decisions:
            project_id = decision.get("project_id")
            decision_text = decision.get("decision")

            if project_id in self.decisions:
                established = self.decisions[project_id]
                for est in established:
                    if est["decision"] == decision_text:
                        # Check if rationale matches
                        if "rationale" in decision and decision["rationale"] != est.get("rationale"):
                            checks.append(ConsistencyCheck(
                                check_name="decision_consistency",
                                passed=False,
                                message=f"Decision rationale changed: {decision_text}",
                                severity="warning",
                                involved_elements=[f"{project_id}.{decision_text}"],
                            ))
                        break
                else:
                    # New decision for this project
                    self.register_decision(project_id, decision_text, decision.get("rationale", ""))
            else:
                self.register_decision(project_id, decision_text, decision.get("rationale", ""))

        return checks

    def _check_timeline_consistency(self, answer: dict, context: dict) -> list[ConsistencyCheck]:
        """Check timeline claims for consistency."""
        checks = []

        timeline = answer.get("timeline", [])

        for event in timeline:
            project_id = event.get("project_id")
            event_text = event.get("event")
            timing = event.get("timing")

            if project_id in self.timeline_events:
                established = self.timeline_events[project_id]
                for est in established:
                    if est["event"] == event_text and est["timing"] != timing:
                        checks.append(ConsistencyCheck(
                            check_name="timeline_consistency",
                            passed=False,
                            message=f"Timeline inconsistency: {event_text} claimed at {timing}, previously {est['timing']}",
                            severity="error",
                            involved_elements=[f"{project_id}.{event_text}"],
                        ))
                        break
                else:
                    self.register_timeline(project_id, event_text, timing)
            else:
                self.register_timeline(project_id, event_text, timing)

        return checks

    def get_established_fact(self, category: str, key: str) -> Optional[any]:
        """Get an established fact."""
        return self.session_facts.get(category, {}).get(key, {}).get("value")

    def get_established_numerical(self, quantity: str, context: str = "") -> Optional[dict]:
        """Get an established numerical value."""
        key = f"{quantity}_{context}" if context else quantity
        return self.numerical_values.get(key)

    def get_established_architecture(self, project_id: str) -> Optional[dict]:
        """Get established architecture."""
        return self.architectures.get(project_id)

    def get_established_ownership(self, project_id: str, component: str) -> Optional[str]:
        """Get established ownership."""
        return self.ownership_claims.get(project_id, {}).get(component)

    def get_all_established(self) -> dict:
        """Get all established facts."""
        return {
            "facts": self.session_facts,
            "numerical": self.numerical_values,
            "architectures": self.architectures,
            "ownership": self.ownership_claims,
            "decisions": self.decisions,
            "timeline": self.timeline_events,
        }

    def reset(self):
        """Reset all established facts."""
        self.session_facts = {}
        self.numerical_values = {}
        self.architectures = {}
        self.ownership_claims = {}
        self.decisions = {}
        self.timeline_events = {}