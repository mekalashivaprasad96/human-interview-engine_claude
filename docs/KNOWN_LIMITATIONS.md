# Known Limitations

1. **Deterministic Offline Synthesizer vs. Live LLM Surface Fluency:**
   The zero-dependency Python runtime produces crisp, consistent, ledger-verified spoken answers for offline execution and regression testing, while an LLM adapter (Claude Code, Claude, ChatGPT) provides richer linguistic nuance over those same structured ledgers and cognitive rules.
2. **Resume Parsing Heuristics:**
   Highly unconventional multi-column PDF/table text dumps (e.g., side-by-side layout strings without clear date ranges or section headings) may require light pre-formatting or JSON resume input for optimal chronology extraction.
3. **Technology Timeline Registry Scope:**
   `config/technology_timeline.json` tracks 70+ major frameworks, clouds, languages, and infrastructure tools. Niche proprietary internal frameworks not listed in the registry are not flagged by chronology validation unless added to `config/technology_timeline.json`.
4. **External Voice / ASR Integration:**
   Speech transcription cleanup handles text transcripts and common phonetic errors (`cube control`, `pie torch`, `open telemetry`, etc.); live microphone capture must be supplied by an authorized host voice interface.
5. **No Outcome Guarantees:**
   High rubric scores reflect conversational realism and technical consistency, not guaranteed hiring decisions.
