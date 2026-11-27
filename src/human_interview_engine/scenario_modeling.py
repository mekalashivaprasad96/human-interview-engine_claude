"""Scenario Modeling Engine — constructs chronologically valid, internally consistent project models."""

from __future__ import annotations

from typing import Any

from .config_loader import EngineConfig
from .employer_intelligence import EmployerIntelligenceEngine
from .models import current_year_utc, short_id
from .numerical_ledger import NumericalLedger


class ScenarioModelingEngine:
    """Builds deeply structured project scenarios anchored to actual employers and eras."""

    def __init__(self, config: EngineConfig, employer_engine: EmployerIntelligenceEngine) -> None:
        self.config = config
        self.employer_engine = employer_engine

    def build_project_scenarios(
        self,
        profile: dict[str, Any],
        world_model: dict[str, Any],
        jd_analysis: dict[str, Any],
        ledger: NumericalLedger,
        operating_mode: str = "immersive_simulation",
    ) -> dict[str, Any]:
        """Construct coherent SimulatedProject scenarios grounded in employer eras and seniority."""
        chronology = profile.get("career_chronology", [])
        contexts = world_model.get("employer_contexts", [])
        seniority = world_model.get("inferred_seniority", {}).get("level", "mid")
        skills_lower = {s.lower() for s in profile.get("explicit_skills", [])}
        jd_tech_lower = {t.lower() for t in jd_analysis.get("core_technical_competencies", [])}
        combined_tech = skills_lower | jd_tech_lower

        projects: list[dict[str, Any]] = []
        if not chronology:
            chronology = [
                {
                    "employer": "Prior Engineering Team",
                    "role_title": "Software Engineer",
                    "start_date": str(current_year_utc() - 2),
                    "end_date": "Present",
                    "start_year": current_year_utc() - 2,
                    "end_year": current_year_utc(),
                    "highlights": [],
                }
            ]
            contexts = [self.employer_engine.infer_employer_context(chronology[0])]

        for idx, job in enumerate(chronology[:3]):
            ctx = contexts[idx] if idx < len(contexts) else self.employer_engine.infer_employer_context(job)
            start_year = job.get("start_year") or (current_year_utc() - 2)
            end_year = job.get("end_year") or current_year_utc()
            if end_year < start_year:
                end_year = start_year

            project = self._create_domain_project(
                idx=idx,
                candidate_id=profile["candidate_id"],
                job=job,
                ctx=ctx,
                seniority=seniority,
                combined_tech=combined_tech,
                start_year=start_year,
                end_year=end_year,
                documented_metrics=profile.get("documented_metrics", []),
            )
            # Chronology sanity check across stack
            stack_names = [t["name"] for t in project["technology_stack"]]
            violations = self.employer_engine.validate_technology_chronology(stack_names, start_year, end_year)
            if violations:
                bad_names = {v["technology"].lower() for v in violations}
                project["technology_stack"] = [
                    t for t in project["technology_stack"] if t["name"].lower() not in bad_names
                ]

            projects.append(project)
            self._register_project_metrics(project, ledger, operating_mode)

        return {
            "candidate_id": profile["candidate_id"],
            "projects": projects,
        }

    def _create_domain_project(
        self,
        idx: int,
        candidate_id: str,
        job: dict[str, Any],
        ctx: dict[str, Any],
        seniority: str,
        combined_tech: set[str],
        start_year: int,
        end_year: int,
        documented_metrics: list[dict[str, Any]],
    ) -> dict[str, Any]:
        employer = job.get("employer", "Employer")
        period = f"{job.get('start_date', start_year)} - {job.get('end_date', end_year)}".strip(" -")
        industry_key = ctx.get("industry_key", "cloud_infrastructure")
        highlights = job.get("highlights", [])
        is_ai_gpu = bool(combined_tech & {"gpu", "cuda", "pytorch", "tensorflow", "triton inference server", "vllm", "ray", "ai", "ml"}) or industry_key == "ai_ml_platform"
        is_semiconductor = industry_key == "semiconductor" or bool(combined_tech & {"rtl", "verilog", "uvm", "fpga", "asic"})
        is_mobile = industry_key == "mobile_applications" or bool(combined_tech & {"swift", "swiftui", "kotlin", "jetpack compose", "react native", "flutter"})
        is_customer_role = ctx.get("candidate_role_scope") == "customer_advisory_and_engineering"

        # Determine realistic scale & team size calibrated to seniority & domain
        team_size = 4 if seniority in ("junior", "mid") else 7 if seniority in ("senior", "staff", "manager") else 12
        nodes = 6 if seniority == "junior" else 16 if (is_ai_gpu or seniority in ("senior", "staff", "principal")) else 12
        gpus_per_node = 8 if is_ai_gpu else 0
        total_gpus = nodes * gpus_per_node

        stack = self._select_era_valid_stack(
            start_year=start_year,
            end_year=end_year,
            industry_key=industry_key,
            is_ai_gpu=is_ai_gpu,
            is_semiconductor=is_semiconductor,
            is_mobile=is_mobile,
            preferred_tech=combined_tech,
        )

        if is_ai_gpu and idx == 0:
            title = f"Distributed GPU Inference & Serving Platform ({employer})"
            objective = "Reduce model serving tail latency and stabilize GPU utilization under burst traffic without breaking multi-tenant cost budgets."
            arch = (
                f"We ran a stateless API gateway fronting a {nodes}-node GPU inference cluster ({gpus_per_node} GPUs/node, "
                f"{total_gpus} GPUs total) with dynamic batching, request priority queues, and autoscaling warm pools."
            )
            baseline_p99 = 480.0
            final_p99 = 278.0
            rps = 1200.0
            monthly_savings = 18500.0
            duration_months = 5
            avail_pct = 99.95
            decisions = [
                {
                    "decision": "We separated latency-critical interactive requests from batch embedding jobs using dedicated node pools and queue weights.",
                    "rationale": "prevented batch memory spikes from starving interactive KV-cache allocations.",
                    "alternatives_considered": ["Single shared best-effort queue", "Over-provisioning 2x static GPUs"],
                    "tradeoffs": "slightly lower off-peak GPU packing (~68% vs 80%) in exchange for predictable p99 latency.",
                },
                {
                    "decision": "We capped the dynamic micro-batch wait window at 12ms instead of 50ms.",
                    "rationale": "cut tail-latency queueing spikes during moderate load while preserving batch efficiency under peak load.",
                    "alternatives_considered": ["Fixed static batch size", "50ms greedy batching"],
                    "tradeoffs": "slightly higher per-request scheduler overhead under low QPS.",
                },
            ]
            challenges = [
                "we hit CUDA out-of-memory evictions during peak context-length bursts because readiness probes passed before model weights warmed.",
                "we rolled back an aggressive preemption policy after noisy-neighbor retries amplified tail latency by 3x.",
            ]
        elif is_semiconductor and idx == 0:
            title = f"Pre-Silicon Regression & Timing Validation Pipeline ({employer})"
            objective = "Eliminate nightly verification bottlenecks and catch CDC/timing regressions before tape-out sign-off."
            arch = (
                f"We ran a distributed UVM simulation farm across {nodes} compute nodes with deterministic seed tracking, "
                "incremental RTL lint gates, and automated coverage-closure dashboards."
            )
            baseline_p99 = 640.0
            final_p99 = 390.0
            rps = 320.0
            monthly_savings = 14000.0
            duration_months = 6
            avail_pct = 99.9
            decisions = [
                {
                    "decision": "We split smoke suites from long-seed constrained-random regressions with deterministic artifact hashing.",
                    "rationale": "gave RTL designers 18-minute feedback instead of waiting 9 hours for overnight runs.",
                    "alternatives_considered": ["Running full UVM regression on every commit", "Manual designer-triggered runs"],
                    "tradeoffs": "having to maintain seed-replay tooling and split triage queues.",
                }
            ]
            challenges = [
                "an intermittent clock-domain crossing bug only reproduced under specific seed timing skew on hardware-in-the-loop benches.",
            ]
        elif is_mobile and idx == 0:
            title = f"Mobile Cold-Start & Offline Sync Reliability Initiative ({employer})"
            objective = "Cut app cold-start latency and eliminate silent offline sync conflicts on unreliable cellular connections."
            arch = (
                "We built a local encrypted SQLite write-ahead queue with idempotency keys, an exponential backoff sync worker, "
                "and deferred non-critical SDK initialization off the main UI thread."
            )
            baseline_p99 = 2400.0
            final_p99 = 1380.0
            rps = 850.0
            monthly_savings = 6500.0
            duration_months = 4
            avail_pct = 99.95
            decisions = [
                {
                    "decision": "We moved analytics and feature-flag hydration off the launch path and introduced idempotent delta sync.",
                    "rationale": "eliminated main-thread blocking during first-frame render that caused 40% of cold-start jank.",
                    "alternatives_considered": ["Aggressive splash-screen caching only", "Full offline-first CRDT rewrite"],
                    "tradeoffs": "delaying non-critical telemetry by ~2 seconds on launch to avoid rewrite risk.",
                }
            ]
            challenges = [
                "duplicate mutations occurred when OS background tasks killed connections mid-ack prior to idempotency keys.",
            ]
        elif is_customer_role and idx == 0:
            title = f"Enterprise Production Migration & Reliability Program ({employer})"
            objective = "Guide high-value enterprise customers through zero-downtime migration while stabilizing recurring SLA escalations."
            arch = (
                f"We ran a multi-region active-passive service deployment across {nodes} worker nodes with traffic-shadow validation, "
                "automated canary health gates, and customer-facing runbooks."
            )
            baseline_p99 = 410.0
            final_p99 = 235.0
            rps = 1500.0
            monthly_savings = 22000.0
            duration_months = 6
            avail_pct = 99.95
            decisions = [
                {
                    "decision": "We required shadow-traffic parity checks and rollback drills before flipping production DNS weights.",
                    "rationale": "caught cutover issues on legacy customer webhooks before customers ever saw them.",
                    "alternatives_considered": ["Big-bang weekend maintenance cutover"],
                    "tradeoffs": "adding two weeks to pilot onboarding in exchange for zero P1 cutover outages.",
                }
            ]
            challenges = [
                "a key retail customer resisted schema validation rules until a joint load test exposed silent payload truncation.",
            ]
        else:
            title = f"Service Reliability & Platform Modernization ({employer})"
            objective = f"Improve reliability, deployment safety, and latency across core {ctx.get('industry', 'platform')} services."
            arch = (
                f"We ran a horizontally scaled service tier on {nodes} compute nodes behind weighted L7 load balancing, "
                "read-through caching, asynchronous event queue decoupling, and automated canary rollbacks."
            )
            baseline_p99 = 420.0
            final_p99 = 245.0
            rps = 950.0
            monthly_savings = 9500.0
            duration_months = 4
            avail_pct = 99.95
            decisions = [
                {
                    "decision": "We decoupled synchronous downstream audit/notification writes onto an idempotent asynchronous worker queue.",
                    "rationale": "stopped downstream latency spikes from exhausting primary request worker pools.",
                    "alternatives_considered": ["Increasing synchronous timeouts and thread pools"],
                    "tradeoffs": "accepting eventual consistency (~1–2s) on non-critical notifications to protect core path latency.",
                }
            ]
            challenges = [
                "connection-pool saturation under retry storms required adding jittered backoff and circuit breakers.",
            ]

        ownership_items = self._derive_individual_contributions(seniority, highlights, is_customer_role)
        scale_obj: dict[str, Any] = {
            "nodes": nodes,
            "throughput_rps": rps,
            "daily_requests": int(rps * 86400),
            "p99_latency_baseline_ms": baseline_p99,
            "p99_latency_final_ms": final_p99,
            "availability_pct": avail_pct,
            "monthly_downtime_minutes": round((1.0 - avail_pct / 100.0) * 43200.0, 2),
            "monthly_cost_savings_usd": monthly_savings,
            "annual_cost_savings_usd": monthly_savings * 12.0,
            "project_duration_months": duration_months,
        }
        if is_ai_gpu:
            scale_obj["gpus_per_node"] = gpus_per_node
            scale_obj["total_gpus"] = total_gpus
            scale_obj["allocation_hours"] = 48
            scale_obj["gpu_hours"] = total_gpus * 48

        # Check documented metrics from resume to honor verified values if available
        emp_metrics = [m for m in documented_metrics if m.get("employer", "").lower() == employer.lower()]

        return {
            "project_id": short_id("proj", f"{candidate_id}:{employer}:{idx}"),
            "title": title,
            "employer": employer,
            "employment_period": period,
            "start_year": start_year,
            "end_year": end_year,
            "business_objective": objective,
            "project_scope": highlights[0] if highlights else f"Core platform engineering and reliability delivery at {employer}.",
            "technical_environment": f"{ctx.get('industry')} production environment ({ctx.get('security_posture')})",
            "architecture_summary": arch,
            "components": [
                {"name": "Ingress / Edge Gateway", "responsibility": "TLS termination, auth, rate limiting, canary routing"},
                {"name": "Core Compute / Worker Tier", "responsibility": "Stateless request execution, batching, circuit breaking"},
                {"name": "State & Telemetry Plane", "responsibility": "Durable persistence, audit logs, SLO burn-rate alerting"},
            ],
            "technology_stack": stack,
            "dependencies": ["Identity/Auth service", "Primary transactional datastore", "Telemetry & alerting pipeline"],
            "infrastructure_scale": scale_obj,
            "team_structure": {
                "team_size": team_size,
                "candidate_role": job.get("role_title", "Engineer"),
                "collaborators": ["2 peer backend/infra engineers", "1 SRE/platform partner", "1 product/program partner"],
            },
            "candidate_responsibilities": [
                f"Acted as {job.get('role_title', 'Engineer')} within a {team_size}-person team.",
                f"Adhered to {ctx.get('change_management', 'canary rollout and peer review gates')}.",
            ],
            "individual_contributions": ownership_items,
            "implementation_decisions": decisions,
            "constraints": [
                f"Had to ship within existing headcount ({team_size} engineers) and freeze windows.",
                f"Legacy integration contracts and {ctx.get('regulatory_environment') or ['internal audit']} controls prevented breaking API changes.",
            ],
            "challenges": challenges,
            "testing_methodology": "Unit + integration suite, synthetic load testing at 1.5x expected peak RPS, and staged 5% -> 25% -> 100% canary rollout.",
            "operational_considerations": {
                "monitoring": "SLI dashboards tracking p50/p95/p99 latency, error budget burn, queue depth, and saturation.",
                "slo_target": f"{avail_pct}% monthly availability",
                "failure_modes": "Downstream timeout cascade, connection-pool exhaustion, bad config push.",
                "rollback_plan": "Automated canary abort on 5xx or p99 breach + instant traffic weight revert.",
            },
            "metrics": {
                "documented_resume_metrics": emp_metrics,
                "scenario_baseline_p99_ms": baseline_p99,
                "scenario_final_p99_ms": final_p99,
                "latency_reduction_pct": round(((baseline_p99 - final_p99) / baseline_p99) * 100.0, 2),
            },
            "outcomes": (
                f"Stabilized production reliability at {avail_pct}% availability while cutting p99 latency "
                f"from {baseline_p99:g}ms to {final_p99:g}ms."
            ),
            "lessons_learned": "Measure tail latency and saturation under realistic burst shapes before tuning timeouts or autoscalers.",
            "evidence_status": "fictional_simulation_scenario",
        }

    def _select_era_valid_stack(
        self,
        start_year: int,
        end_year: int,
        industry_key: str,
        is_ai_gpu: bool,
        is_semiconductor: bool,
        is_mobile: bool,
        preferred_tech: set[str],
    ) -> list[dict[str, Any]]:
        candidates: list[tuple[str, str]] = []
        if is_ai_gpu:
            candidates = [
                ("python", "Control plane, orchestration services, and benchmark harnesses"),
                ("pytorch", "Model execution runtime and tensor profiling"),
                ("cuda", "GPU kernel profiling and memory telemetry"),
                ("triton inference server", "Multi-model dynamic batching and GPU serving"),
                ("vllm", "PagedAttention LLM inference serving"),
                ("kubernetes", "GPU node pool scheduling and autoscaling"),
                ("prometheus", "GPU utilization, queue depth, and latency metrics"),
                ("opentelemetry", "Distributed request tracing across gateway and workers"),
            ]
        elif is_semiconductor:
            candidates = [
                ("python", "Regression orchestration and seed-failure triage scripts"),
                ("linux", "Compute farm runtime and toolchain environment"),
                ("postgresql", "Regression seed history and coverage tracking"),
                ("grafana", "Nightly timing, yield, and coverage dashboards"),
            ]
        elif is_mobile:
            candidates = [
                ("swift", "iOS client architecture and background sync worker"),
                ("kotlin", "Android client modules and coroutine concurrency"),
                ("swiftui", "Declarative UI views on modern iOS targets"),
                ("jetpack compose", "Modern Android UI components"),
                ("postgresql", "Backend sync delta state and conflict resolution"),
                ("opentelemetry", "Mobile-to-backend trace correlation"),
            ]
        else:
            candidates = [
                ("go", "Low-overhead gateway and worker services"),
                ("python", "Automation tooling, load generators, and operational scripts"),
                ("postgresql", "Primary transactional state store"),
                ("redis", "Read-through cache and distributed rate-limit counters"),
                ("kafka", "Asynchronous event buffering and retry isolation"),
                ("kubernetes", "Container orchestration and progressive canary rollouts"),
                ("terraform", "Infrastructure-as-code environment provisioning"),
                ("prometheus", "SLI/SLO telemetry and burn-rate alerts"),
                ("opentelemetry", "End-to-end trace propagation"),
            ]

        selected: list[dict[str, Any]] = []
        for name, purpose in candidates:
            meta = self.config.technology_timeline.get(name.lower())
            intro = int(meta["introduced_year"]) if meta else None
            # Only include technologies that actually existed on or before end_year!
            if intro is not None and end_year < intro:
                continue
            # Also skip very recent tools if project ended earlier than enterprise maturity unless explicitly on resume
            if intro is not None and end_year == intro and name.lower() not in preferred_tech and intro >= 2022:
                continue
            selected.append(
                {
                    "name": name,
                    "version_or_era": f"{max(start_year, intro or start_year)}-{end_year}",
                    "introduced_year": intro,
                    "purpose": purpose,
                }
            )
        if not selected:
            selected.append(
                {
                    "name": "linux",
                    "version_or_era": f"{start_year}-{end_year}",
                    "introduced_year": 1991,
                    "purpose": "Core production compute runtime",
                }
            )
        return selected

    @staticmethod
    def _derive_individual_contributions(
        seniority: str,
        highlights: list[str],
        is_customer_role: bool,
    ) -> list[str]:
        if seniority == "junior":
            base = [
                "I implemented the targeted service configuration and unit/integration test coverage under senior review.",
                "I triaged staging regressions, pulled trace/log evidence, and paired on the safe rollback path.",
            ]
        elif is_customer_role:
            base = [
                "I led technical discovery workshops with customer engineering leads and mapped failure boundaries.",
                "I authored the cutover runbook, ran shadow-traffic verification, and owned executive escalation updates.",
            ]
        elif seniority in ("manager", "director", "executive"):
            base = [
                "I defined reliability guardrails, unblocked cross-team dependencies, and owned rollout sign-off decisions.",
                "I partnered with product and SRE leads on capacity trade-offs while engineers owned direct code execution.",
            ]
        else:
            base = [
                "I designed the queue isolation and backpressure strategy and implemented the core service/config changes.",
                "I built the load-test harness, diagnosed the production saturation bottleneck, and led the canary rollout.",
            ]
        if highlights:
            base.append(f"That work tied directly to {highlights[0][0].lower() + highlights[0][1:]}")
        return base

    @staticmethod
    def _register_project_metrics(
        project: dict[str, Any],
        ledger: NumericalLedger,
        operating_mode: str,
    ) -> None:
        pid = project["project_id"]
        scale = project["infrastructure_scale"]
        period = project["employment_period"]
        ev_status = "fictional_simulation_scenario"
        # Derived metrics inherit fictional status unless all base inputs are verified.
        calc_status = "fictional_simulation_scenario"

        ledger.record_metric(
            project_id=pid,
            metric_name="team_size",
            original_value=project["team_structure"]["team_size"],
            unit="engineers",
            scope=project["employer"],
            measurement_period=period,
            measurement_methodology="Active squad headcount assigned to the project.",
            evidence_status=ev_status,
        )
        ledger.record_metric(
            project_id=pid,
            metric_name="nodes",
            original_value=scale["nodes"],
            unit="nodes",
            scope=project["title"],
            measurement_period=period,
            measurement_methodology="Cluster node inventory in production pool.",
            evidence_status=ev_status,
        )
        if "gpus_per_node" in scale:
            ledger.record_metric(
                project_id=pid,
                metric_name="gpus_per_node",
                original_value=scale["gpus_per_node"],
                unit="GPUs/node",
                scope=project["title"],
                measurement_period=period,
                measurement_methodology="Hardware instance specification per worker node.",
                evidence_status=ev_status,
            )
            ledger.record_metric(
                project_id=pid,
                metric_name="total_gpus",
                original_value=scale["total_gpus"],
                unit="GPUs",
                scope=project["title"],
                measurement_period=period,
                measurement_methodology="Calculated from node count multiplied by GPUs per node.",
                evidence_status=calc_status,
                derived_from=["nodes", "gpus_per_node"],
                formula=f"{scale['nodes']} nodes * {scale['gpus_per_node']} GPUs/node",
            )
            ledger.record_metric(
                project_id=pid,
                metric_name="allocation_hours",
                original_value=scale["allocation_hours"],
                unit="hours",
                scope="48-hour peak stress validation window",
                measurement_period="48-hour benchmark",
                measurement_methodology="Controlled soak test duration.",
                evidence_status=ev_status,
            )
            ledger.record_metric(
                project_id=pid,
                metric_name="gpu_hours",
                original_value=scale["gpu_hours"],
                unit="GPU-hours",
                scope="48-hour peak stress validation window",
                measurement_period="48-hour benchmark",
                measurement_methodology="Calculated by multiplying total allocated GPUs by run duration in hours.",
                evidence_status=calc_status,
                derived_from=["total_gpus", "allocation_hours"],
                formula=f"{scale['total_gpus']} GPUs * {scale['allocation_hours']} hours",
            )

        ledger.record_metric(
            project_id=pid,
            metric_name="p99_latency_ms",
            original_value=scale["p99_latency_final_ms"],
            unit="ms",
            scope="Primary API/serving critical path",
            measurement_period="30-day pre vs post rollout comparison",
            measurement_methodology="Measured at ingress gateway using rolling 5-minute histogram buckets (p99) across matched traffic profiles.",
            evidence_status=ev_status,
            baseline_value=scale["p99_latency_baseline_ms"],
            final_value=scale["p99_latency_final_ms"],
            formula=f"(({scale['p99_latency_final_ms']} - {scale['p99_latency_baseline_ms']}) / {scale['p99_latency_baseline_ms']}) * 100",
        )
        ledger.record_metric(
            project_id=pid,
            metric_name="throughput_rps",
            original_value=scale["throughput_rps"],
            unit="RPS",
            scope="Peak sustained production traffic",
            measurement_period=period,
            measurement_methodology="7-day peak 5-minute average request rate at ingress.",
            evidence_status=ev_status,
        )
        ledger.record_metric(
            project_id=pid,
            metric_name="daily_requests",
            original_value=scale["daily_requests"],
            unit="requests/day",
            scope="Peak sustained daily extrapolation",
            measurement_period="24-hour equivalent",
            measurement_methodology="Sustained RPS multiplied by 86,400 seconds/day.",
            evidence_status=calc_status,
            derived_from=["throughput_rps"],
            formula=f"{scale['throughput_rps']} RPS * 86,400 seconds/day",
        )
        ledger.record_metric(
            project_id=pid,
            metric_name="availability_pct",
            original_value=scale["availability_pct"],
            unit="%",
            scope="Monthly production SLO",
            measurement_period="30-day window (43,200 minutes)",
            measurement_methodology="Successful non-5xx probe and synthetic + real user ratio over 30 days.",
            evidence_status=ev_status,
        )
        ledger.record_metric(
            project_id=pid,
            metric_name="monthly_downtime_minutes",
            original_value=scale["monthly_downtime_minutes"],
            unit="minutes/month",
            scope="Monthly error budget",
            measurement_period="30-day window",
            measurement_methodology="(1 - availability_pct / 100) * 43,200 minutes.",
            evidence_status=calc_status,
            derived_from=["availability_pct"],
            formula=f"(1 - {scale['availability_pct']}/100) * 43,200",
        )
        ledger.record_metric(
            project_id=pid,
            metric_name="monthly_cost_savings_usd",
            original_value=scale["monthly_cost_savings_usd"],
            unit="USD/month",
            scope="Infrastructure run-rate reduction",
            measurement_period="Post-rollout billing cycle",
            measurement_methodology="Matched-traffic cloud billing comparison before and after autoscaling/pool tuning.",
            evidence_status=ev_status,
        )
        ledger.record_metric(
            project_id=pid,
            metric_name="annual_cost_savings_usd",
            original_value=scale["annual_cost_savings_usd"],
            unit="USD/year",
            scope="Annualized run-rate savings",
            measurement_period="12-month annualized projection",
            measurement_methodology="Monthly verified savings multiplied by 12.",
            evidence_status=calc_status,
            derived_from=["monthly_cost_savings_usd"],
            formula=f"${scale['monthly_cost_savings_usd']:,.2f} * 12",
        )
        ledger.record_metric(
            project_id=pid,
            metric_name="project_duration_months",
            original_value=scale["project_duration_months"],
            unit="months",
            scope=project["title"],
            measurement_period=period,
            measurement_methodology="Design kickoff through GA stabilization.",
            evidence_status=ev_status,
        )
