"""
Response Generator - Generates natural human-like spoken responses.
"""

from dataclasses import dataclass, field
from typing import Optional
from ..candidate_intelligence.persona_builder import ProfessionalPersona
from .style_adapter import StyleAdapter


@dataclass
class ResponseContext:
    question: str
    question_type: str  # factual, technical, behavioral, hypothetical, numerical, clarification
    interviewer_type: str  # recruiter, hiring_manager, technical_specialist, architect, executive
    relevant_experience: dict = field(default_factory=dict)
    numerical_data: dict = field(default_factory=dict)
    previous_answer: str = ""
    followup_depth: int = 0
    pressure_level: str = "normal"  # normal, challenging, skeptical
    mode: str = "immersive"  # immersive, authentic, technical, etc.


@dataclass
class GeneratedResponse:
    text: str
    reasoning_trace: dict = field(default_factory=dict)
    evidence_used: list = field(default_factory=list)
    numerical_entries_referenced: list = field(default_factory=list)
    estimated_duration_seconds: float = 0.0


class ResponseGenerator:
    """Generates natural spoken responses based on context and persona."""

    # Duration guidelines by question type (seconds)
    DURATION_GUIDELINES = {
        "acknowledgment": (2, 5),
        "simple_confirmation": (5, 15),
        "numerical_clarification": (5, 20),
        "narrow_technical_followup": (10, 30),
        "recruiter_question": (30, 60),
        "technical_concept": (30, 60),
        "implementation_question": (45, 90),
        "troubleshooting_scenario": (60, 120),
        "behavioral_question": (75, 120),
        "complex_hypothetical": (90, 180),
        "system_design_initial": (120, 180),
        "executive_followup": (30, 45),
    }

    # Opening patterns by style
    OPENING_PATTERNS = {
        "direct": [
            "So, ",
            "The short answer: ",
            "Here's what happened: ",
            "Directly: ",
        ],
        "analytical": [
            "Breaking it down, ",
            "There are a few factors here: ",
            "Let me structure this: ",
            "From first principles: ",
        ],
        "narrative": [
            "Let me give you an example: ",
            "Here's what happened: ",
            "The context was: ",
            "Walking through it: ",
        ],
        "collaborative": [
            "From the team's perspective, ",
            "We approached it by ",
            "The consensus was ",
            "Working together, ",
        ],
        "executive": [
            "Strategically, ",
            "The business impact was: ",
            "At the organizational level: ",
            "Key takeaway: ",
        ],
        "technical-deep": [
            "Implementation-wise, ",
            "Under the hood, ",
            "At the system level, ",
            "Technically: ",
        ],
        "balanced": [
            "In practice, ",
            "What worked was: ",
            "The approach was: ",
            "Here's how it worked: ",
        ],
    }

    # Transition patterns
    TRANSITION_PATTERNS = {
        "elaboration": [
            "The key thing was ",
            "What made the difference was ",
            "The critical decision was ",
            "Digging deeper, ",
        ],
        "contrast": [
            "However, ",
            "On the flip side, ",
            "That said, ",
            "But the reality was ",
        ],
        "causation": [
            "Because ",
            "Since ",
            "Given that ",
            "This led to ",
        ],
        "example": [
            "For instance, ",
            "A concrete example: ",
            "Specifically, ",
            "In one case, ",
        ],
        "conclusion": [
            "Ultimately, ",
            "The outcome was ",
            "End result: ",
            "What it came down to: ",
        ],
    }

    def __init__(self, persona: ProfessionalPersona):
        self.persona = persona
        self.style_adapter = StyleAdapter(persona)
        self._response_count = 0

    def generate(self, context: ResponseContext) -> GeneratedResponse:
        """Generate a natural spoken response."""
        self._response_count += 1

        # Determine question type if not provided
        if not context.question_type:
            context.question_type = self._classify_question(context.question)

        # Select relevant experience
        experience = self._select_experience(context)

        # Build response components
        opening = self._generate_opening(context)
        core_answer = self._generate_core_answer(context, experience)
        elaboration = self._generate_elaboration(context, experience)
        closing = self._generate_closing(context)

        # Combine with natural flow
        response_text = self._assemble_response(opening, core_answer, elaboration, closing)

        # Apply persona style
        response_text = self.style_adapter.apply_style(response_text, context)

        # Estimate duration
        duration = self._estimate_duration(context, response_text)

        # Build reasoning trace
        reasoning = {
            "question_type": context.question_type,
            "interviewer_type": context.interviewer_type,
            "experience_used": experience.get("id", "none"),
            "persona_style": self.persona.communication_style,
            "mode": context.mode,
            "followup_depth": context.followup_depth,
        }

        return GeneratedResponse(
            text=response_text.strip(),
            reasoning_trace=reasoning,
            evidence_used=experience.get("evidence", []),
            numerical_entries_referenced=experience.get("numerical_refs", []),
            estimated_duration_seconds=duration,
        )

    def _classify_question(self, question: str) -> str:
        """Classify question type."""
        q_lower = question.lower()

        if any(kw in q_lower for kw in ["how many", "how much", "what percentage", "what was the", "give me a number"]):
            return "numerical"
        if any(kw in q_lower for kw in ["tell me about", "describe a time", "give an example", "walk me through"]):
            return "behavioral"
        if any(kw in q_lower for kw in ["how would you", "what would you do", "imagine", "suppose", "hypothetically"]):
            return "hypothetical"
        if any(kw in q_lower for kw in ["design", "architect", "scale", "system"]):
            return "system_design"
        if any(kw in q_lower for kw in ["debug", "troubleshoot", "incident", "outage", "failure", "root cause"]):
            return "troubleshooting"
        if any(kw in q_lower for kw in ["implement", "code", "build", "develop", "configuration", "setup"]):
            return "implementation"
        if any(kw in q_lower for kw in ["why", "reason", "decision", "choose", "tradeoff"]):
            return "reasoning"
        if any(kw in q_lower for kw in ["what is", "define", "explain", "difference between"]):
            return "technical_concept"
        return "factual"

    def _select_experience(self, context: ResponseContext) -> dict:
        """Select most relevant experience for the question."""
        # In production, this would query the experience story bank
        # For now, return the provided relevant_experience
        exp = context.relevant_experience.copy()
        if not exp.get("id"):
            exp["id"] = "scenario_default"
        return exp

    def _generate_opening(self, context: ResponseContext) -> str:
        """Generate natural opening."""
        # Skip opening for follow-ups at depth > 1
        if context.followup_depth > 1:
            return ""

        # Don't always use an opening - sometimes jump straight in
        if self._response_count > 3 and context.question_type in ["numerical", "narrow_technical_followup"]:
            return ""

        patterns = self.OPENING_PATTERNS.get(self.persona.communication_style, self.OPENING_PATTERNS["balanced"])
        # Vary based on response count
        idx = self._response_count % len(patterns)
        return patterns[idx]

    def _generate_core_answer(self, context: ResponseContext, experience: dict) -> str:
        """Generate the core answer to the question."""
        q_type = context.question_type

        if q_type == "numerical":
            return self._answer_numerical(context, experience)
        elif q_type == "behavioral":
            return self._answer_behavioral(context, experience)
        elif q_type == "implementation":
            return self._answer_implementation(context, experience)
        elif q_type == "troubleshooting":
            return self._answer_troubleshooting(context, experience)
        elif q_type == "system_design":
            return self._answer_system_design(context, experience)
        elif q_type == "hypothetical":
            return self._answer_hypothetical(context, experience)
        elif q_type == "technical_concept":
            return self._answer_technical_concept(context, experience)
        elif q_type == "reasoning":
            return self._answer_reasoning(context, experience)
        else:
            return self._answer_factual(context, experience)

    def _answer_numerical(self, context: ResponseContext, experience: dict) -> str:
        """Answer numerical question directly."""
        num_data = context.numerical_data
        if not num_data:
            return "I don't have that exact number offhand, but I can walk you through how we'd calculate it."

        # Direct answer first
        value = num_data.get("value")
        unit = num_data.get("unit", "")
        quantity = num_data.get("quantity", "it")

        if value is not None:
            answer = f"{quantity} was {value:,} {unit}".strip()
            # Add brief context if relevant
            if num_data.get("context"):
                answer += f". {num_data['context']}"
            return answer

        return "Let me think... the exact number escapes me, but it was in the ballpark of..."

    def _answer_behavioral(self, context: ResponseContext, experience: dict) -> str:
        """Answer behavioral question using implicit STAR."""
        situation = experience.get("situation", "In my previous role, we faced a situation where")
        task = experience.get("task", "I needed to")
        action = experience.get("action", "I")
        result = experience.get("result", "The outcome was")

        # Natural STAR without labels
        return f"{situation}. {task} {action}. {result}."

    def _answer_implementation(self, context: ResponseContext, experience: dict) -> str:
        """Answer implementation question with technical depth."""
        impl = experience.get("implementation", {})
        approach = impl.get("approach", "We built it using")
        key_decision = impl.get("key_decision", "The main decision was")
        detail = impl.get("detail", "")

        answer = f"{approach} {experience.get('technologies', ['the stack'])[0]}. {key_decision}."
        if detail:
            answer += f" {detail}"
        return answer

    def _answer_troubleshooting(self, context: ResponseContext, experience: dict) -> str:
        """Answer troubleshooting question with methodology."""
        steps = experience.get("troubleshooting_steps", [
            "First, I looked at the symptoms and business impact",
            "Then checked recent changes and deployments",
            "Narrowed down to the component",
            "Identified root cause",
            "Implemented fix and verified",
        ])

        return " ".join(steps) + "."

    def _answer_system_design(self, context: ResponseContext, experience: dict) -> str:
        """Answer system design question."""
        arch = experience.get("architecture", {})
        requirements = arch.get("requirements", "We needed to handle")
        pattern = arch.get("pattern", "We went with a")
        components = arch.get("components", "")

        return f"{requirements} at scale. {pattern} {components} architecture. Key tradeoffs were around consistency vs availability and operational complexity."

    def _answer_hypothetical(self, context: ResponseContext, experience: dict) -> str:
        """Answer hypothetical question with structured reasoning."""
        approach = "I'd start by understanding the constraints and objectives. "
        approach += "Then I'd identify the key variables and form hypotheses. "
        approach += "Prioritize by impact and feasibility. "
        approach += "Run a small experiment or calculation to validate. "
        approach += "Then iterate based on results."
        return approach

    def _answer_technical_concept(self, context: ResponseContext, experience: dict) -> str:
        """Answer technical concept question."""
        concept = experience.get("concept", "It's a")
        explanation = experience.get("explanation", "pattern where")
        return f"{concept} {explanation}. In practice, we used it for {experience.get('use_case', 'similar problems')}."

    def _answer_reasoning(self, context: ResponseContext, experience: dict) -> str:
        """Answer reasoning/decision question."""
        decision = experience.get("decision", "We chose")
        rationale = experience.get("rationale", "because")
        tradeoff = experience.get("tradeoff", "The tradeoff was")
        return f"{decision} {rationale}. {tradeoff}."

    def _answer_factual(self, context: ResponseContext, experience: dict) -> str:
        """Answer simple factual question."""
        fact = experience.get("fact", "Yes, that's correct.")
        return fact

    def _generate_elaboration(self, context: ResponseContext, experience: dict) -> str:
        """Generate elaboration if needed."""
        # Don't elaborate for simple questions or deep follow-ups
        if context.question_type in ["numerical", "simple_confirmation", "acknowledgment"]:
            return ""
        if context.followup_depth > 2:
            return ""

        # Add elaboration based on question type
        if context.question_type in ["implementation", "troubleshooting", "system_design"]:
            transitions = self.TRANSITION_PATTERNS["elaboration"]
            idx = hash(context.question) % len(transitions)
            return transitions[idx] + experience.get("elaboration", "the details mattered because of the scale we were operating at.")

        return ""

    def _generate_closing(self, context: ResponseContext) -> str:
        """Generate natural closing."""
        # Don't close every answer
        if context.question_type in ["numerical", "narrow_technical_followup"]:
            return ""

        # Vary closings
        closings = [
            "",
            "That was the main thing.",
            "That's how it played out.",
            "Made a real difference.",
            "Learned a lot from that one.",
        ]
        idx = (self._response_count + hash(context.question)) % len(closings)
        return closings[idx]

    def _assemble_response(self, opening: str, core: str, elaboration: str, closing: str) -> str:
        """Assemble response components naturally."""
        parts = []
        if opening:
            parts.append(opening)
        parts.append(core)
        if elaboration:
            parts.append(elaboration)
        if closing:
            parts.append(closing)

        # Join with natural spacing
        response = " ".join(parts)

        # Ensure proper sentence endings
        response = re.sub(r'\s+', ' ', response)
        response = response.strip()

        return response

    def _estimate_duration(self, context: ResponseContext, text: str) -> float:
        """Estimate speaking duration in seconds."""
        # Rough estimate: 150 words per minute = 2.5 words per second
        word_count = len(text.split())
        base_duration = word_count / 2.5

        # Apply guidelines
        guidelines = self.DURATION_GUIDELINES.get(context.question_type, (30, 90))
        min_dur, max_dur = guidelines

        # Clamp to guidelines
        return max(min_dur, min(max_dur, base_duration))


import re