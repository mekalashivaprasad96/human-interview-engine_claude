"""
Follow-up Handler - Processes follow-up questions and maintains context.
"""

from dataclasses import dataclass, field
from typing import Optional
from ..interviewer_intelligence.intent_analyzer import IntentCategory
from ..experience_enrichment.scenario_generator import Scenario
from ..experience_enrichment.project_modeler import ProjectModel
from ..numerical_intelligence.ledger import NumericalLedger


@dataclass
class FollowUpContext:
    original_question: str
    original_answer: str
    followup_question: str
    followup_intent: IntentCategory
    depth: int
    topic: str
    referenced_entities: list = field(default_factory=list)
    numerical_refs: list = field(default_factory=list)


class FollowUpHandler:
    """Handles follow-up questions with context awareness."""

    FOLLOWUP_TYPES = {
        "deeper_technical": [
            "how exactly", "what specifically", "implementation detail",
            "configuration", "under the hood", "internally",
        ],
        "ownership_clarification": [
            "what did you", "your role", "your contribution", "personally",
            "individually", "specifically you",
        ],
        "numerical_probe": [
            "how many", "how much", "what percentage", "exact number",
            "give me a number", "quantify",
        ],
        "decision_challenge": [
            "why did you", "why not", "alternatives", "tradeoff",
            "what if", "devil's advocate",
        ],
        "evidence_request": [
            "how do you know", "prove it", "evidence", "measure",
            "baseline", "how measured",
        ],
        "scenario_extension": [
            "what would happen", "if that failed", "scale to",
            "what about", "edge case",
        ],
        "correction_response": [
            "actually", "that's not", "correction", "not quite",
        ],
    }

    def __init__(self):
        pass

    def process_followup(self, context: FollowUpContext,
                          scenario: Scenario, model: ProjectModel,
                          ledger: NumericalLedger) -> dict:
        """Process a follow-up question and generate response context."""
        # Analyze follow-up type
        followup_type = self._classify_followup(context.followup_question)

        # Determine what specific information is needed
        info_needed = self._identify_info_needed(context, followup_type)

        # Retrieve relevant context from scenario/model/ledger
        retrieved = self._retrieve_context(info_needed, scenario, model, ledger, context)

        # Check consistency with previous answer
        consistency = self._check_consistency(context, retrieved, ledger)

        return {
            "followup_type": followup_type,
            "info_needed": info_needed,
            "retrieved_context": retrieved,
            "consistency_check": consistency,
            "response_strategy": self._determine_strategy(followup_type, consistency),
        }

    def _classify_followup(self, question: str) -> str:
        """Classify follow-up question type."""
        q_lower = question.lower()

        for ftype, keywords in self.FOLLOWUP_TYPES.items():
            for kw in keywords:
                if kw in q_lower:
                    return ftype

        return "general_clarification"

    def _identify_info_needed(self, context: FollowUpContext, followup_type: str) -> dict:
        """Identify what specific information is needed."""
        info = {
            "entities": [],
            "numerical": [],
            "technical_details": [],
            "ownership": [],
            "decisions": [],
            "metrics": [],
        }

        q_lower = context.followup_question.lower()

        # Extract entities referenced
        if "that" in q_lower or "it" in q_lower or "the" in q_lower:
            info["entities"] = context.referenced_entities

        # Numerical probes
        if followup_type == "numerical_probe":
            if "many" in q_lower:
                info["numerical"].append("count")
            if "much" in q_lower:
                info["numerical"].append("volume")
            if "percentage" in q_lower or "percent" in q_lower:
                info["numerical"].append("percentage")

        # Technical details
        if followup_type == "deeper_technical":
            if "config" in q_lower:
                info["technical_details"].append("configuration")
            if "algorithm" in q_lower or "approach" in q_lower:
                info["technical_details"].append("algorithm")
            if "architect" in q_lower:
                info["technical_details"].append("architecture")

        # Ownership
        if followup_type == "ownership_clarification":
            info["ownership"] = ["specific_contribution", "decision_authority"]

        # Decisions
        if followup_type == "decision_challenge":
            info["decisions"] = ["rationale", "alternatives", "tradeoffs"]

        # Evidence
        if followup_type == "evidence_request":
            info["metrics"] = ["baseline", "measurement_method", "validation"]

        return info

    def _retrieve_context(self, info_needed: dict, scenario: Scenario,
                           model: ProjectModel, ledger: NumericalLedger,
                           context: FollowUpContext) -> dict:
        """Retrieve relevant context from knowledge sources."""
        retrieved = {}

        # From scenario
        if info_needed.get("technical_details"):
            retrieved["architecture"] = scenario.architecture
            retrieved["implementation"] = scenario.implementation_details
            retrieved["tech_env"] = scenario.technical_environment

        if info_needed.get("ownership"):
            retrieved["contributions"] = scenario.individual_contributions
            retrieved["role"] = scenario.candidate_role

        if info_needed.get("decisions"):
            retrieved["key_decisions"] = scenario.architecture.get('key_decisions', [])
            retrieved["tradeoffs"] = scenario.architecture.get('tradeoffs', [])

        if info_needed.get("metrics"):
            retrieved["outcomes"] = scenario.outcomes
            retrieved["challenges"] = scenario.challenges

        # From project model
        if info_needed.get("technical_details") or info_needed.get("metrics"):
            retrieved["numerical_model"] = model.numerical_model
            retrieved["timeline"] = model.timeline
            retrieved["team"] = model.team

        # From ledger
        if info_needed.get("numerical"):
            for num_type in info_needed["numerical"]:
                entries = self._get_ledger_entries(ledger, num_type, context)
                if entries:
                    retrieved[f"ledger_{num_type}"] = entries

        return retrieved

    def _get_ledger_entries(self, ledger: NumericalLedger, num_type: str,
                             context: FollowUpContext) -> list:
        """Get relevant ledger entries."""
        entries = []

        if num_type == "count":
            # Look for node, server, team, GPU counts
            for entry in ledger.entries.values():
                if any(kw in entry.quantity.lower() for kw in ['node', 'server', 'team', 'gpu', 'count']):
                    entries.append(entry)
        elif num_type == "volume":
            for entry in ledger.entries.values():
                if any(kw in entry.quantity.lower() for kw in ['request', 'transaction', 'data', 'volume', 'throughput']):
                    entries.append(entry)
        elif num_type == "percentage":
            for entry in ledger.entries.values():
                if entry.unit in ['%', 'percent', 'percentage']:
                    entries.append(entry)

        return entries

    def _check_consistency(self, context: FollowUpContext,
                            retrieved: dict, ledger: NumericalLedger) -> dict:
        """Check consistency with previous answer."""
        issues = []

        # Check numerical consistency
        if "ledger_count" in retrieved:
            for entry in retrieved["ledger_count"]:
                if entry.conflicts:
                    issues.append(f"Numerical conflict: {entry.conflicts[0]}")

        # Check ownership consistency
        if "contributions" in retrieved:
            # Verify ownership claims match
            pass

        # Check decision consistency
        if "key_decisions" in retrieved:
            # Verify decisions haven't changed
            pass

        return {
            "consistent": len(issues) == 0,
            "issues": issues,
        }

    def _determine_strategy(self, followup_type: str, consistency: dict) -> str:
        """Determine response strategy."""
        if not consistency["consistent"]:
            return "acknowledge_and_correct"

        strategies = {
            "deeper_technical": "expand_technical_detail",
            "ownership_clarification": "clarify_ownership",
            "numerical_probe": "provide_exact_number",
            "decision_challenge": "defend_with_rationale",
            "evidence_request": "provide_measurement_detail",
            "scenario_extension": "extend_scenario",
            "correction_response": "acknowledge_and_correct",
        }

        return strategies.get(followup_type, "direct_answer")

    def extract_referenced_entities(self, question: str, previous_answer: str) -> list:
        """Extract entities referenced in follow-up."""
        entities = []

        # Simple extraction - in production would use NLP
        # Look for pronouns and references
        q_lower = question.lower()
        if "that" in q_lower or "it" in q_lower:
            # Find nouns in previous answer
            import re
            nouns = re.findall(r'\b[A-Z][a-z]+\b|\b\w+(?:service|system|component|database|api)\b', previous_answer)
            entities.extend(nouns[:5])

        return list(set(entities))