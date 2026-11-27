"""Central Orchestration Layer — coordinates initialization, turn reasoning, validation, and memory."""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any

from .behavioral_reasoning import BehavioralReasoningEngine
from .business_reasoning import BusinessIntelligenceEngine
from .candidate_intelligence import CandidateIntelligenceEngine
from .communication_engine import HumanCommunicationEngine
from .config_loader import EngineConfig, find_package_root
from .employer_intelligence import EmployerIntelligenceEngine
from .evidence_classifier import EvidenceClassifier
from .experience_enrichment import ExperienceEnrichmentEngine
from .followup_pressure import FollowUpAndPressureHandler
from .importers import HistoricalInterviewImporter
from .improvement_engine import ContinuousImprovementEngine
from .interviewer_intelligence import InterviewerIntelligence
from .jd_analyzer import JobDescriptionAnalyzer
from .length_controller import DynamicLengthController
from .models import short_id, utc_now_iso
from .numerical_engine import NumericalEngine
from .numerical_ledger import NumericalLedger
from .scenario_modeling import ScenarioModelingEngine
from .schema_validator import assert_valid_schema
from .session_memory import SessionMemoryManager
from .technical_reasoning import TechnicalReasoningEngine
from .transcription_intelligence import TranscriptionIntelligence
from .validators import ResponseValidator
from .world_model import ProfessionalWorldModelBuilder


class HumanInterviewEngine:
    """Universal Human Candidate Cognitive Intelligence System orchestrator."""

    def __init__(
        self,
        root_dir: str | Path | None = None,
        memory_dir: str | Path | None = None,
    ) -> None:
        self.root_dir = find_package_root(Path(root_dir) if root_dir else None)
        self.config = EngineConfig(self.root_dir)
        mem_root = Path(memory_dir) if memory_dir else (self.root_dir / "memory")

        self.memory = SessionMemoryManager(mem_root)
        self.candidate_engine = CandidateIntelligenceEngine(self.config)
        self.employer_engine = EmployerIntelligenceEngine(self.config)
        self.world_model_builder = ProfessionalWorldModelBuilder(self.config, self.employer_engine)
        self.jd_analyzer = JobDescriptionAnalyzer(self.config, self.employer_engine)
        self.scenario_engine = ScenarioModelingEngine(self.config, self.employer_engine)
        self.enrichment_engine = ExperienceEnrichmentEngine()
        self.numerical_engine = NumericalEngine()
        self.transcription = TranscriptionIntelligence()
        self.interviewer = InterviewerIntelligence()
        self.length_controller = DynamicLengthController(self.config)
        self.communication = HumanCommunicationEngine(self.config)
        self.technical_reasoning = TechnicalReasoningEngine()
        self.behavioral_reasoning = BehavioralReasoningEngine()
        self.business_reasoning = BusinessIntelligenceEngine()
        self.followup_pressure = FollowUpAndPressureHandler(self.numerical_engine)
        self.validator = ResponseValidator(self.config, self.employer_engine, self.numerical_engine)
        self.importer = HistoricalInterviewImporter()
        self.improvement_engine = ContinuousImprovementEngine(self.config, self.employer_engine)

    def initialize_session(
        self,
        resume: str | dict[str, Any],
        job_description: str,
        operating_mode: str = "immersive_simulation",
        company_name: str | None = None,
        interviewer_type: str | None = None,
        candidate_notes: list[str] | None = None,
        communication_preferences: dict[str, Any] | None = None,
        candidate_id: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """Initialize candidate world model, JD analysis, scenario bank, ledgers, and wait for first question."""
        start_t = time.perf_counter()
        operating_mode = self.config.resolve_mode(operating_mode)
        if isinstance(resume, str) and not resume.strip():
            raise ValueError("Resume is empty: pass a resume file path or the resume text.")
        if not (job_description or "").strip():
            raise ValueError("Job description is empty: pass a job description file path or text.")

        profile = self.candidate_engine.parse_resume(
            resume_input=resume,
            candidate_notes=candidate_notes,
            candidate_id=candidate_id,
        )
        assert_valid_schema(profile, self.config.load_schema("candidate_profile"), "candidate_profile")

        jd_analysis = self.jd_analyzer.analyze(
            jd_text=job_description,
            profile=profile,
            company_override=company_name,
        )
        assert_valid_schema(jd_analysis, self.config.load_schema("jd_analysis"), "jd_analysis")

        world_model = self.world_model_builder.build(profile=profile, jd_analysis=jd_analysis)
        assert_valid_schema(world_model, self.config.load_schema("professional_world_model"), "professional_world_model")

        sid = session_id or short_id("sess")
        ledger = NumericalLedger(session_id=sid, candidate_id=profile["candidate_id"])
        evidence = EvidenceClassifier(candidate_id=profile["candidate_id"], session_id=sid)

        # Register documented resume items in evidence ledger
        for job in profile.get("career_chronology", []):
            evidence.add_item(
                claim=f"{job['role_title']} at {job['employer']} ({job['start_date']} - {job['end_date']})",
                category="documented_candidate_experience",
                source_reference="resume_chronology",
                confirmed_by_candidate=True,
            )
            for bullet in job.get("highlights", []):
                evidence.add_item(
                    claim=bullet,
                    category="documented_candidate_experience",
                    source_reference=f"resume:{job['employer']}",
                    confirmed_by_candidate=True,
                )

        for metric in profile.get("documented_metrics", []):
            evidence.add_item(
                claim=f"{metric['raw_text']} — {metric['context']}",
                category="verified_numerical_information",
                source_reference=f"resume:{metric['employer']}",
                confirmed_by_candidate=True,
            )

        project_catalog = self.scenario_engine.build_project_scenarios(
            profile=profile,
            world_model=world_model,
            jd_analysis=jd_analysis,
            ledger=ledger,
            operating_mode=operating_mode,
        )
        assert_valid_schema(project_catalog, self.config.load_schema("simulated_project"), "simulated_projects")
        assert_valid_schema(ledger.to_dict(), self.config.load_schema("numerical_ledger"), "numerical_ledger")

        for proj in project_catalog.get("projects", []):
            evidence.add_item(
                claim=f"Scenario '{proj['title']}' at {proj['employer']}: {proj['architecture_summary']}",
                category="fictional_simulation_scenario",
                source_reference=f"scenario:{proj['project_id']}",
                confirmed_by_candidate=False,
            )

        story_bank = self.enrichment_engine.build_story_bank(
            profile=profile,
            project_catalog=project_catalog,
            world_model=world_model,
        )
        assert_valid_schema(story_bank, self.config.load_schema("experience_story_bank"), "experience_story_bank")

        comm_prefs = {
            "candidate_id": profile["candidate_id"],
            "preferred_contractions": True,
            "target_wpm": 145,
            "verbosity_bias": "balanced",
            "banned_phrases": list(self.config.communication_rules.get("banned_ai_and_cliche_phrases", [])),
            "preferred_terminology": {},
            "learned_rules": [],
        }
        if communication_preferences:
            comm_prefs.update({k: v for k, v in communication_preferences.items() if v is not None})
        assert_valid_schema(comm_prefs, self.config.load_schema("communication_preferences"), "communication_preferences")
        assert_valid_schema(evidence.to_dict(), self.config.load_schema("evidence_classification"), "evidence_classification")

        self.memory.save_candidate_bundle(
            candidate_id=profile["candidate_id"],
            profile=profile,
            world_model=world_model,
            story_bank=story_bank,
            project_catalog=project_catalog,
            communication_preferences=comm_prefs,
        )

        projects = project_catalog.get("projects", [])
        active_project_id = projects[0]["project_id"] if projects else None

        session = self.memory.create_session(
            candidate_id=profile["candidate_id"],
            resume_version=profile["resume_version"],
            jd_analysis=jd_analysis,
            operating_mode=operating_mode,
            numerical_ledger=ledger.to_dict(),
            evidence_ledger=evidence.to_dict(),
            interviewer_context={"interviewer_type": interviewer_type} if interviewer_type else {},
            active_project_id=active_project_id,
            session_id=sid,
        )
        assert_valid_schema(session, self.config.load_schema("interview_session"), "interview_session")

        init_ms = round((time.perf_counter() - start_t) * 1000.0, 2)
        return {
            "status": "initialized_waiting_for_question",
            "session_id": sid,
            "candidate_id": profile["candidate_id"],
            "operating_mode": operating_mode,
            "inferred_seniority": world_model["inferred_seniority"],
            "active_project_id": active_project_id,
            "evidence_gaps_count": len(world_model["potential_gaps"]),
            "init_latency_ms": init_ms,
        }

    def process_turn(
        self,
        session_id: str,
        interviewer_input: str,
        interviewer_hint: str | None = None,
        mode_override: str | None = None,
    ) -> dict[str, Any]:
        """Process one interviewer turn, synthesize a validated response, and persist state."""
        start_t = time.perf_counter()
        bundle = self.memory.load_session_bundle(session_id)
        session = bundle["session"]
        profile = bundle["profile"]
        world_model = bundle["world_model"]
        jd_analysis = bundle["jd_analysis"]
        story_bank = bundle["story_bank"]
        projects = bundle["project_catalog"].get("projects", [])
        comm_prefs = bundle["communication_preferences"]

        ledger = NumericalLedger(
            session_id=session_id,
            candidate_id=profile["candidate_id"],
            entries=bundle["numerical_ledger"].get("entries", []),
            consistency_checks=bundle["numerical_ledger"].get("consistency_checks", []),
        )
        evidence = EvidenceClassifier(
            candidate_id=profile["candidate_id"],
            session_id=session_id,
            initial_items=bundle["evidence_ledger"].get("items", []),
        )

        if mode_override:
            mode_override = self.config.resolve_mode(mode_override)
            session["operating_mode"] = mode_override
        operating_mode = mode_override or session["operating_mode"]

        # Active project resolution (check if transcript names a specific employer)
        active_project = self._resolve_active_project(
            interviewer_input=interviewer_input,
            projects=projects,
            active_project_id=session.get("active_project_id"),
        )

        # Handle pending clarification continuation
        clarification_resolved = False
        effective_input = interviewer_input
        if session.get("clarification_pending", {}).get("active"):
            pending_pid = session["clarification_pending"].get("pending_project_id")
            if pending_pid and not any(
                any(tok in interviewer_input.lower() for tok in p["employer"].lower().split() if len(tok) >= 4)
                for p in projects
            ):
                active_project = next((p for p in projects if p["project_id"] == pending_pid), active_project)
            if active_project:
                session["active_project_id"] = active_project["project_id"]
            if len(interviewer_input.split()) <= 12 and "?" not in interviewer_input:
                emp_ctx = f" at {active_project['employer']}" if active_project else ""
                effective_input = f"Regarding {interviewer_input.strip()}{emp_ctx}: how did that work?"
            session["clarification_pending"] = {"active": False, "question_asked": None, "turn_index": None, "pending_project_id": None}
            clarification_resolved = True

        # Step 1: Speech & transcription cleanup
        trans_meta = self.transcription.interpret(
            raw_input=effective_input,
            active_project_id=session.get("active_project_id"),
            discussed_projects=session.get("discussed_projects", []),
            candidate_skills=profile.get("explicit_skills", []),
        )
        cleaned = trans_meta["cleaned_transcript"]

        # Step 2: Interviewer intent & precision analysis
        hint = interviewer_hint or session.get("interviewer_context", {}).get("interviewer_type")
        int_analysis = self.interviewer.analyze(
            cleaned_transcript=cleaned,
            transcription_meta=trans_meta,
            interviewer_hint=hint,
            operating_mode=operating_mode,
            previous_turns=session.get("turns", []),
        )

        # Step 3: Length budget & communication setup
        seniority_level = world_model.get("inferred_seniority", {}).get("level", "mid")
        budget = self.length_controller.determine_budget(
            interviewer_analysis=int_analysis,
            transcription_meta=trans_meta,
            operating_mode=operating_mode,
            seniority_level=seniority_level,
            verbosity_bias=comm_prefs.get("verbosity_bias", "balanced"),
        )
        opening_style = self.communication.select_opening_style(
            recent_openings=session.get("recent_openings", []),
            precision_targets=int_analysis.get("precision_targets", []),
            is_yes_no=int_analysis.get("is_yes_no_lead", False),
        )

        # Step 4: Route & synthesize response
        turn_index = len(session.get("turns", [])) + 1
        reasoning_result = self._route_and_reason(
            cleaned=cleaned,
            trans_meta=trans_meta,
            int_analysis=int_analysis,
            operating_mode=operating_mode,
            opening_style=opening_style,
            active_project=active_project,
            profile=profile,
            world_model=world_model,
            jd_analysis=jd_analysis,
            story_bank=story_bank,
            session=session,
            ledger=ledger,
            evidence=evidence,
        )

        raw_spoken = reasoning_result["spoken_draft"]
        if int_analysis.get("is_coaching_request") or operating_mode == "coaching_evaluation":
            final_response = raw_spoken
        else:
            final_response = self.communication.humanize_spoken_text(
                raw_text=raw_spoken,
                use_contractions=comm_prefs.get("preferred_contractions", True),
                banned_phrases=comm_prefs.get("banned_phrases", []),
                max_words=budget["max_words"],
            )

        # Step 5: Internal validation (plus one revision pass if stylistic repetition triggered)
        val_report = self.validator.validate(
            response_text=final_response,
            session=session,
            profile=profile,
            ledger=ledger,
            active_project=active_project,
            length_budget=budget,
            operating_mode=operating_mode,
            needs_clarification=trans_meta.get("needs_clarification", False),
            banned_extra=[r["rule_text"] for r in comm_prefs.get("learned_rules", []) if r.get("active")],
        )

        if any(i["code"] == "repetitive_opening" for i in val_report["issues"]) and operating_mode != "coaching_evaluation":
            # Shift opening slightly so consecutive turns never start identically
            final_response = self._vary_opening(final_response, turn_index)
            val_report = self.validator.validate(
                response_text=final_response,
                session=session,
                profile=profile,
                ledger=ledger,
                active_project=active_project,
                length_budget=budget,
                operating_mode=operating_mode,
                needs_clarification=trans_meta.get("needs_clarification", False),
            )

        # Step 6: Persist turn memory & story usage
        if trans_meta.get("needs_clarification") and not clarification_resolved:
            session["clarification_pending"] = {
                "active": True,
                "question_asked": final_response,
                "turn_index": turn_index,
                "pending_project_id": active_project["project_id"] if active_project else None,
            }

        if reasoning_result.get("project_used"):
            pid = reasoning_result["project_used"]
            session["active_project_id"] = pid
            if pid not in session["discussed_projects"]:
                session["discussed_projects"].append(pid)
            proj_obj = next((p for p in projects if p["project_id"] == pid), None)
            if proj_obj:
                if proj_obj["employer"] not in session["discussed_employers"]:
                    session["discussed_employers"].append(proj_obj["employer"])
                if proj_obj["architecture_summary"] not in session["discussed_architectures"]:
                    session["discussed_architectures"].append(proj_obj["architecture_summary"])
                for t in proj_obj.get("technology_stack", []):
                    session["discussed_tech_versions"][t["name"]] = t.get("version_or_era", "")

        if reasoning_result.get("story_used"):
            sid_used = reasoning_result["story_used"]
            if sid_used not in session["stories_used"]:
                session["stories_used"].append(sid_used)
            for st in story_bank.get("stories", []):
                if st["story_id"] == sid_used:
                    st["times_used"] = int(st.get("times_used", 0)) + 1
                    st["last_used_turn"] = turn_index

        if operating_mode != "coaching_evaluation":
            open_stem = self.communication.extract_opening_stem(final_response)
            close_stem = self.communication.extract_closing_stem(final_response)
            session.setdefault("recent_openings", []).append(open_stem)
            session["recent_openings"] = session["recent_openings"][-5:]
            session.setdefault("recent_closings", []).append(close_stem)
            session["recent_closings"] = session["recent_closings"][-5:]

        latency_ms = round((time.perf_counter() - start_t) * 1000.0, 2)
        turn_record = {
            "turn_index": turn_index,
            "raw_input": interviewer_input,
            "cleaned_transcript": cleaned,
            "transcription_repairs": trans_meta["repairs"],
            "interviewer_analysis": int_analysis,
            "length_budget": budget,
            "reasoning_meta": {
                "project_used": reasoning_result.get("project_used"),
                "story_used": reasoning_result.get("story_used"),
                "evidence_basis": reasoning_result.get("evidence_basis"),
            },
            "candidate_response": final_response,
            "validation_report": val_report,
            "latency_ms": latency_ms,
            "timestamp": utc_now_iso(),
        }
        session["turns"].append(turn_record)
        self.memory.compress_context_if_needed(
            session,
            turn_limit=int(self.config.defaults.get("memory", {}).get("context_window_turn_limit", 8)),
        )

        self.memory.save_session_state(
            session=session,
            numerical_ledger=ledger.to_dict(),
            evidence_ledger=evidence.to_dict(),
            story_bank=story_bank,
            communication_preferences=comm_prefs,
        )

        return {
            "session_id": session_id,
            "turn_index": turn_index,
            "response": final_response,
            "cleaned_transcript": cleaned,
            "transcription_repairs": trans_meta["repairs"],
            "interviewer_analysis": int_analysis,
            "length_budget": budget,
            "validation_report": val_report,
            "clarification_pending": session["clarification_pending"]["active"],
            "latency_ms": latency_ms,
        }

    def _resolve_active_project(
        self,
        interviewer_input: str,
        projects: list[dict[str, Any]],
        active_project_id: str | None,
    ) -> dict[str, Any] | None:
        low = (interviewer_input or "").lower()
        for proj in projects:
            emp_low = proj["employer"].lower()
            if emp_low in low or proj["title"].lower() in low:
                return proj
            if any(
                re.search(rf"\b{re.escape(tok)}\b", low)
                for tok in emp_low.split()
                if len(tok) >= 4
            ):
                return proj
        if active_project_id:
            for proj in projects:
                if proj["project_id"] == active_project_id:
                    return proj
        return projects[0] if projects else None

    def _route_and_reason(
        self,
        cleaned: str,
        trans_meta: dict[str, Any],
        int_analysis: dict[str, Any],
        operating_mode: str,
        opening_style: str,
        active_project: dict[str, Any] | None,
        profile: dict[str, Any],
        world_model: dict[str, Any],
        jd_analysis: dict[str, Any],
        story_bank: dict[str, Any],
        session: dict[str, Any],
        ledger: NumericalLedger,
        evidence: EvidenceClassifier,
    ) -> dict[str, Any]:
        # 0. Explicit coaching mode
        if int_analysis.get("is_coaching_request") or operating_mode == "coaching_evaluation":
            return self._build_coaching_response(cleaned, session, world_model, ledger, evidence)

        # 1. Non-question interviewer acknowledgment / monologue
        if trans_meta.get("is_non_question"):
            act = int_analysis.get("question_act")
            msg = "Sounds good, thanks for having me." if act == "closing" else "Got it."
            return {"spoken_draft": msg, "project_used": None, "evidence_basis": "general_technical_knowledge"}

        # 2. Material ambiguity or cut-off question -> Ask ONE concise clarifying question and wait
        if trans_meta.get("needs_clarification"):
            if trans_meta.get("clarification_reason") == "interrupted_transcript":
                q_text = "Sorry, you cut out right at the end there—which part did you want me to dig into?"
            else:
                q_text = "Which project did you want me to focus on—the primary platform work or an earlier role?"
            return {"spoken_draft": q_text, "project_used": None, "evidence_basis": "general_technical_knowledge"}

        # 3. Multi-part question -> address every meaningful sub-question cohesively
        sub_qs = trans_meta.get("sub_questions", [])
        if len(sub_qs) > 1:
            parts_spoken: list[str] = []
            proj_used = None
            story_used = None
            ev_basis = "general_technical_knowledge"
            for sq in sub_qs[:3]:
                sub_meta = self.transcription.interpret(sq, active_project_id=session.get("active_project_id"))
                sub_int = self.interviewer.analyze(sq, sub_meta, operating_mode=operating_mode, previous_turns=session.get("turns", []))
                sub_res = self._route_single_question(
                    cleaned=sq,
                    int_analysis=sub_int,
                    operating_mode=operating_mode,
                    opening_style=opening_style,
                    active_project=active_project,
                    profile=profile,
                    world_model=world_model,
                    jd_analysis=jd_analysis,
                    story_bank=story_bank,
                    session=session,
                    ledger=ledger,
                )
                parts_spoken.append(sub_res["spoken_draft"])
                proj_used = proj_used or sub_res.get("project_used")
                story_used = story_used or sub_res.get("story_used")
                ev_basis = sub_res.get("evidence_basis", ev_basis)
            return {
                "spoken_draft": " ".join(parts_spoken),
                "project_used": proj_used,
                "story_used": story_used,
                "evidence_basis": ev_basis,
            }

        return self._route_single_question(
            cleaned=cleaned,
            int_analysis=int_analysis,
            operating_mode=operating_mode,
            opening_style=opening_style,
            active_project=active_project,
            profile=profile,
            world_model=world_model,
            jd_analysis=jd_analysis,
            story_bank=story_bank,
            session=session,
            ledger=ledger,
        )

    def _route_single_question(
        self,
        cleaned: str,
        int_analysis: dict[str, Any],
        operating_mode: str,
        opening_style: str,
        active_project: dict[str, Any] | None,
        profile: dict[str, Any],
        world_model: dict[str, Any],
        jd_analysis: dict[str, Any],
        story_bank: dict[str, Any],
        session: dict[str, Any],
        ledger: NumericalLedger,
    ) -> dict[str, Any]:
        act = int_analysis.get("question_act", "new_question")
        itype = int_analysis.get("interviewer_type", "hiring_manager")
        precision = int_analysis.get("precision_targets", [])
        low = cleaned.lower()

        if act in ("challenge", "correction"):
            return self.followup_pressure.handle_pressure_or_correction(
                question=cleaned,
                question_act=act,
                project=active_project,
                previous_turns=session.get("turns", []),
                ledger=ledger,
            )

        if act == "numerical_probe":
            return self.followup_pressure.handle_numerical_probe(
                question=cleaned,
                ledger=ledger,
                project_id=active_project["project_id"] if active_project else None,
                operating_mode=operating_mode,
                profile=profile,
                world_model=world_model,
            )

        if act == "hypothetical_gca" or operating_mode == "general_cognitive_ability":
            return self.behavioral_reasoning.reason_hypothetical_gca(cleaned, world_model, jd_analysis)

        if act == "system_design_prompt" or (operating_mode == "system_design" and any(k in low for k in ("design", "architect", "scale"))):
            return self.technical_reasoning.reason_system_design(cleaned, world_model, jd_analysis)

        if act == "troubleshooting_probe" or any(k in low for k in ("outage", "incident", "debug", "troubleshoot")):
            return self.technical_reasoning.reason_troubleshooting(cleaned, active_project, operating_mode)

        if act == "behavioral_prompt" or (operating_mode == "behavioral" and act == "new_question"):
            return self.behavioral_reasoning.reason_behavioral(
                question=cleaned,
                story_bank=story_bank,
                stories_used=session.get("stories_used", []),
                operating_mode=operating_mode,
                opening_style=opening_style,
                precision_targets=precision,
            )

        if itype == "recruiter" or any(k in low for k in ("tell me about yourself", "introduce yourself", "walk me through your background", "why this role")):
            return self.business_reasoning.reason_recruiter(cleaned, profile, world_model, jd_analysis)

        if itype == "executive" or operating_mode == "executive" or (
            any(k in low for k in ("business impact", "roi", "executive", "customer trust", "renewal"))
            and "config" not in low
            and "implement" not in low
        ):
            return self.business_reasoning.reason_business_or_executive(
                cleaned, active_project, world_model, jd_analysis, operating_mode
            )

        # Yes/No lead question handling
        result = self.technical_reasoning.reason_implementation(
            question=cleaned,
            project=active_project,
            world_model=world_model,
            jd_analysis=jd_analysis,
            operating_mode=operating_mode,
            opening_style=opening_style,
            precision_targets=precision,
        )
        if int_analysis.get("is_yes_no_lead") and not result["spoken_draft"].lower().startswith(("yes", "no", "not ", "i haven't")):
            draft = result["spoken_draft"]
            lead_fixed = draft if draft.startswith("I ") else (draft[0].lower() + draft[1:])
            result["spoken_draft"] = "Yes, " + lead_fixed
        return result

    @staticmethod
    def _vary_opening(text: str, turn_index: int) -> str:
        prefixes = ["On that point, ", "Looking closely at it, ", "From a practical standpoint, ", "In practice, "]
        chosen = prefixes[turn_index % len(prefixes)]
        stripped = text.strip()
        if not stripped:
            return text
        return chosen + stripped[0].lower() + stripped[1:]

    @staticmethod
    def _build_coaching_response(
        cleaned: str,
        session: dict[str, Any],
        world_model: dict[str, Any],
        ledger: NumericalLedger,
        evidence: EvidenceClassifier,
    ) -> dict[str, Any]:
        gaps = [g["gap_area"] for g in world_model.get("potential_gaps", [])]
        checks = ledger.validate_all()
        failed_checks = [c["details"] for c in checks if not c["passed"]]
        unconfirmed = len(evidence.get_by_category("fictional_simulation_scenario"))
        turns = session.get("turns", [])
        last_turn_note = (
            f"Last turn ({turns[-1]['turn_index']}) length: {turns[-1]['validation_report']['word_count']} words, "
            f"validation passed={turns[-1]['validation_report']['passed']}."
            if turns
            else "No spoken turns recorded yet."
        )
        coaching_text = (
            f"Coaching Assessment:\n"
            f"- Request analyzed: {cleaned}\n"
            f"- Seniority calibration: {world_model['inferred_seniority']['level']} ({world_model['inferred_seniority']['rationale']})\n"
            f"- Evidence status: {unconfirmed} simulated scenario item(s) remain isolated from verified resume history; "
            f"confirm real numbers/experiences via `confirm` before using them in Authentic Preparation mode.\n"
            f"- Numerical ledger status: {len(checks)} consistency check(s), {len(failed_checks)} failure(s).\n"
            f"- Experience gaps to prepare honest bridges for: {', '.join(gaps) if gaps else 'None flagged'}.\n"
            f"- Session health: {last_turn_note}"
        )
        return {
            "spoken_draft": coaching_text,
            "project_used": None,
            "evidence_basis": "general_technical_knowledge",
        }

    def confirm_candidate_detail(
        self,
        session_id: str,
        claim: str,
        metric_name: str | None = None,
        metric_value: float | None = None,
        metric_unit: str | None = None,
    ) -> dict[str, Any]:
        """Explicitly confirm real candidate experience or verified numerical metrics (never auto-promoted)."""
        bundle = self.memory.load_session_bundle(session_id)
        session = bundle["session"]
        evidence = EvidenceClassifier(
            candidate_id=session["candidate_id"],
            session_id=session_id,
            initial_items=bundle["evidence_ledger"].get("items", []),
        )
        ev_item = evidence.add_item(
            claim=claim,
            category="verified_numerical_information" if metric_value is not None else "candidate_confirmed_experience",
            source_reference="explicit_candidate_confirmation",
            confirmed_by_candidate=True,
        )

        ledger = NumericalLedger(
            session_id=session_id,
            candidate_id=session["candidate_id"],
            entries=bundle["numerical_ledger"].get("entries", []),
            consistency_checks=bundle["numerical_ledger"].get("consistency_checks", []),
        )
        if metric_name and metric_value is not None:
            # Replace or insert verified metric
            ledger.entries = [e for e in ledger.entries if e["metric_name"] != metric_name]
            ledger.record_metric(
                project_id=session.get("active_project_id") or "confirmed",
                metric_name=metric_name,
                original_value=metric_value,
                unit=metric_unit or "units",
                scope=claim,
                measurement_period="candidate-confirmed",
                measurement_methodology="Directly confirmed by candidate.",
                evidence_status="verified_numerical_information",
            )

        self.memory.save_session_state(
            session=session,
            numerical_ledger=ledger.to_dict(),
            evidence_ledger=evidence.to_dict(),
        )
        return {"confirmed_evidence": ev_item, "ledger_entries": len(ledger.entries)}
