"""
Intent Analyzer - Analyzes interviewer intent behind questions.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class IntentCategory(Enum):
    NEW_QUESTION = "new_question"
    CLARIFICATION = "clarification"
    DEPTH_TEST = "depth_test"
    OWNERSHIP_TEST = "ownership_test"
    NUMERICAL_TEST = "numerical_test"
    BUSINESS_JUDGMENT_TEST = "business_judgment_test"
    LEADERSHIP_TEST = "leadership_test"
    COMMUNICATION_TEST = "communication_test"
    CHALLENGE = "challenge"
    CORRECTION = "correction"
    INFO_PROVIDING = "info_providing"
    RHETORICAL = "rhetorical"
    INTERRUPT = "interrupt"
    REPEAT = "repeat"
    TOPIC_CHANGE = "topic_change"
    ENDING = "ending"


@dataclass
class IntentAnalysis:
    primary_intent: IntentCategory
    secondary_intents: list = field(default_factory=list)
    confidence: float = 0.0
    competency_tested: str = ""
    expected_response_type: str = ""
    followup_likelihood: float = 0.0
    pressure_indicator: str = "normal"


class IntentAnalyzer:
    """Analyzes interviewer intent from question structure and context."""

    INTENT_PATTERNS = {
        IntentCategory.NEW_QUESTION: {
            "patterns": [
                r"^(tell me about|describe|walk me through|explain|how do you|what is|what was)",
                r"^(give me an example|give an example|can you share)",
            ],
            "competencies": ["knowledge", "experience", "communication"],
            "response_type": "substantive_answer",
            "followup_likelihood": 0.7,
        },
        IntentCategory.CLARIFICATION: {
            "patterns": [
                r"^(can you clarify|what do you mean|could you elaborate|expand on)",
                r"^(when you say|you mentioned|earlier you said)",
            ],
            "competencies": ["communication", "precision"],
            "response_type": "clarification",
            "followup_likelihood": 0.5,
        },
        IntentCategory.DEPTH_TEST: {
            "patterns": [
                r"^(how exactly|what specifically|in detail|deep dive|technical details)",
                r"^(implementation|architecture|configuration|under the hood|internally)",
            ],
            "competencies": ["technical_depth", "implementation_knowledge"],
            "response_type": "detailed_technical",
            "followup_likelihood": 0.8,
        },
        IntentCategory.OWNERSHIP_TEST: {
            "patterns": [
                r"^(what did you (personally|actually|directly)|your (role|contribution|ownership))",
                r"^(you (specifically|personally)|individual (contribution|responsibility))",
            ],
            "competencies": ["ownership", "individual_impact", "honesty"],
            "response_type": "ownership_clarification",
            "followup_likelihood": 0.6,
        },
        IntentCategory.NUMERICAL_TEST: {
            "patterns": [
                r"^(how many|how much|what (percentage|ratio|number|figure))",
                r"^(give me a number|exact (number|figure)|quantify|measure)",
            ],
            "competencies": ["numerical_reasoning", "precision", "measurement"],
            "response_type": "numerical_answer",
            "followup_likelihood": 0.7,
        },
        IntentCategory.BUSINESS_JUDGMENT_TEST: {
            "patterns": [
                r"^(business (impact|value|case|justification)|roi|investment|cost)",
                r"^(customer (impact|value)|revenue|strategic|priority|tradeoff)",
            ],
            "competencies": ["business_acumen", "prioritization", "stakeholder_alignment"],
            "response_type": "business_reasoning",
            "followup_likelihood": 0.6,
        },
        IntentCategory.LEADERSHIP_TEST: {
            "patterns": [
                r"^(how do you (lead|manage|mentor|hire|build team|handle conflict))",
                r"^(leadership|team (dynamic|culture)|performance (review|management))",
            ],
            "competencies": ["leadership", "people_management", "team_building"],
            "response_type": "leadership_example",
            "followup_likelihood": 0.7,
        },
        IntentCategory.COMMUNICATION_TEST: {
            "patterns": [
                r"^(explain to (a non-technical|an executive|a customer|someone without))",
                r"^(how would you (communicate|present|convince|influence))",
            ],
            "competencies": ["communication", "audience_adaptation", "influence"],
            "response_type": "adapted_explanation",
            "followup_likelihood": 0.5,
        },
        IntentCategory.CHALLENGE: {
            "patterns": [
                r"^(are you sure|really|but|however|what about|counter|devil's advocate)",
                r"^(i disagree|that doesn't|i've seen|in my experience|actually)",
                r"^(prove|evidence|validate|justify|defend)",
            ],
            "competencies": ["confidence", "evidence_based", "pressure_handling"],
            "response_type": "defended_position",
            "followup_likelihood": 0.8,
            "pressure": "high",
        },
        IntentCategory.CORRECTION: {
            "patterns": [
                r"^(actually|correction|that's not|i think you|not quite|slight correction)",
                r"^(the (correct|right|accurate) (way|answer|approach) is)",
            ],
            "competencies": ["humility", "learning", "accuracy"],
            "response_type": "acknowledge_correction",
            "followup_likelihood": 0.4,
        },
        IntentCategory.INFO_PROVIDING: {
            "patterns": [
                r"^(let me (tell|share|give) you|here's (some|the) (context|background|info))",
                r"^(for context|background:|important to note|keep in mind)",
            ],
            "competencies": ["active_listening", "incorporation"],
            "response_type": "acknowledge_and_incorporate",
            "followup_likelihood": 0.3,
        },
        IntentCategory.RHETORICAL: {
            "patterns": [
                r"^(right\?|correct\?|makes sense\?|don't you think\?|wouldn't you agree\?)",
            ],
            "competencies": ["engagement", "agreement"],
            "response_type": "brief_acknowledgment",
            "followup_likelihood": 0.2,
        },
        IntentCategory.INTERRUPT: {
            "patterns": [
                r"^(hold on|wait|stop|let me interrupt|before you go on)",
            ],
            "competencies": ["adaptability", "pivot"],
            "response_type": "pause_and_pivot",
            "followup_likelihood": 0.9,
            "pressure": "high",
        },
        IntentCategory.REPEAT: {
            "patterns": [
                r"^(again|once more|repeat|rephrase|different way)",
            ],
            "competencies": ["clarity", "patience", "adaptation"],
            "response_type": "rephrased_answer",
            "followup_likelihood": 0.5,
        },
        IntentCategory.TOPIC_CHANGE: {
            "patterns": [
                r"^(moving on|next topic|different subject|let's talk about|switching gears)",
            ],
            "competencies": ["adaptability", "breadth"],
            "response_type": "new_topic_answer",
            "followup_likelihood": 0.6,
        },
        IntentCategory.ENDING: {
            "patterns": [
                r"^(that's all|no more questions|we're (done|out of time)|thank you|wrap up)",
            ],
            "competencies": ["closing"],
            "response_type": "closing_response",
            "followup_likelihood": 0.0,
        },
    }

    def __init__(self):
        pass

    def analyze(self, question: str, context: dict = None) -> IntentAnalysis:
        """Analyze interviewer intent from question."""
        q_lower = question.lower().strip()

        # Score each intent category
        scores = {}
        for intent, data in self.INTENT_PATTERNS.items():
            score = 0.0
            for pattern in data["patterns"]:
                if re.search(pattern, q_lower, re.IGNORECASE):
                    score += 1.0
            scores[intent] = score

        # Boost based on context
        if context:
            prev_intent = context.get("previous_intent")
            if prev_intent and prev_intent in scores:
                # Likely follow-up
                if prev_intent in [IntentCategory.DEPTH_TEST, IntentCategory.OWNERSHIP_TEST, IntentCategory.NUMERICAL_TEST]:
                    scores[IntentCategory.DEPTH_TEST] += 0.5
                    scores[IntentCategory.OWNERSHIP_TEST] += 0.5
                    scores[IntentCategory.NUMERICAL_TEST] += 0.5

            # Check for follow-up markers
            followup_markers = ["follow", "deeper", "more detail", "specifically", "exactly", "precisely"]
            if any(m in q_lower for m in followup_markers):
                scores[IntentCategory.DEPTH_TEST] += 1.0
                scores[IntentCategory.OWNERSHIP_TEST] += 0.5

        # Determine primary intent
        if max(scores.values()) > 0:
            primary = max(scores, key=scores.get)
            confidence = min(scores[primary] / 2.0, 1.0)
        else:
            primary = IntentCategory.NEW_QUESTION
            confidence = 0.5

        # Secondary intents (above threshold)
        secondary = [intent for intent, score in scores.items() if score > 0.5 and intent != primary]

        # Get metadata
        intent_data = self.INTENT_PATTERNS.get(primary, {})
        competency = intent_data.get("competencies", ["general"])[0]
        response_type = intent_data.get("response_type", "general")
        followup_likelihood = intent_data.get("followup_likelihood", 0.5)
        pressure = intent_data.get("pressure", "normal")

        return IntentAnalysis(
            primary_intent=primary,
            secondary_intents=secondary,
            confidence=confidence,
            competency_tested=competency,
            expected_response_type=response_type,
            followup_likelihood=followup_likelihood,
            pressure_indicator=pressure,
        )

    def predict_followup_intents(self, current_intent: IntentCategory) -> list[IntentCategory]:
        """Predict likely follow-up intents."""
        followup_map = {
            IntentCategory.NEW_QUESTION: [IntentCategory.DEPTH_TEST, IntentCategory.OWNERSHIP_TEST, IntentCategory.NUMERICAL_TEST],
            IntentCategory.DEPTH_TEST: [IntentCategory.DEPTH_TEST, IntentCategory.NUMERICAL_TEST, IntentCategory.CHALLENGE],
            IntentCategory.OWNERSHIP_TEST: [IntentCategory.OWNERSHIP_TEST, IntentCategory.NUMERICAL_TEST, IntentCategory.CHALLENGE],
            IntentCategory.NUMERICAL_TEST: [IntentCategory.NUMERICAL_TEST, IntentCategory.DEPTH_TEST, IntentCategory.CHALLENGE],
            IntentCategory.BUSINESS_JUDGMENT_TEST: [IntentCategory.BUSINESS_JUDGMENT_TEST, IntentCategory.LEADERSHIP_TEST],
            IntentCategory.LEADERSHIP_TEST: [IntentCategory.LEADERSHIP_TEST, IntentCategory.BEHAVIORAL, IntentCategory.CHALLENGE],
            IntentCategory.CHALLENGE: [IntentCategory.CHALLENGE, IntentCategory.DEPTH_TEST, IntentCategory.NUMERICAL_TEST],
            IntentCategory.CORRECTION: [IntentCategory.NEW_QUESTION, IntentCategory.DEPTH_TEST],
            IntentCategory.INFO_PROVIDING: [IntentCategory.NEW_QUESTION],
        }
        return followup_map.get(current_intent, [IntentCategory.NEW_QUESTION])

    def is_pressure_increasing(self, recent_intents: list[IntentCategory]) -> bool:
        """Detect if interview pressure is increasing."""
        pressure_intents = {IntentCategory.CHALLENGE, IntentCategory.DEPTH_TEST, IntentCategory.OWNERSHIP_TEST, IntentCategory.NUMERICAL_TEST}
        recent_pressure = sum(1 for i in recent_intents[-3:] if i in pressure_intents)
        earlier_pressure = sum(1 for i in recent_intents[-6:-3] if i in pressure_intents)
        return recent_pressure > earlier_pressure


import re
from dataclasses import field