"""Continuous Improvement Engine — analyzes historical failures, generates regression tests, and updates rules."""

from __future__ import annotations

import re
from typing import Any

from .config_loader import EngineConfig
from .employer_intelligence import EmployerIntelligenceEngine
from .models import SHORTCOMING_CATEGORIES, short_id, utc_now_iso, word_count


class ContinuousImprovementEngine:
    """Diagnoses transcript weaknesses, creates regression test cases, and applies validated rule updates."""

    def __init__(self, config: EngineConfig, employer_engine: EmployerIntelligenceEngine) -> None:
        self.config = config
        self.employer_engine = employer_engine
        self.rules = config.communication_rules

    def analyze_imported_history(
        self,
        imported_bundle: dict[str, Any],
        profile: dict[str, Any] | None = None,
        explicit_feedback: list[str] | None = None,
    ) -> dict[str, Any]:
        """Inspect imported conversations, separating direct transcript evidence from inferred weaknesses."""
        observed_evidence: list[dict[str, Any]] = []
        inferred_weaknesses: list[dict[str, Any]] = []
        category_counts: dict[str, int] = {}

        def record(category: str, turn_idx: int, quote: str, detail: str, observed: bool = True) -> None:
            if category not in SHORTCOMING_CATEGORIES:
                return
            category_counts[category] = category_counts.get(category, 0) + 1
            entry = {
                "category": category,
                "turn_index": turn_idx,
                "evidence_quote": quote[:200],
                "detail": detail,
            }
            if observed:
                observed_evidence.append(entry)
            else:
                inferred_weaknesses.append(entry)

        banned = list(self.rules.get("banned_ai_and_cliche_phrases", []))
        star_markers = ["situation:", "task:", "action:", "result:"]

        for conv in imported_bundle.get("conversations", []):
            seen_openings: list[str] = []
            seen_story_stems: list[str] = []

            for turn in conv.get("turns", []):
                t_idx = turn.get("turn_index", 0)
                q = turn.get("question", "")
                a = turn.get("answer", "")
                q_low = q.lower()
                a_low = a.lower()

                if not a:
                    continue

                # 1. Breaking character / referencing resume or internal scenario labels
                for leak in (
                    "based on the resume",
                    "based on your resume",
                    "not mentioned in your resume",
                    "as an ai",
                    "provided documents",
                    "the question doesn't specify",
                    "the interview scenario",
                    "verified node count",
                    "i'd answer in your voice",
                ):
                    if leak in a_low:
                        record("breaking_character_resume_reference", t_idx, a, f"Observed phrase '{leak}'.", observed=True)

                stripped_a = a.strip()
                if (stripped_a.startswith('"') and stripped_a.endswith('"')) or (
                    stripped_a.startswith("“") and stripped_a.endswith("”")
                ):
                    record("breaking_character_resume_reference", t_idx, a, "Wrapped spoken answer in outer quotation marks.", observed=True)

                # 2. Robotic communication / clichés / STAR labels
                if any(m in a_low for m in star_markers) or any(p in a_low for p in banned):
                    record("robotic_communication", t_idx, a, "Observed STAR headings or scripted AI clichés.", observed=True)

                # 3. Excessive length
                wc = word_count(a)
                if wc > 280 or (any(k in q_low for k in ("how many", "yes or no", "did you")) and wc > 120):
                    record("excessive_length", t_idx, a, f"Response length {wc} words exceeds expected spoken cadence.", observed=True)

                # 4. Insufficient depth on implementation probes
                if any(k in q_low for k in ("how did you implement", "walk me through the config", "exact configuration")) and wc < 35:
                    record("insufficient_depth", t_idx, a, f"Implementation probe answered in only {wc} words.", observed=True)

                # 5. Missing numbers on quantitative questions
                if any(k in q_low for k in ("how many", "how much", "what percentage", "how fast", "latency")) and not re.search(r"\d", a):
                    record("missing_numbers", t_idx, a, "Quantitative prompt answered without any concrete numeric value.", observed=True)

                # 6. Weak individual ownership
                if "what did you personally" in q_low and " i " not in f" {a_low} " and "we " in f" {a_low} ":
                    record("weak_individual_ownership", t_idx, a, "Ownership probe answered solely with collective 'we'.", observed=True)

                # 7. Excessive agreement with incorrect premise
                if any(k in q_low for k in ("hypervisor", "tcp guarantee duplicate", "isn't that")) and a_low.startswith(("yes", "absolutely", "you're right")):
                    record("excessive_agreement", t_idx, a, "Agreed with challenged or potentially incorrect interviewer premise.", observed=True)

                # 8. Failure to wait after asking clarifying question
                if "?" in a and len(a.split("?")[1].strip().split()) > 25:
                    record("failure_to_wait_for_clarification", t_idx, a, "Asked a clarifying question and immediately answered it.", observed=True)

                # 9. Repetitive openings / repeated stories
                open_stem = " ".join(a_low.split()[:4])
                if open_stem in seen_openings and len(a.split()) > 15:
                    record("robotic_communication", t_idx, a, "Repeated exact opening phrasing from a prior turn.", observed=True)
                seen_openings.append(open_stem)

                story_sig = " ".join(sorted(set(re.findall(r"\b[a-z]{6,}\b", a_low)))[:6])
                if story_sig and story_sig in seen_story_stems and "tell me about a time" in q_low:
                    record("repeated_stories", t_idx, a, "Likely recycled the same behavioral story.", observed=False)
                if "tell me about a time" in q_low:
                    seen_story_stems.append(story_sig)

                # 10. Unnatural conclusions
                if any(a_low.rstrip(".!").endswith(end) for end in ("that's how i approach these situations", "in conclusion", "hope that answers your question")):
                    record("unnatural_conclusions", t_idx, a, "Used formulaic closing cliché.", observed=True)

                # 11. Technology timeline check if profile chronology provided
                if profile and profile.get("career_chronology"):
                    earliest_yr = min((j.get("start_year") or 2020) for j in profile["career_chronology"])
                    latest_yr = max((j.get("end_year") or 2026) for j in profile["career_chronology"])
                    for tech in self.employer_engine.detect_technologies_in_text(a):
                        meta = self.config.technology_timeline.get(tech)
                        if meta and int(meta["introduced_year"]) > latest_yr:
                            record("technology_timeline_errors", t_idx, a, f"Mentioned {tech} ({meta['introduced_year']}) beyond career window {latest_yr}.", observed=True)

                # 12. Inferred business impact / textbook gap
                if wc > 60 and "cost" not in a_low and "customer" not in a_low and "impact" not in a_low and "availability" not in a_low:
                    record("missing_business_impact", t_idx, a, "Technical answer omits explicit business or customer consequence.", observed=False)

        # Process explicit user corrections / feedback
        for fb in explicit_feedback or []:
            fb_low = fb.lower()
            if "natural" in fb_low or "human" in fb_low or "robotic" in fb_low:
                record("robotic_communication", 0, fb, "User requested more natural, human communication.", observed=True)
            if "too long" in fb_low or "shorter" in fb_low or "concise" in fb_low:
                record("excessive_length", 0, fb, "User requested tighter, more concise answers.", observed=True)
            if "ownership" in fb_low or "personally" in fb_low:
                record("weak_individual_ownership", 0, fb, "User requested clearer personal ownership.", observed=True)
            if "number" in fb_low or "consistent" in fb_low:
                record("follow_up_contradictions", 0, fb, "User flagged numerical or follow-up consistency issue.", observed=True)

        regression_cases = self._generate_regression_cases(observed_evidence + inferred_weaknesses)
        proposed_rules = self._propose_durable_rules(category_counts, explicit_feedback or [])

        return {
            "import_id": imported_bundle.get("import_id"),
            "observed_transcript_evidence": observed_evidence,
            "inferred_weaknesses": inferred_weaknesses,
            "category_counts": category_counts,
            "generated_regression_cases": regression_cases,
            "proposed_rules": proposed_rules,
        }

    @staticmethod
    def _generate_regression_cases(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        cases: list[dict[str, Any]] = []
        seen_cats: set[str] = set()
        for item in findings:
            cat = item["category"]
            if cat in seen_cats:
                continue
            seen_cats.add(cat)
            cases.append(
                {
                    "regression_id": short_id("reg", cat),
                    "failure_category": cat,
                    "source_evidence": item["evidence_quote"],
                    "assertion": f"Engine response must avoid '{cat}' ({item['detail']}).",
                }
            )
        return cases

    @staticmethod
    def _propose_durable_rules(category_counts: dict[str, int], explicit_feedback: list[str]) -> list[dict[str, Any]]:
        rule_templates = {
            "robotic_communication": "Use varied natural openings and contractions; ban STAR headers and corporate clichés.",
            "excessive_length": "Enforce dynamic spoken word budgets; stop immediately once the exact question is answered.",
            "weak_individual_ownership": "State personal 'I' contributions before mentioning collective team support.",
            "missing_numbers": "Provide established or explicitly calculated ledger figures directly on quantitative prompts.",
            "breaking_character_resume_reference": "Never reference uploaded documents, resumes, or AI constraints in spoken simulation.",
            "excessive_agreement": "Challenge false technical or mathematical premises calmly instead of agreeing.",
            "failure_to_wait_for_clarification": "When asking a clarifying question, stop and wait for the interviewer reply.",
            "repeated_stories": "Rotate stories across employers and exclude previously used story IDs.",
            "unnatural_conclusions": "End cleanly on outcome or lesson without summary clichés.",
            "follow_up_contradictions": "Validate every number and component against NumericalLedger and active SimulatedProject.",
        }
        rules: list[dict[str, Any]] = []
        for cat, count in category_counts.items():
            if cat in rule_templates:
                rules.append(
                    {
                        "rule_id": short_id("rule", f"{cat}:{count}"),
                        "category": cat,
                        "rule_text": rule_templates[cat],
                        "source": "historical_analysis_and_feedback",
                        "created_at": utc_now_iso(),
                        "active": True,
                    }
                )
        for fb in explicit_feedback:
            if not any(fb.lower() in r["rule_text"].lower() for r in rules):
                rules.append(
                    {
                        "rule_id": short_id("rule", fb),
                        "category": "explicit_user_preference",
                        "rule_text": fb.strip(),
                        "source": "user_correction",
                        "created_at": utc_now_iso(),
                        "active": True,
                    }
                )
        return rules

    @staticmethod
    def apply_validated_rules(
        comm_prefs: dict[str, Any],
        proposed_rules: list[dict[str, Any]],
        baseline_score: float,
        candidate_score: float,
    ) -> dict[str, Any]:
        """Persist proposed rules ONLY if validation score improves or stays at parity without regression."""
        if candidate_score < baseline_score:
            return {
                "applied": False,
                "reason": f"Candidate regression score ({candidate_score}) regressed below baseline ({baseline_score}).",
                "rules_added": 0,
            }
        existing_texts = {r["rule_text"].lower() for r in comm_prefs.get("learned_rules", [])}
        added = 0
        for rule in proposed_rules:
            if rule["rule_text"].lower() not in existing_texts:
                comm_prefs.setdefault("learned_rules", []).append(rule)
                existing_texts.add(rule["rule_text"].lower())
                added += 1
            if rule["category"] == "excessive_length":
                comm_prefs["verbosity_bias"] = "concise"
        return {
            "applied": True,
            "baseline_score": baseline_score,
            "candidate_score": candidate_score,
            "rules_added": added,
        }
