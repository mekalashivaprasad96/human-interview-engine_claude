"""Speech & Transcription Intelligence — cleans ASR artifacts, detects multi-questions & cutoffs."""

from __future__ import annotations

import re
from typing import Any


_PHONETIC_REPAIRS: tuple[tuple[str, str], ...] = (
    (r"\bcube\s+control\b", "kubectl"),
    (r"\bcube\s*ctl\b", "kubectl"),
    (r"\bkube\s+control\b", "kubectl"),
    (r"\bkuberneties\b", "Kubernetes"),
    (r"\bkuber\s*net\s*ease\b", "Kubernetes"),
    (r"\bkube\s*net\s*ease\b", "Kubernetes"),
    (r"\bk8\s+s\b", "Kubernetes"),
    (r"\btera\s*form\b", "Terraform"),
    (r"\bpie\s*torch\b", "PyTorch"),
    (r"\btensor\s+flow\b", "TensorFlow"),
    (r"\bpost\s*gress(?:\s*q\s*l)?\b", "PostgreSQL"),
    (r"\bred\s+is\b", "Redis"),
    (r"\bkaafka\b", "Kafka"),
    (r"\bcafka\b", "Kafka"),
    (r"\bopen\s+telemetry\b", "OpenTelemetry"),
    (r"\bo\s+tel\b", "OTel"),
    (r"\bg\s*r\s*p\s*c\b", "gRPC"),
    (r"\bv\s*l\s*l\s*m\b", "vLLM"),
    (r"\bcudda\b", "CUDA"),
    (r"\bkuda\b", "CUDA"),
    (r"\bsee\s+eye\s+see\s+dee\b", "CI/CD"),
    (r"\bpee\s+ninety\s+nine\b", "p99"),
    (r"\bp\s+ninety\s+nine\b", "p99"),
    (r"\bs\s*l\s*o\b", "SLO"),
    (r"\bs\s*l\s*a\b", "SLA"),
    (r"\be\s*k\s*s\b", "EKS"),
    (r"\bg\s*k\s*e\b", "GKE"),
    (r"\ba\s*w\s*s\b", "AWS"),
    (r"\bhippa\b", "HIPAA"),
    (r"\bo\s+auth\b", "OAuth"),
    (r"\bj\s*w\s*t\b", "JWT"),
    (r"\bb\s*g\s*p\b", "BGP"),
    (r"\bt\s*l\s*s\b", "TLS"),
    (r"\bu\s*v\s*m\b", "UVM"),
    (r"\br\s*t\s*l\b", "RTL"),
)

_NON_QUESTION_ACK_RE = re.compile(
    r"^(?:ok|okay|got it|makes sense|thank you|thanks|interesting|noted|alright|cool|great|right|sure|understood|let me note that|let me pull up my next note)"
    r"(?:[\s,.\-!]+(?:thanks|thank you|got it|that makes sense|makes sense|noted|for walking through that|for sharing that|let me pull up my next note|one second))*[.\s!]*$",
    re.IGNORECASE,
)


class TranscriptionIntelligence:
    """Interprets raw text or noisy speech-to-text transcripts into clean conversational turns."""

    def interpret(
        self,
        raw_input: str,
        active_project_id: str | None = None,
        discussed_projects: list[str] | None = None,
        candidate_skills: list[str] | None = None,
    ) -> dict[str, Any]:
        """Repair phonetic ASR errors, split sub-questions, and detect cutoffs/non-questions."""
        text = (raw_input or "").strip()
        repairs: list[dict[str, str]] = []
        cleaned = text

        # 1. Remove verbal fillers (um, uh, er) while keeping sentence cadence
        cleaned_no_fillers = re.sub(r"\b(?:uh+|um+|er+|ah+)\b[, ]*", "", cleaned, flags=re.IGNORECASE)
        if cleaned_no_fillers != cleaned:
            repairs.append({"type": "filler_removal", "detail": "Removed verbal hesitation markers"})
            cleaned = cleaned_no_fillers

        # 2. Collapse consecutive duplicated stutter words ("the the", "how how")
        deduped = re.sub(r"\b([a-zA-Z]+)\s+\1\b", r"\1", cleaned, flags=re.IGNORECASE)
        if deduped != cleaned:
            repairs.append({"type": "stutter_collapse", "detail": "Collapsed repeated consecutive words"})
            cleaned = deduped

        # 3. Phonetic domain term normalization
        for pattern, replacement in _PHONETIC_REPAIRS:
            new_cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
            if new_cleaned != cleaned:
                repairs.append({"type": "phonetic_repair", "detail": f"Normalized ASR term to '{replacement}'"})
                cleaned = new_cleaned

        # Context-aware ASR repair: "notes" -> "nodes" when talking about GPUs, clusters, servers, instances
        if re.search(r"\b(?:gpu|gpus|cluster|server|contain|large|ec2|instance|host)\b", cleaned, re.IGNORECASE):
            repaired_notes = re.sub(r"\bnotes\b", "nodes", cleaned, flags=re.IGNORECASE)
            if repaired_notes != cleaned:
                repairs.append({"type": "phonetic_repair", "detail": "Normalized ASR term 'notes' to 'nodes' in compute/GPU context"})
                cleaned = repaired_notes

        cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()

        # 4. Detect interrupted / truncated fragments or material ambiguity before non-question checks
        is_incomplete = self._detect_incomplete(cleaned)
        material_ambiguity = self._detect_material_ambiguity(cleaned, active_project_id, discussed_projects or [])

        # 5. Detect non-question statements / interviewer acknowledgments
        is_non_question = (not is_incomplete and not material_ambiguity) and (
            bool(_NON_QUESTION_ACK_RE.match(cleaned))
            or (
                "?" not in cleaned
                and len(cleaned.split()) <= 10
                and not re.match(r"^(?:tell|walk|explain|describe|how|what|why|when|which|where|who|can|could|would|did|do|are|is|was|were|have)\b", cleaned, re.IGNORECASE)
            )
        )

        # 6. Split multi-part questions
        sub_questions = self._split_questions(cleaned) if not is_non_question else []

        return {
            "raw_input": raw_input,
            "cleaned_transcript": cleaned,
            "repairs": repairs,
            "is_non_question": is_non_question,
            "is_incomplete": is_incomplete,
            "material_ambiguity": material_ambiguity,
            "needs_clarification": bool(is_incomplete or material_ambiguity),
            "clarification_reason": (
                "interrupted_transcript" if is_incomplete else ("material_ambiguity" if material_ambiguity else None)
            ),
            "sub_questions": sub_questions,
        }

    @staticmethod
    def _detect_incomplete(cleaned: str) -> bool:
        if not cleaned:
            return True
        if cleaned.endswith(("—", "--", "...")):
            return True
        words = cleaned.lower().split()
        if len(words) >= 2 and words[-1] in {"the", "a", "an", "about", "when", "if", "with", "for", "of", "to", "that"}:
            return True
        return False

    @staticmethod
    def _detect_material_ambiguity(
        cleaned: str,
        active_project_id: str | None,
        discussed_projects: list[str],
    ) -> bool:
        low = cleaned.lower()
        # Only flag material ambiguity when pronoun reference is genuinely unresolvable
        ambiguous_markers = ("that other one", "the other project", "which one of those", "either of those")
        if any(m in low for m in ambiguous_markers) and len(discussed_projects) >= 2:
            return True
        if re.match(r"^(?:how|what)\s+(?:did|was)\s+(?:that|it)\??$", low) and not active_project_id:
            return True
        return False

    @staticmethod
    def _split_questions(cleaned: str) -> list[str]:
        # Split on '?' first, then look for compound ", and (how|what|why|when|which|did|do|can)"
        parts = [p.strip() for p in re.split(r"\?\s*", cleaned) if p.strip()]
        result: list[str] = []
        for idx, part in enumerate(parts):
            suffix = "?" if (idx < len(parts) - 1 or cleaned.endswith("?")) else ""
            sub = re.split(
                r",\s+and\s+(?=(?:how|what|why|when|which|who|did|do|was|were|could|would|can)\b)",
                part,
                flags=re.IGNORECASE,
            )
            if len(sub) > 1:
                for s_idx, s in enumerate(sub):
                    s_clean = s.strip().rstrip("?.") + "?"
                    result.append(s_clean)
            else:
                result.append(part + suffix if suffix and not part.endswith("?") else part)
        return result or [cleaned]
