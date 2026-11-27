"""
Interviewer Classifier - Classifies interviewer type from behavior and questions.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class InterviewerType(Enum):
    RECRUITER = "recruiter"
    HIRING_MANAGER = "hiring_manager"
    TECHNICAL_SPECIALIST = "technical_specialist"
    SENIOR_ENGINEER = "senior_engineer"
    ARCHITECT = "architect"
    EXECUTIVE = "executive"
    CUSTOMER_STAKEHOLDER = "customer_stakeholder"
    BEHAVIORAL_INTERVIEWER = "behavioral_interviewer"
    SYSTEM_DESIGN_INTERVIEWER = "system_design_interviewer"
    SKEPTICAL_INTERVIEWER = "skeptical_interviewer"
    COLLABORATIVE_INTERVIEWER = "collaborative_interviewer"
    PANEL_MEMBER = "panel_member"
    UNKNOWN = "unknown"


@dataclass
class InterviewerProfile:
    type: InterviewerType
    confidence: float
    name: str = ""
    role: str = ""
    company: str = ""
    background: str = ""
    signals: list = field(default_factory=list)


class InterviewerClassifier:
    """Classifies interviewer type from questions and behavior."""

    TYPE_KEYWORDS = {
        InterviewerType.RECRUITER: [
            "tell me about yourself", "walk me through your resume", "why this company",
            "what are you looking for", "salary expectations", "notice period",
            "career goals", "why leaving", "availability", "relocation",
        ],
        InterviewerType.HIRING_MANAGER: [
            "how do you prioritize", "team conflict", "difficult decision",
            "mentoring", "hiring", "performance review", "project delivery",
            "stakeholder management", "cross-functional", "roadmap",
        ],
        InterviewerType.TECHNICAL_SPECIALIST: [
            "implement", "debug", "optimize", "code review", "design pattern",
            "data structure", "algorithm", "complexity", "framework", "library",
            "configuration", "deployment", "testing", "ci/cd",
        ],
        InterviewerType.SENIOR_ENGINEER: [
            "technical leadership", "architecture decision", "tradeoff", "scalability",
            "technical debt", "refactor", "mentoring junior", "code quality",
            "best practice", "technical strategy",
        ],
        InterviewerType.ARCHITECT: [
            "system design", "architecture", "scale", "distributed", "consistency",
            "availability", "partition tolerance", "cap theorem", "eventual consistency",
            "service mesh", "api gateway", "event driven", "microservices",
            "failure mode", "disaster recovery", "capacity planning",
        ],
        InterviewerType.EXECUTIVE: [
            "business impact", "roi", "strategy", "investment", "risk",
            "competitive", "market", "customer", "revenue", "cost",
            "organizational", "transformation", "vision", "roadmap",
        ],
        InterviewerType.BEHAVIORAL_INTERVIEWER: [
            "tell me about a time", "give an example", "describe a situation",
            "how did you handle", "conflict", "failure", "mistake", "disagreement",
            "pressure", "deadline", "ambiguity", "ethical",
        ],
        InterviewerType.SYSTEM_DESIGN_INTERVIEWER: [
            "design a", "architect a", "scale to", "million users",
            "high availability", "low latency", "data model", "api design",
            "database schema", "caching strategy", "load balancing",
        ],
        InterviewerType.SKEPTICAL_INTERVIEWER: [
            "are you sure", "really", "prove it", "evidence", "how do you know",
            "what if", "but", "however", "counterargument", "devil's advocate",
        ],
        InterviewerType.COLLABORATIVE_INTERVIEWER: [
            "what do you think", "how would you approach", "let's explore",
            "interesting", "tell me more", "curious", "perspective",
        ],
    }

    BEHAVIORAL_SIGNALS = {
        InterviewerType.RECRUITER: ["rapid_fire_questions", "checking_boxes", "surface_level", "selling_company"],
        InterviewerType.HIRING_MANAGER: ["deep_dive_ownership", "team_fit_focus", "delivery_oriented", "growth_mindset"],
        InterviewerType.TECHNICAL_SPECIALIST: ["specific_technical_probes", "implementation_focus", "tool_knowledge", "debugging_scenarios"],
        InterviewerType.SENIOR_ENGINEER: ["judgment_questions", "tradeoff_exploration", "mentoring_signals", "long_term_thinking"],
        InterviewerType.ARCHITECT: ["requirements_first", "constraint_exploration", "failure_mode_analysis", "operational_thinking"],
        InterviewerType.EXECUTIVE: ["business_first", "strategic_questions", "concise_expectations", "outcome_focused"],
        InterviewerType.BEHAVIORAL_INTERVIEWER: ["star_probing", "specifics_requested", "reflection_seeking", "growth_oriented"],
        InterviewerType.SYSTEM_DESIGN_INTERVIEWER: ["blank_slate", "iterative_refinement", "constraint_discussion", "tradeoff_explicit"],
        InterviewerType.SKEPTICAL_INTERVIEWER: ["challenging_assumptions", "demanding_evidence", "pressure_testing", "devils_advocate"],
        InterviewerType.COLLABORATIVE_INTERVIEWER: ["building_on_answers", "encouraging_thinking", "mutual_exploration", "low_pressure"],
    }

    def __init__(self):
        self.question_history = []
        self.behavior_history = []

    def classify(self, question: str, context: dict = None) -> InterviewerProfile:
        """Classify interviewer from current question and context."""
        scores = {itype: 0.0 for itype in InterviewerType}
        signals = []

        # Score based on keywords
        q_lower = question.lower()
        for itype, keywords in self.TYPE_KEYWORDS.items():
            for kw in keywords:
                if kw in q_lower:
                    scores[itype] += 1.0
                    signals.append(f"Keyword: '{kw}' suggests {itype.value}")

        # Score based on context
        if context:
            # Previous questions
            prev_questions = context.get("previous_questions", [])
            for prev_q in prev_questions:
                prev_lower = prev_q.lower()
                for itype, keywords in self.TYPE_KEYWORDS.items():
                    for kw in keywords:
                        if kw in prev_lower:
                            scores[itype] += 0.5

            # Interviewer info
            interviewer_role = context.get("interviewer_role", "").lower()
            role_mapping = {
                "recruiter": InterviewerType.RECRUITER,
                "talent": InterviewerType.RECRUITER,
                "hr": InterviewerType.RECRUITER,
                "hiring manager": InterviewerType.HIRING_MANAGER,
                "manager": InterviewerType.HIRING_MANAGER,
                "engineering manager": InterviewerType.HIRING_MANAGER,
                "technical lead": InterviewerType.SENIOR_ENGINEER,
                "tech lead": InterviewerType.SENIOR_ENGINEER,
                "senior engineer": InterviewerType.SENIOR_ENGINEER,
                "staff engineer": InterviewerType.SENIOR_ENGINEER,
                "principal engineer": InterviewerType.ARCHITECT,
                "architect": InterviewerType.ARCHITECT,
                "director": InterviewerType.EXECUTIVE,
                "vp": InterviewerType.EXECUTIVE,
                "cto": InterviewerType.EXECUTIVE,
                "behavioral": InterviewerType.BEHAVIORAL_INTERVIEWER,
                "system design": InterviewerType.SYSTEM_DESIGN_INTERVIEWER,
            }
            for role_key, itype in role_mapping.items():
                if role_key in interviewer_role:
                    scores[itype] += 2.0
                    signals.append(f"Role: '{interviewer_role}' suggests {itype.value}")

        # Determine best match
        if max(scores.values()) > 0:
            best_type = max(scores, key=scores.get)
            confidence = min(scores[best_type] / 3.0, 1.0)
        else:
            best_type = InterviewerType.UNKNOWN
            confidence = 0.0

        # Store for history
        self.question_history.append((question, best_type))

        profile = InterviewerProfile(
            type=best_type,
            confidence=confidence,
            signals=signals,
        )

        # Add context info if available
        if context:
            profile.name = context.get("interviewer_name", "")
            profile.role = context.get("interviewer_role", "")
            profile.company = context.get("company", "")
            profile.background = context.get("interviewer_background", "")

        return profile

    def update_from_behavior(self, behavior: str, context: dict = None):
        """Update classification based on observed behavior."""
        self.behavior_history.append((behavior, context))

        # This would refine the classification over time
        # For now, just track

    def get_consensus_type(self) -> InterviewerType:
        """Get consensus type from history."""
        if not self.question_history:
            return InterviewerType.UNKNOWN

        type_counts = {}
        for _, itype in self.question_history:
            type_counts[itype] = type_counts.get(itype, 0) + 1

        return max(type_counts, key=type_counts.get)

    def get_type_distribution(self) -> dict:
        """Get distribution of classified types."""
        dist = {itype: 0 for itype in InterviewerType}
        for _, itype in self.question_history:
            dist[itype] += 1
        return dist

    def predict_next_question_type(self) -> list[str]:
        """Predict likely next question types based on interviewer type."""
        consensus = self.get_consensus_type()

        predictions = {
            InterviewerType.RECRUITER: ["behavioral", "motivation", "logistics", "culture_fit"],
            InterviewerType.HIRING_MANAGER: ["behavioral", "leadership", "project_management", "team_dynamics"],
            InterviewerType.TECHNICAL_SPECIALIST: ["implementation", "debugging", "technical_concept", "optimization"],
            InterviewerType.SENIOR_ENGINEER: ["technical_judgment", "architecture", "tradeoffs", "mentoring"],
            InterviewerType.ARCHITECT: ["system_design", "scalability", "failure_modes", "tradeoffs"],
            InterviewerType.EXECUTIVE: ["strategy", "business_impact", "risk", "investment"],
            InterviewerType.BEHAVIORAL_INTERVIEWER: ["behavioral", "failure", "conflict", "growth"],
            InterviewerType.SYSTEM_DESIGN_INTERVIEWER: ["system_design", "scalability", "data_modeling", "api_design"],
            InterviewerType.SKEPTICAL_INTERVIEWER: ["challenge", "evidence_request", "counterargument", "pressure"],
            InterviewerType.COLLABORATIVE_INTERVIEWER: ["exploration", "hypothetical", "thinking_process", "collaboration"],
        }

        return predictions.get(consensus, ["technical", "behavioral", "system_design"])

    def reset(self):
        """Reset classifier state."""
        self.question_history = []
        self.behavior_history = []


from dataclasses import field