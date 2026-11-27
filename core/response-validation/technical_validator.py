"""
Technical Validator - Validates technical accuracy of responses.
"""

from dataclasses import dataclass
from typing import Optional
from ..experience_enrichment.scenario_generator import Scenario
from ..experience_enrichment.project_modeler import ProjectModel
from ..numerical_intelligence.ledger import NumericalLedger


@dataclass
class TechnicalValidationResult:
    passed: bool
    score: float
    issues: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    corrected_claims: list = field(default_factory=list)


class TechnicalValidator:
    """Validates technical claims in responses."""

    def __init__(self):
        self.technology_facts = self._load_technology_facts()

    def _load_technology_facts(self) -> dict:
        """Load verified technology facts."""
        return {
            "kubernetes": {
                "max_pods_per_node": 110,
                "max_nodes": 5000,
                "control_plane_components": ["api-server", "scheduler", "controller-manager", "etcd"],
                "requires_container_runtime": True,
            },
            "docker": {
                "layer_limit": 127,
                "default_network_driver": "bridge",
                "supports_multi_arch": True,
            },
            "kafka": {
                "max_partition_per_broker": 10000,
                "default_replication_factor": 3,
                "min_insync_replicas": 2,
            },
            "postgresql": {
                "max_connections_default": 100,
                "shared_buffers_recommendation": "25% RAM",
                "work_mem_default": "4MB",
                "supports_partitioning": True,
            },
            "redis": {
                "single_threaded": True,
                "max_clients": 10000,
                "supports_clustering": True,
                "data_structures": ["string", "hash", "list", "set", "sorted_set", "stream"],
            },
            "aws": {
                "regions": 30,
                "availability_zones_per_region": "3-6",
                "s3_durability": "99.999999999%",
                "lambda_max_execution_time": "15 minutes",
            },
            "gcp": {
                "regions": 38,
                "zones_per_region": "3-4",
                "cloud_run_max_instances": 1000,
                "cloud_sql_max_storage": "64 TB",
            },
        }

    def validate(self, response: str, scenario: Scenario, model: ProjectModel,
                  ledger: NumericalLedger, context: dict) -> TechnicalValidationResult:
        """Validate technical claims in response."""
        issues = []
        warnings = []
        corrected = []
        score = 1.0
        r_lower = response.lower()

        # Check technology version claims
        score = min(score, self._check_version_claims(r_lower, scenario, model))

        # Check architecture claims
        score = min(score, self._check_architecture_claims(r_lower, scenario, model))

        # Check scale claims
        score = min(score, self._check_scale_claims(r_lower, scenario, model))

        # Check performance claims
        score = min(score, self._check_performance_claims(r_lower, scenario, model))

        # Check configuration claims
        score = min(score, self._check_config_claims(r_lower, scenario, model))

        # Check protocol claims
        score = min(score, self._check_protocol_claims(r_lower))

        # Check security claims
        score = min(score, self._check_security_claims(r_lower))

        # Check numerical claims against ledger
        score = min(score, self._check_numerical_against_ledger(response, ledger))

        passed = score >= 0.7 and len([i for i in issues if "error" in str(i).lower()]) == 0

        return TechnicalValidationResult(
            passed=passed,
            score=score,
            issues=issues,
            warnings=warnings,
            corrected_claims=corrected,
        )

    def _check_version_claims(self, response: str, scenario: Scenario, model: ProjectModel) -> float:
        """Check technology version claims against timeline."""
        score = 1.0
        # In production, would check against technology timeline validator
        # For now, basic check
        return score

    def _check_architecture_claims(self, response: str, scenario: Scenario, model: ProjectModel) -> float:
        """Check architecture claims against established architecture."""
        score = 1.0
        r_lower = response.lower()

        # Check if claimed architecture matches scenario
        established_pattern = scenario.architecture.get('pattern', '')
        if established_pattern:
            if established_pattern == 'microservices':
                if 'monolith' in r_lower and 'modular' not in r_lower:
                    # Might be contradiction
                    pass

        return score

    def _check_scale_claims(self, response: str, scenario: Scenario, model: ProjectModel) -> float:
        """Check scale claims against scenario."""
        score = 1.0
        r_lower = response.lower()

        # Check for implausible scale
        implausible = [
            ("million requests per second per node", "Implausible per-node RPS"),
            ("petabyte in memory", "Implausible memory scale"),
            ("zero latency", "Zero latency impossible"),
            ("infinite scale", "Infinite scale impossible"),
        ]

        for claim, note in implausible:
            if claim in r_lower:
                return 0.4

        return score

    def _check_performance_claims(self, response: str, scenario: Scenario, model: ProjectModel) -> float:
        """Check performance claims."""
        score = 1.0
        r_lower = response.lower()

        # Check against scenario metrics
        latency = scenario.technical_environment.get('scale', {}).get('latency_p50_ms', 0)
        if latency > 0 and "sub-millisecond" in r_lower and latency > 100:
            return 0.5

        return score

    def _check_config_claims(self, response: str, scenario: Scenario, model: ProjectModel) -> float:
        """Check configuration claims."""
        score = 1.0
        r_lower = response.lower()

        # Known good configs
        good_configs = {
            "kubernetes": ["hpa", "pdb", "resources", "limits", "requests", "mTLS"],
            "kafka": ["acks=all", "min.insync.replicas", "linger.ms", "batch.size"],
            "postgresql": ["shared_buffers", "work_mem", "effective_cache_size", "pgbouncer"],
            "redis": ["maxmemory-policy", "lazyfree", "cluster"],
        }

        # Check for bad configs
        bad_configs = {
            "kubernetes": ["privileged=true", "hostnetwork=true", "runasroot"],
            "kafka": ["acks=0", "replication.factor=1"],
            "postgresql": ["shared_buffers=100%", "autovacuum=off"],
            "redis": ["maxmemory-policy=noeviction", "save=\"\""],
        }

        for tech, bad in bad_configs.items():
            if tech in r_lower:
                for bad_config in bad:
                    if bad_config in r_lower:
                        return 0.4

        return score

    def _check_protocol_claims(self, response: str) -> float:
        """Check protocol claims."""
        score = 1.0
        r_lower = response.lower()

        wrong_protocols = [
            ("http is faster than grpc", "gRPC is typically faster"),
            ("tcp guarantees order but udp doesn't so udp is unreliable", "UDP can be reliable with app-level"),
            ("rest is always better than graphql", "Tradeoffs depend on use case"),
            ("websockets are just http", "WebSockets are different protocol"),
        ]

        for claim, correction in wrong_protocols:
            if claim in r_lower:
                return 0.5

        return score

    def _check_security_claims(self, response: str) -> float:
        """Check security claims."""
        score = 1.0
        r_lower = response.lower()

        wrong_security = [
            ("we encrypt everything so we're secure", "Encryption is necessary but not sufficient"),
            ("jwt is secure because it's signed", "JWT security depends on implementation"),
            ("we use oauth so no security issues", "OAuth implementation matters"),
            ("tls 1.2 is fine", "TLS 1.3 recommended"),
        ]

        for claim, correction in wrong_security:
            if claim in r_lower:
                return 0.6

        return score

    def _check_numerical_against_ledger(self, response: str, ledger: NumericalLedger) -> float:
        """Check numerical claims against ledger."""
        score = 1.0
        # In production, would extract numbers from response and compare to ledger
        return score


from dataclasses import field