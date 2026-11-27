"""
Behavior Tracker - Tracks interviewer behavior patterns across the interview.
"""

from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict
from .interviewer_classifier import InterviewerType
from .intent_analyzer import IntentCategory


@dataclass
class InterviewerBehavior:
    type: InterviewerType
    intent_distribution: dict = field(default_factory=dict)
    question_count: int = 0
    followup_depth: int = 0
    pressure_level: str = "normal"
    engagement_style: str = "neutral"
    topic_coverage: list = field(default_factory=list)
    correction_count: int = 0
    challenge_count: int = 0
    info_providing_count: int = 0
    rhetorical_count: int = 0
    interrupt_count: int = 0
    repeat_count: int = 0
    topic_change_count: int = 0


class BehaviorTracker:
    """Tracks and analyzes interviewer behavior patterns."""

    def __init__(self):
        self.behavior = InterviewerBehavior(type=InterviewerType.UNKNOWN)
        self.intent_history = []
        self.question_history = []
        self.topic_history = []

    def record_question(self, question: str, intent: IntentCategory, interviewer_type: InterviewerType,
                        topic: str = ""):
        """Record a question and its analysis."""
        self.behavior.type = interviewer_type
        self.behavior.question_count += 1

        # Update intent distribution
        intent_key = intent.value
        self.behavior.intent_distribution[intent_key] = self.behavior.intent_distribution.get(intent_key, 0) + 1

        # Track pressure indicators
        if intent in [IntentCategory.CHALLENGE, IntentCategory.DEPTH_TEST,
                      IntentCategory.OWNERSHIP_TEST, IntentCategory.NUMERICAL_TEST]:
            self.behavior.challenge_count += 1
        if intent == IntentCategory.CORRECTION:
            self.behavior.correction_count += 1
        if intent == IntentCategory.INFO_PROVIDING:
            self.behavior.info_providing_count += 1
        if intent == IntentCategory.RHETORICAL:
            self.behavior.rhetorical_count += 1
        if intent == IntentCategory.INTERRUPT:
            self.behavior.interrupt_count += 1
        if intent == IntentCategory.REPEAT:
            self.behavior.repeat_count += 1
        if intent == IntentCategory.TOPIC_CHANGE:
            self.behavior.topic_change_count += 1

        # Track topics
        if topic:
            self.topic_history.append(topic)
            if topic not in self.behavior.topic_coverage:
                self.behavior.topic_coverage.append(topic)

        # Update pressure level
        self._update_pressure_level()

        # Store history
        self.intent_history.append(intent)
        self.question_history.append(question)

    def _update_pressure_level(self):
        """Update pressure level based on behavior."""
        total = self.behavior.question_count
        if total == 0:
            return

        pressure_ratio = (self.behavior.challenge_count + self.behavior.correction_count +
                          self.behavior.interrupt_count) / total

        if pressure_ratio > 0.5:
            self.behavior.pressure_level = "high"
        elif pressure_ratio > 0.3:
            self.behavior.pressure_level = "moderate"
        elif pressure_ratio > 0.1:
            self.behavior.pressure_level = "low"
        else:
            self.behavior.pressure_level = "normal"

    def get_behavior_summary(self) -> dict:
        """Get summary of interviewer behavior."""
        return {
            "type": self.behavior.type.value,
            "question_count": self.behavior.question_count,
            "intent_distribution": self.behavior.intent_distribution,
            "pressure_level": self.behavior.pressure_level,
            "followup_depth": self.behavior.followup_depth,
            "topic_coverage": self.behavior.topic_coverage,
            "challenge_rate": self.behavior.challenge_count / max(self.behavior.question_count, 1),
            "correction_rate": self.behavior.correction_count / max(self.behavior.question_count, 1),
            "info_sharing_rate": self.behavior.info_providing_count / max(self.behavior.question_count, 1),
            "topic_changes": self.behavior.topic_change_count,
        }

    def get_pressure_trend(self) -> str:
        """Get pressure trend over interview."""
        if len(self.intent_history) < 3:
            return "insufficient_data"

        recent_pressure = sum(1 for i in self.intent_history[-3:]
                              if i in [IntentCategory.CHALLENGE, IntentCategory.DEPTH_TEST,
                                       IntentCategory.OWNERSHIP_TEST, IntentCategory.NUMERICAL_TEST])
        earlier_pressure = sum(1 for i in self.intent_history[-6:-3]
                               if i in [IntentCategory.CHALLENGE, IntentCategory.DEPTH_TEST,
                                        IntentCategory.OWNERSHIP_TEST, IntentCategory.NUMERICAL_TEST])

        if recent_pressure > earlier_pressure:
            return "increasing"
        elif recent_pressure < earlier_pressure:
            return "decreasing"
        return "stable"

    def predict_next_behavior(self) -> dict:
        """Predict likely next interviewer behavior."""
        if not self.intent_history:
            return {"predicted_intent": "new_question", "confidence": 0.3}

        last_intent = self.intent_history[-1]

        # Transition probabilities
        transitions = {
            IntentCategory.NEW_QUESTION: {
                IntentCategory.DEPTH_TEST: 0.3,
                IntentCategory.OWNERSHIP_TEST: 0.2,
                IntentCategory.NUMERICAL_TEST: 0.2,
                IntentCategory.NEW_QUESTION: 0.3,
            },
            IntentCategory.DEPTH_TEST: {
                IntentCategory.DEPTH_TEST: 0.4,
                IntentCategory.NUMERICAL_TEST: 0.2,
                IntentCategory.CHALLENGE: 0.2,
                IntentCategory.NEW_QUESTION: 0.2,
            },
            IntentCategory.OWNERSHIP_TEST: {
                IntentCategory.OWNERSHIP_TEST: 0.3,
                IntentCategory.NUMERICAL_TEST: 0.3,
                IntentCategory.CHALLENGE: 0.2,
                IntentCategory.NEW_QUESTION: 0.2,
            },
            IntentCategory.NUMERICAL_TEST: {
                IntentCategory.NUMERICAL_TEST: 0.3,
                IntentCategory.DEPTH_TEST: 0.3,
                IntentCategory.CHALLENGE: 0.2,
                IntentCategory.NEW_QUESTION: 0.2,
            },
            IntentCategory.CHALLENGE: {
                IntentCategory.CHALLENGE: 0.3,
                IntentCategory.DEPTH_TEST: 0.3,
                IntentCategory.NUMERICAL_TEST: 0.2,
                IntentCategory.NEW_QUESTION: 0.2,
            },
            IntentCategory.CORRECTION: {
                IntentCategory.NEW_QUESTION: 0.5,
                IntentCategory.DEPTH_TEST: 0.3,
                IntentCategory.NUMERICAL_TEST: 0.2,
            },
            IntentCategory.INFO_PROVIDING: {
                IntentCategory.NEW_QUESTION: 0.6,
                IntentCategory.DEPTH_TEST: 0.2,
                IntentCategory.OWNERSHIP_TEST: 0.2,
            },
            IntentCategory.TOPIC_CHANGE: {
                IntentCategory.NEW_QUESTION: 0.7,
                IntentCategory.DEPTH_TEST: 0.2,
                IntentCategory.OWNERSHIP_TEST: 0.1,
            },
        }

        probs = transitions.get(last_intent, {IntentCategory.NEW_QUESTION: 1.0})
        predicted = max(probs, key=probs.get)
        confidence = probs[predicted]

        return {
            "predicted_intent": predicted.value,
            "confidence": confidence,
            "pressure_trend": self.get_pressure_trend(),
        }

    def detect_patterns(self) -> list[str]:
        """Detect behavioral patterns."""
        patterns = []

        # Rapid-fire questions
        if self.behavior.question_count > 10 and self.behavior.followup_depth < 2:
            patterns.append("rapid_fire_questions")

        # Deep dive pattern
        depth_ratio = self.behavior.intent_distribution.get("depth_test", 0) / max(self.behavior.question_count, 1)
        if depth_ratio > 0.4:
            patterns.append("deep_dive_oriented")

        # Challenge-heavy
        if self.behavior.pressure_level == "high":
            patterns.append("high_pressure")

        # Collaborative
        if self.behavior.info_providing_count > self.behavior.challenge_count:
            patterns.append("collaborative")

        # Structured/behavioral
        if self.behavior.intent_distribution.get("leadership_test", 0) > 2:
            patterns.append("behavioral_focus")

        # System design focus
        if self.behavior.intent_distribution.get("business_judgment_test", 0) > 2:
            patterns.append("strategic_focus")

        # Skeptical
        if self.behavior.correction_count > 2:
            patterns.append("skeptical")

        return patterns

    def reset(self):
        """Reset tracker."""
        self.behavior = InterviewerBehavior(type=InterviewerType.UNKNOWN)
        self.intent_history = []
        self.question_history = []
        self.topic_history = []