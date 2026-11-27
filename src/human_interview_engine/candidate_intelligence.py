"""Candidate Intelligence Engine — parses resumes and builds CandidateProfile."""

from __future__ import annotations

import json
import re
from typing import Any

from .config_loader import EngineConfig
from .models import current_year_utc, short_id, slugify, utc_now_iso

_DATE_RANGE_RE = re.compile(
    r"(?P<start>(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\d{1,2}/\d{4}|\b(?:19|20)\d{2}\b)"
    r"\s*(?:-|–|—|to)\s*"
    r"(?P<end>Present|Current|Now|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\d{1,2}/\d{4}|\b(?:19|20)\d{2}\b)",
    re.IGNORECASE,
)

_YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")

_METRIC_RE = re.compile(
    r"(?P<value>\$?\d[\d,]*(?:\.\d+)?)\s*(?P<unit>%|percent|ms|s|sec|seconds|minutes|hrs|hours|gpus?|nodes?|servers?|clusters?|rps|qps|tps|tb|gb|mb|pb|k|m|b|x|users?|customers?|engineers?|teams?|incidents?|tickets?)?",
    re.IGNORECASE,
)

_SECTION_HEADERS = {
    "experience": {"experience", "work experience", "employment", "employment history", "career history", "professional experience"},
    "skills": {"skills", "technical skills", "core competencies", "technologies", "tools", "tech stack"},
    "education": {"education", "academic background", "degrees"},
    "certifications": {"certifications", "certificates", "licenses"},
    "summary": {"summary", "profile", "about", "objective"},
    "projects": {"projects", "selected projects", "key projects"},
}


def _extract_year(text: str, is_end: bool = False) -> int | None:
    low = (text or "").strip().lower()
    if is_end and low in {"present", "current", "now"}:
        return current_year_utc()
    m = _YEAR_RE.search(text or "")
    return int(m.group(1)) if m else None


def _estimate_duration_months(start_text: str, end_text: str) -> int | None:
    sy = _extract_year(start_text, is_end=False)
    ey = _extract_year(end_text, is_end=True)
    if sy is None or ey is None:
        return None
    months = max(1, (ey - sy) * 12)
    return months


def _detect_section(line: str) -> str | None:
    clean = re.sub(r"^[#*\-\s]+|[:\s]+$", "", line.strip().lower())
    for sec, aliases in _SECTION_HEADERS.items():
        if clean in aliases:
            return sec
    return None


def _split_role_and_employer(header_text: str) -> tuple[str, str]:
    text = _DATE_RANGE_RE.sub("", header_text).strip(" |-–—,()\t")
    # Common formats: "Role at Employer", "Role | Employer", "Employer — Role", "Employer - Role"
    if " at " in text.lower():
        parts = re.split(r"\s+at\s+", text, maxsplit=1, flags=re.IGNORECASE)
        return parts[0].strip(), parts[1].strip()
    for sep in (" | ", " — ", " – ", " - ", ", "):
        if sep in text:
            left, right = [p.strip() for p in text.split(sep, 1)]
            # Heuristic: job title tokens usually sit on one side
            role_hints = ("engineer", "architect", "manager", "director", "lead", "developer", "analyst", "specialist", "consultant", "vp", "officer", "scientist", "administrator", "tam")
            if any(h in left.lower() for h in role_hints) and not any(h in right.lower() for h in role_hints):
                return left, right
            if any(h in right.lower() for h in role_hints) and not any(h in left.lower() for h in role_hints):
                return right, left
            return left, right
    return text or "Engineer", "Confidential Employer"


class CandidateIntelligenceEngine:
    """Extracts structured candidate profiles from raw text, markdown, or JSON resumes."""

    def __init__(self, config: EngineConfig) -> None:
        self.config = config
        self._known_tech_aliases = self._build_tech_alias_map()

    def _build_tech_alias_map(self) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for canonical, meta in self.config.technology_timeline.items():
            mapping[canonical.lower()] = canonical
            for alias in meta.get("aliases", []):
                mapping[alias.lower()] = canonical
        # Additional broad professional & engineering keywords
        for extra in (
            "linux", "networking", "tcp/ip", "bgp", "dns", "tls", "iam", "rbac", "oauth", "oidc",
            "ci/cd", "jenkins", "gitlab", "sql", "nosql", "microservices", "distributed systems",
            "system design", "incident management", "sre", "observability", "slo", "sla",
            "product management", "roadmap", "stakeholder management", "account management",
            "rtl", "verilog", "systemverilog", "uvm", "fpga", "asic", "silicon validation",
            "ios", "android", "mobile", "rest", "api", "llm", "rag", "fine-tuning", "gpu",
        ):
            mapping[extra] = extra
        return mapping

    def parse_resume(
        self,
        resume_input: str | dict[str, Any],
        candidate_notes: list[str] | None = None,
        candidate_id: str | None = None,
    ) -> dict[str, Any]:
        """Parse a resume (dict, JSON string, or plain/markdown text) into CandidateProfile."""
        if isinstance(resume_input, dict):
            return self._from_structured_dict(resume_input, candidate_notes, candidate_id)

        stripped = (resume_input or "").strip()
        if stripped.startswith("{"):
            try:
                parsed = json.loads(stripped)
                if isinstance(parsed, dict):
                    return self._from_structured_dict(parsed, candidate_notes, candidate_id)
            except json.JSONDecodeError:
                pass

        return self._from_text(stripped, candidate_notes or [], candidate_id)

    def _from_structured_dict(
        self,
        data: dict[str, Any],
        candidate_notes: list[str] | None,
        candidate_id: str | None,
    ) -> dict[str, Any]:
        name = (data.get("full_name") or data.get("name") or "Candidate").strip()
        cid = candidate_id or data.get("candidate_id") or f"{slugify(name, 'candidate')}-{short_id('c', name)[-4:]}"
        chronology = []
        for entry in data.get("career_chronology") or data.get("experience") or []:
            start_d = str(entry.get("start_date", ""))
            end_d = str(entry.get("end_date", ""))
            sy = entry.get("start_year") or _extract_year(start_d, False)
            ey = entry.get("end_year") or _extract_year(end_d, True)
            chronology.append(
                {
                    "employer": entry.get("employer") or entry.get("company") or "Employer",
                    "role_title": entry.get("role_title") or entry.get("title") or "Role",
                    "start_date": start_d,
                    "end_date": end_d,
                    "start_year": sy,
                    "end_year": ey,
                    "is_current": end_d.lower() in {"present", "current", "now"} or bool(entry.get("is_current")),
                    "duration_months": entry.get("duration_months") or _estimate_duration_months(start_d, end_d),
                    "industry": entry.get("industry", ""),
                    "domain_tags": list(entry.get("domain_tags", [])),
                    "highlights": list(entry.get("highlights") or entry.get("bullets") or []),
                }
            )
        skills = list(data.get("explicit_skills") or data.get("skills") or [])
        metrics = self._extract_metrics_from_chronology(chronology)
        if data.get("documented_metrics"):
            metrics = list(data["documented_metrics"])

        total_bullets = sum(len(item["highlights"]) for item in chronology)
        return {
            "candidate_id": cid,
            "full_name": name,
            "headline": data.get("headline", ""),
            "resume_version": data.get("resume_version") or short_id("rv", json.dumps(data, sort_keys=True)),
            "created_at": utc_now_iso(),
            "career_chronology": chronology,
            "education": [
                {
                    "institution": e.get("institution", ""),
                    "degree": e.get("degree", ""),
                    "field": e.get("field", ""),
                    "graduation_year": e.get("graduation_year"),
                    "evidence_status": "documented_candidate_experience",
                }
                for e in data.get("education", [])
            ],
            "certifications": [
                {
                    "name": c.get("name", c) if isinstance(c, dict) else str(c),
                    "issuer": c.get("issuer", "") if isinstance(c, dict) else "",
                    "year": c.get("year") if isinstance(c, dict) else None,
                    "evidence_status": "documented_candidate_experience",
                }
                for c in data.get("certifications", [])
            ],
            "explicit_skills": sorted({s.strip() for s in skills if str(s).strip()}),
            "documented_metrics": metrics,
            "candidate_notes": list(candidate_notes or data.get("candidate_notes") or []),
            "is_sparse_resume": (len(chronology) <= 1 and total_bullets <= 3) or total_bullets <= 4,
        }

    def _from_text(
        self,
        text: str,
        candidate_notes: list[str],
        candidate_id: str | None,
    ) -> dict[str, Any]:
        lines = [line.rstrip() for line in text.splitlines()]
        non_empty = [l.strip() for l in lines if l.strip()]

        full_name = "Candidate"
        headline = ""
        if non_empty:
            first = re.sub(r"^#+\s*", "", non_empty[0]).strip()
            if len(first.split()) <= 5 and not _DATE_RANGE_RE.search(first) and _detect_section(first) is None:
                full_name = first
                if len(non_empty) > 1 and _detect_section(non_empty[1]) is None and not _DATE_RANGE_RE.search(non_empty[1]):
                    second = re.sub(r"^#+\s*", "", non_empty[1]).strip()
                    if "@" not in second and "http" not in second.lower():
                        headline = second

        cid = candidate_id or f"{slugify(full_name, 'candidate')}-{short_id('c', text)[:6]}"

        current_section = "preamble"
        chronology: list[dict[str, Any]] = []
        education: list[dict[str, Any]] = []
        certifications: list[dict[str, Any]] = []
        explicit_skills: list[str] = []
        active_job: dict[str, Any] | None = None

        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                continue

            sec = _detect_section(line)
            if sec is not None:
                current_section = sec
                continue

            is_bullet = line.startswith(("-", "*", "•"))
            clean_line = re.sub(r"^[-*•]+\s*", "", line).strip()
            clean_heading = re.sub(r"^#+\s*", "", line).strip()

            if current_section in ("experience", "preamble", "projects"):
                date_match = _DATE_RANGE_RE.search(clean_heading)
                if date_match and not is_bullet:
                    start_s = date_match.group("start").strip()
                    end_s = date_match.group("end").strip()
                    role_title, employer = _split_role_and_employer(clean_heading)
                    active_job = {
                        "employer": employer,
                        "role_title": role_title,
                        "start_date": start_s,
                        "end_date": end_s,
                        "start_year": _extract_year(start_s, False),
                        "end_year": _extract_year(end_s, True),
                        "is_current": end_s.lower() in {"present", "current", "now"},
                        "duration_months": _estimate_duration_months(start_s, end_s),
                        "industry": "",
                        "domain_tags": [],
                        "highlights": [],
                    }
                    chronology.append(active_job)
                    continue

                if is_bullet and active_job is not None:
                    active_job["highlights"].append(clean_line)
                    continue

                if current_section == "experience" and active_job is not None and not is_bullet:
                    # Handle two-line headers where role is on line 1 and employer/date or vice versa
                    if len(clean_line.split()) <= 10 and not clean_line.endswith("."):
                        if active_job["employer"] == "Confidential Employer":
                            active_job["employer"] = clean_line
                        else:
                            active_job["highlights"].append(clean_line)
                    else:
                        active_job["highlights"].append(clean_line)

            elif current_section == "skills":
                parts = re.split(r"[,|;/•]+", re.sub(r"^[^:]+:\s*", "", clean_line))
                for part in parts:
                    token = part.strip(" .-")
                    if token and len(token) <= 45:
                        explicit_skills.append(token)

            elif current_section == "education":
                yr = _extract_year(clean_line, False)
                education.append(
                    {
                        "institution": clean_line,
                        "degree": clean_line,
                        "field": "",
                        "graduation_year": yr,
                        "evidence_status": "documented_candidate_experience",
                    }
                )

            elif current_section == "certifications":
                yr = _extract_year(clean_line, False)
                certifications.append(
                    {
                        "name": clean_line,
                        "issuer": "",
                        "year": yr,
                        "evidence_status": "documented_candidate_experience",
                    }
                )

        # Fallback: infer explicit skills from technology mentions across resume text
        text_lower = text.lower()
        for alias, canonical in self._known_tech_aliases.items():
            if re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])", text_lower):
                explicit_skills.append(canonical)

        # Preserve order while deduplicating case-insensitively
        dedup_skills: list[str] = []
        seen_skills: set[str] = set()
        for skill in explicit_skills:
            key = skill.lower()
            if key not in seen_skills:
                seen_skills.add(key)
                dedup_skills.append(skill)

        metrics = self._extract_metrics_from_chronology(chronology)
        total_bullets = sum(len(item["highlights"]) for item in chronology)
        is_sparse = (len(chronology) <= 1 and total_bullets <= 3) or total_bullets <= 4

        return {
            "candidate_id": cid,
            "full_name": full_name,
            "headline": headline,
            "resume_version": short_id("rv", text),
            "created_at": utc_now_iso(),
            "career_chronology": chronology,
            "education": education,
            "certifications": certifications,
            "explicit_skills": dedup_skills,
            "documented_metrics": metrics,
            "candidate_notes": candidate_notes,
            "is_sparse_resume": is_sparse,
        }

    def _extract_metrics_from_chronology(self, chronology: list[dict[str, Any]]) -> list[dict[str, Any]]:
        metrics: list[dict[str, Any]] = []
        counter = 1
        for job in chronology:
            period = f"{job.get('start_date', '')} - {job.get('end_date', '')}".strip(" -")
            for bullet in job.get("highlights", []):
                for match in _METRIC_RE.finditer(bullet):
                    raw_val = match.group("value")
                    unit = (match.group("unit") or "").lower()
                    if not unit and not raw_val.startswith("$"):
                        continue
                    numeric_str = raw_val.replace("$", "").replace(",", "")
                    try:
                        val = float(numeric_str)
                    except ValueError:
                        continue
                    if raw_val.startswith("$"):
                        unit = "usd" + (f"_{unit}" if unit else "")
                    metrics.append(
                        {
                            "metric_id": f"m-{counter}",
                            "raw_text": match.group(0).strip(),
                            "value": val,
                            "unit": unit or "count",
                            "context": bullet,
                            "employer": job.get("employer", ""),
                            "period": period,
                            "evidence_status": "verified_numerical_information",
                        }
                    )
                    counter += 1
        return metrics
