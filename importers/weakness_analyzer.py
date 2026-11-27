"""
Weakness Analyzer - Analyzes historical interviews to identify recurring weaknesses.
"""

import re
from dataclasses import dataclass, field
from typing import Optional
from collections import Counter
from .transcript_importer import InterviewTranscript


@dataclass
class WeaknessFinding:
    category: str
    description: str
    evidence: list = field(default_factory=list)
    frequency: int = 0
    severity: str = "medium"  # low, medium, high, critical
    suggested_fix: str = ""
    related_categories: list = field(default_factory=list)


@dataclass
class WeaknessReport:
    total_interviews_analyzed: int = 0
    total_messages_analyzed: int = 0
    findings: list = field(default_factory=list)
    category_counts: dict = field(default_factory=dict)
    communication_profile: dict = field(default_factory=dict)
    regression_tests: list = field(default_factory=list)


class WeaknessAnalyzer:
    """Analyzes historical interviews to identify recurring weaknesses."""

    WEAKNESS_CATEGORIES = {
        "robotic_communication": {
            "patterns": [
                r"that's a great question",
                r"absolutely,",
                r"in my previous role",
                r"that's how i approach",
                r"as an ai language model",
                r"based on the resume",
                r"the information provided",
                r"i would say that",
                r"it's important to note",
                r"first and foremost",
            ],
            "description": "Uses robotic, template-like phrases that sound rehearsed",
            "severity": "high",
            "fix": "Use natural, varied language with contractions and personal voice",
        },
        "excessive_answer_length": {
            "patterns": [
                r"\b(?:however|furthermore|moreover|additionally|consequently)\b.*\b(?:however|furthermore|moreover|additionally|consequently)\b",
            ],
            "description": "Answers are excessively long with repetitive transitions",
            "severity": "medium",
            "fix": "Practice concise answers; use duration guidelines per question type",
        },
        "insufficient_answer_depth": {
            "patterns": [
                r"^i (?:used|worked|did|handled) .*\.?$",
                r"^we (?:used|implemented|built) .*\.?$",
            ],
            "description": "Answers lack technical depth and implementation detail",
            "severity": "high",
            "fix": "Add implementation specifics: configurations, algorithms, tradeoffs, metrics",
        },
        "missing_numerical_information": {
            "patterns": [
                r"(?:many|much|several|a lot|few|some) (?:requests|users|servers|nodes|gb|tb)",
            ],
            "description": "Uses vague quantifiers instead of specific numbers",
            "severity": "high",
            "fix": "Maintain numerical ledger; answer quantitative questions with exact figures",
        },
        "weak_numerical_reasoning": {
            "patterns": [
                r"(?:about|around|roughly|approximately) \d+",
                r"\d+% (?:improvement|reduction|increase) (?:without|no) (?:baseline|context)",
            ],
            "description": "Provides numbers without context, baselines, or calculation methodology",
            "severity": "high",
            "fix": "Always provide baseline, methodology, and unit when giving numbers",
        },
        "unsupported_metrics": {
            "patterns": [
                r"(?:improved|reduced|increased|optimized) (?:by|to) \d+%",
            ],
            "description": "Claims percentage improvements without baseline or verification",
            "severity": "high",
            "fix": "Track baselines in ledger; explain calculation when giving percentages",
        },
        "inadequate_technical_implementation": {
            "patterns": [
                r"we (?:used|implemented) (?:kafka|kubernetes|redis|postgresql) (?:for|to) .*\.?$",
            ],
            "description": "Names technologies but doesn't explain implementation details",
            "severity": "high",
            "fix": "Explain configuration, scaling, failure modes, and operational considerations",
        },
        "generic_textbook_explanations": {
            "patterns": [
                r"(?:kafka|kubernetes|redis) is a (?:distributed|in-memory|message) (?:system|queue|database)",
                r"by definition, ",
                r"textbook (?:approach|solution|pattern)",
            ],
            "description": "Gives textbook definitions instead of practical experience",
            "severity": "medium",
            "fix": "Focus on your implementation: config choices, challenges, tradeoffs, lessons",
        },
        "weak_individual_ownership": {
            "patterns": [
                r"^we (?:did|built|implemented|handled|designed) ",
                r"the team (?:did|built|implemented|handled|designed) ",
            ],
            "description": "Uses 'we' without clarifying individual contribution",
            "severity": "high",
            "fix": "Use ownership language: 'I led', 'I designed', 'I implemented', 'My responsibility'",
        },
        "repeated_professional_stories": {
            "patterns": [],
            "description": "Reuses the same story across multiple questions",
            "severity": "medium",
            "fix": "Build diverse story bank; select different experiences for different competencies",
        },
        "employer_misalignment": {
            "patterns": [],
            "description": "References experiences that don't match employer/industry context",
            "severity": "medium",
            "fix": "Align stories with employer's industry, scale, and operational priorities",
        },
        "technology_timeline_errors": {
            "patterns": [
                r"(?:kubernetes|docker|kafka|terraform) (?:in|during) 20(?:1[0-5]|0\d)",
            ],
            "description": "References technologies that didn't exist during employment period",
            "severity": "high",
            "fix": "Validate technology availability against employment dates",
        },
        "candidate_identity_contamination": {
            "patterns": [
                r"(?:as a|i am a) (?:junior|senior|principal|staff|manager|director) ",
            ],
            "description": "Inconsistent seniority signals across answers",
            "severity": "medium",
            "fix": "Maintain consistent persona throughout interview session",
        },
        "unnecessary_clarifying_questions": {
            "patterns": [
                r"could you clarify",
                r"what do you mean by",
                r"can you define",
            ],
            "description": "Asks clarifying questions for straightforward questions",
            "severity": "low",
            "fix": "Only clarify when answer materially changes; use reasonable assumptions",
        },
        "failure_to_wait_for_clarification": {
            "patterns": [
                r"i'll assume",
                r"assuming you mean",
                r"let me answer",
            ],
            "description": "Asks clarification but immediately answers without waiting",
            "severity": "medium",
            "fix": "Ask one concise question, then STOP and wait for response",
        },
        "misunderstood_interviewer_intent": {
            "patterns": [],
            "description": "Answers different question than what was asked",
            "severity": "high",
            "fix": "Classify question type; identify competency being tested; answer that specifically",
        },
        "speech_transcription_errors": {
            "patterns": [
                r"(?:kubernetis|cubernetes|cafka|reddis|postgress)",
            ],
            "description": "Fails to correct speech recognition errors in technical terms",
            "severity": "medium",
            "fix": "Use technical term corrector; recognize phonetic variants",
        },
        "followup_contradictions": {
            "patterns": [],
            "description": "Contradicts previous answers in follow-up questions",
            "severity": "critical",
            "fix": "Maintain consistency ledger; track all established facts and numbers",
        },
        "incorrect_technical_assumptions": {
            "patterns": [
                r"(?:always|never|must|only way) ",
            ],
            "description": "Makes absolute technical claims that are context-dependent",
            "severity": "medium",
            "fix": "Use nuanced language: 'typically', 'in our context', 'tradeoff was'",
        },
        "excessive_agreement": {
            "patterns": [
                r"you're (?:absolutely|completely|totally) right",
                r"that's (?:exactly|precisely) correct",
            ],
            "description": "Automatically agrees with interviewer challenges without defending valid positions",
            "severity": "medium",
            "fix": "Defend valid decisions with reasoning; acknowledge legitimate criticism only",
        },
        "weak_pressure_handling": {
            "patterns": [
                r"i (?:don't know|not sure|guess|think maybe)",
                r"that's a (?:hard|difficult|tough) question",
            ],
            "description": "Shows uncertainty or deflection under pressure",
            "severity": "high",
            "fix": "Stay calm; show how you'd validate; admit limits honestly but demonstrate problem-solving",
        },
        "missing_business_impact": {
            "patterns": [],
            "description": "Technical answers lack business context and outcome focus",
            "severity": "medium",
            "fix": "Connect technical decisions to business outcomes: revenue, cost, risk, customer value",
        },
        "unnatural_conclusions": {
            "patterns": [
                r"that's how i approach these situations",
                r"that's my (?:approach|methodology|process)",
                r"in conclusion, ",
                r"to summarize, ",
            ],
            "description": "Ends answers with rehearsed, template conclusions",
            "severity": "low",
            "fix": "Stop naturally when question answered; no forced summaries",
        },
        "breaking_character_referencing_resume": {
            "patterns": [
                r"based on (?:my|the) resume",
                r"according to (?:my|the) resume",
                r"the resume (?:says|mentions|shows)",
                r"as mentioned in (?:my|the) resume",
            ],
            "description": "Breaks candidate persona by referencing resume/documents",
            "severity": "high",
            "fix": "Never reference resume, documents, or initialization; speak as the candidate",
        },
    }

    def __init__(self):
        self.compiled_patterns = {}
        for category, info in self.WEAKNESS_CATEGORIES.items():
            patterns = info.get("patterns", [])
            if patterns:
                self.compiled_patterns[category] = [re.compile(p, re.IGNORECASE) for p in patterns]

    def analyze_transcripts(self, transcripts: list[InterviewTranscript]) -> WeaknessReport:
        """Analyze multiple transcripts for weaknesses."""
        report = WeaknessReport(
            total_interviews_analyzed=len(transcripts),
        )

        all_findings = []
        total_messages = 0

        for transcript in transcripts:
            candidate_messages = [m for m in transcript.messages if m.get('role') in ['candidate', 'interviewee']]
            total_messages += len(candidate_messages)

            for msg in candidate_messages:
                content = msg.get('content', '')
                findings = self._analyze_message(content, transcript)
                all_findings.extend(findings)

        report.total_messages_analyzed = total_messages
        report.findings = self._consolidate_findings(all_findings)
        report.category_counts = self._count_categories(report.findings)
        report.communication_profile = self._build_communication_profile(transcripts)
        report.regression_tests = self._generate_regression_tests(report.findings)

        return report

    def _analyze_message(self, content: str, transcript: InterviewTranscript) -> list[WeaknessFinding]:
        """Analyze a single candidate message for weaknesses."""
        findings = []

        for category, info in self.WEAKNESS_CATEGORIES.items():
            patterns = self.compiled_patterns.get(category, [])

            for pattern in patterns:
                matches = pattern.findall(content)
                if matches:
                    finding = WeaknessFinding(
                        category=category,
                        description=info["description"],
                        evidence=[content[:200]],
                        frequency=len(matches),
                        severity=info["severity"],
                        suggested_fix=info["fix"],
                    )
                    findings.append(finding)

        return findings

    def _consolidate_findings(self, findings: list[WeaknessFinding]) -> list[WeaknessFinding]:
        """Consolidate duplicate findings."""
        consolidated = {}

        for finding in findings:
            key = finding.category
            if key in consolidated:
                consolidated[key].frequency += finding.frequency
                consolidated[key].evidence.extend(finding.evidence[:2])
            else:
                consolidated[key] = finding

        # Sort by severity and frequency
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_findings = sorted(
            consolidated.values(),
            key=lambda f: (severity_order.get(f.severity, 99), -f.frequency)
        )

        return sorted_findings

    def _count_categories(self, findings: list[WeaknessFinding]) -> dict:
        """Count findings by category."""
        return Counter(f.category for f in findings)

    def _build_communication_profile(self, transcripts: list[InterviewTranscript]) -> dict:
        """Build communication profile from transcripts."""
        all_candidate_text = " ".join(
            m.get('content', '')
            for t in transcripts
            for m in t.messages
            if m.get('role') in ['candidate', 'interviewee']
        )

        words = all_candidate_text.split()
        sentences = re.split(r'[.!?]+', all_candidate_text)

        return {
            "total_words": len(words),
            "total_sentences": len([s for s in sentences if s.strip()]),
            "avg_words_per_sentence": len(words) / max(len(sentences), 1),
            "contraction_rate": self._calculate_contraction_rate(all_candidate_text),
            "first_person_rate": self._calculate_first_person_rate(all_candidate_text),
            "technical_term_density": self._calculate_technical_density(all_candidate_text),
        }

    def _calculate_contraction_rate(self, text: str) -> float:
        """Calculate contraction usage rate."""
        contractions = len(re.findall(r"\b\w+'\w+\b", text))
        total_words = len(text.split())
        return contractions / max(total_words, 1)

    def _calculate_first_person_rate(self, text: str) -> float:
        """Calculate first-person pronoun rate."""
        first_person = len(re.findall(r"\b(?:i|my|me|mine)\b", text, re.IGNORECASE))
        total_pronouns = len(re.findall(r"\b(?:i|me|my|mine|we|us|our|ours|you|your|yours|he|him|his|she|her|hers|they|them|their|theirs)\b", text, re.IGNORECASE))
        return first_person / max(total_pronouns, 1)

    def _calculate_technical_density(self, text: str) -> float:
        """Calculate technical term density."""
        technical_terms = [
            'kubernetes', 'docker', 'kafka', 'redis', 'postgresql', 'aws', 'gcp', 'azure',
            'microservice', 'api', 'database', 'cache', 'queue', 'pipeline', 'deployment',
            'monitoring', 'observability', 'latency', 'throughput', 'scalability', 'reliability',
        ]
        text_lower = text.lower()
        technical_count = sum(1 for term in technical_terms if term in text_lower)
        total_words = len(text.split())
        return technical_count / max(total_words / 100, 1)  # per 100 words

    def _generate_regression_tests(self, findings: list[WeaknessFinding]) -> list[str]:
        """Generate regression tests from findings."""
        tests = []

        for finding in findings:
            if finding.severity in ["critical", "high"]:
                tests.append(f"Test: {finding.category} - Verify {finding.suggested_fix}")

        # Add standard regression tests
        standard_tests = [
            "Test: No robotic phrases in responses",
            "Test: Numerical claims have baselines and units",
            "Test: Ownership language uses 'I' appropriately",
            "Test: No technology timeline violations",
            "Test: Follow-up consistency maintained",
            "Test: Technical depth appropriate for question type",
            "Test: No breaking character (resume references)",
            "Test: Answer length within guidelines",
        ]

        tests.extend(standard_tests)
        return tests

    def get_top_weaknesses(self, report: WeaknessReport, n: int = 5) -> list[WeaknessFinding]:
        """Get top N weaknesses by severity and frequency."""
        return report.findings[:n]

    def generate_action_plan(self, report: WeaknessReport) -> list[str]:
        """Generate prioritized action plan."""
        actions = []

        for finding in report.findings:
            if finding.severity in ["critical", "high"]:
                actions.append(f"[HIGH] {finding.category}: {finding.suggested_fix}")
            elif finding.severity == "medium":
                actions.append(f"[MEDIUM] {finding.category}: {finding.suggested_fix}")

        return actions