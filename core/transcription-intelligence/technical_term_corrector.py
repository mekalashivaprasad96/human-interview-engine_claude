"""
Technical Term Corrector - Corrects misrecognized technical terms in transcripts.
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class TermCorrection:
    original: str
    corrected: str
    confidence: float
    context: str


class TechnicalTermCorrector:
    """Corrects technical terms using context and phonetic similarity."""

    # Comprehensive technical term dictionary with phonetic variants
    TERM_DICTIONARY = {
        # Infrastructure & Cloud
        "kubernetes": ["kubernetis", "cubernetes", "cubernetis", "k8s", "kube"],
        "docker": ["dockers", "doker", "dockr", "docker container"],
        "container": ["containr", "contaner", "containerd"],
        "pod": ["pods", "podd"],
        "service": ["servis", "servise"],
        "deployment": ["deploymnt", "deploment"],
        "replicaset": ["replica set", "replicaset"],
        "daemonset": ["daemon set", "demonset"],
        "statefulset": ["stateful set", "state full set"],
        "namespace": ["name space", "namespce"],
        "ingress": ["ingres", "ingress controller"],
        "service mesh": ["servis mesh", "service mech", "istio", "linkerd"],
        "api gateway": ["a p i gateway", "api gate way", "api gw"],
        "load balancer": ["load balencer", "lode balancer", "elb", "alb", "nlb"],
        "auto scaling": ["auto scaling", "autoscaling", "auto scale"],
        "horizontal pod autoscaler": ["hpa", "horizontal pod autoscaler"],
        "vertical pod autoscaler": ["vpa", "vertical pod autoscaler"],
        "cluster autoscaler": ["ca", "cluster autoscaler"],
        "helm": ["helm chart", "helm charts"],
        "argocd": ["argo cd", "argo cd", "argocd"],
        "flux": ["flux cd", "fluxcd"],
        "terraform": ["terraforms", "terrafoam", "terra firm", "tf"],
        "ansible": ["ansable", "ansibl", "an sibel", "ansible playbook"],
        "packer": ["packr", "packer image"],
        "vagrant": ["vagrent", "vagrant box"],

        # Monitoring & Observability
        "prometheus": ["promethius", "prometheous", "prometheus server"],
        "grafana": ["grafana", "graphana", "graffana", "grafana dashboard"],
        "alertmanager": ["alert manager", "alertmanager"],
        "pushgateway": ["push gateway", "pushgateway"],
        "node exporter": ["node exporter", "nodexporter"],
        "blackbox exporter": ["blackbox exporter", "black box exporter"],
        "opentelemetry": ["open telemetry", "otel", "opentelemetry collector"],
        "jaeger": ["jager", "jaeger tracing"],
        "zipkin": ["zip kin", "zipkin tracing"],
        "datadog": ["data dog", "datadog agent"],
        "new relic": ["newrelic", "new relic", "nr"],
        "splunk": ["splunk", "splunk enterprise"],
        "elastic": ["elastic", "elk stack", "elasticsearch", "kibana"],
        "loki": ["loki", "grafana loki"],
        "tempo": ["tempo", "grafana tempo"],
        "pyroscope": ["pyroscope", "pyro scope"],

        # Messaging & Streaming
        "kafka": ["cafka", "kafca", "kafa", "apache kafka"],
        "kafka connect": ["kafka connect", "kafka connecter"],
        "kafka streams": ["kafka streams", "kafka stream"],
        "ksql": ["k sql", "ksql db"],
        "schema registry": ["schema registry", "schema registr"],
        "rabbitmq": ["rabbit mq", "rabbitmq", "rabbit m q"],
        "pulsar": ["pulsar", "apache pulsar"],
        "nats": ["n a t s", "nats", "nats streaming"],
        "redis streams": ["redis streams", "redis stream"],
        "pub/sub": ["pub sub", "publish subscribe", "google pub sub"],
        "eventbridge": ["event bridge", "aws eventbridge"],
        "sqs": ["s q s", "sqs", "simple queue service"],
        "sns": ["s n s", "sns", "simple notification service"],
        "kinesis": ["kinesis", "amazon kinesis"],
        "mqtt": ["m q t t", "mqtt", "mosquitto"],

        # Databases
        "postgresql": ["postgress", "postgre", "postgres ql", "postgres", "pg"],
        "mysql": ["my sequel", "my sql", "my s q l"],
        "mongodb": ["mongo db", "mongo", "mongo d b"],
        "redis": ["reddis", "redus", "reddis"],
        "cassandra": ["cassandra", "cassandra db"],
        "dynamodb": ["dynamo db", "dynamodb", "dynamo d b"],
        "elasticsearch": ["elastic search", "elasticsearch", "es"],
        "opensearch": ["open search", "opensearch"],
        "snowflake": ["snowflake", "snow flake"],
        "bigquery": ["big query", "bigquery", "bq"],
        "redshift": ["red shift", "redshift"],
        "clickhouse": ["click house", "clickhouse"],
        "timescaledb": ["timescale db", "timescaledb"],
        "cockroachdb": ["cockroach db", "cockroachdb", "crdb"],
        "yugabytedb": ["yugabyte db", "yugabytedb"],
        "planetscale": ["planet scale", "planetscale"],
        "neon": ["neon", "neon db"],
        "supabase": ["super base", "supabase"],
        "firebase": ["fire base", "firebase"],
        "firestore": ["fire store", "firestore"],
        "dynamodb": ["dynamo db", "dynamodb"],

        # Languages & Runtimes
        "python": ["python", "py"],
        "java": ["java", "jvm"],
        "javascript": ["java script", "js", "javascript"],
        "typescript": ["type script", "ts", "typescript"],
        "go": ["go", "golang", "go lang"],
        "rust": ["rust", "rust lang"],
        "cpp": ["c plus plus", "c++", "cpp"],
        "csharp": ["c sharp", "c#", "csharp", "dotnet"],
        "ruby": ["ruby", "ruby on rails", "rails"],
        "php": ["p h p", "php"],
        "swift": ["swift", "swift lang"],
        "kotlin": ["kotlin", "kotlin lang"],
        "scala": ["scala", "scala lang"],
        "r": ["r", "r lang", "r programming"],
        "julia": ["julia", "julia lang"],

        # Frameworks
        "react": ["react", "react js", "reactjs"],
        "vue": ["vue", "vue js", "vuejs"],
        "angular": ["angular", "angular js"],
        "svelte": ["svelte", "svelte js"],
        "next.js": ["next js", "nextjs", "next dot js"],
        "nuxt": ["nuxt", "nuxt js", "nuxtjs"],
        "django": ["django", "jango"],
        "flask": ["flask", "flask python"],
        "fastapi": ["fast api", "fastapi"],
        "spring": ["spring", "spring boot", "spring framework"],
        "spring boot": ["spring boot", "springboot"],
        "express": ["express", "express js", "expressjs"],
        "nestjs": ["nest js", "nestjs", "nest"],
        "gin": ["gin", "gin gonic"],
        "echo": ["echo", "echo framework"],
        "actix": ["actix", "actix web"],
        "rocket": ["rocket", "rocket rs"],
        "asp.net": ["asp net", "asp dot net", "asp.net core"],
        "laravel": ["laravel", "laravel php"],
        "rails": ["rails", "ruby on rails"],

        # ML/AI
        "tensorflow": ["tensor flow", "tensorflow", "tf"],
        "pytorch": ["py torch", "pytorch", "torch"],
        "jax": ["jax", "jax ml"],
        "keras": ["keras", "keras tf"],
        "scikit-learn": ["scikit learn", "sklearn", "sci kit learn"],
        "xgboost": ["xg boost", "xgboost"],
        "lightgbm": ["light gbm", "lightgbm"],
        "catboost": ["cat boost", "catboost"],
        "hugging face": ["hugging face", "huggingface", "hf"],
        "transformers": ["transformers", "transformer"],
        "llama": ["llama", "llama 2", "llama 3"],
        "gpt": ["gpt", "gpt 3", "gpt 4", "chat gpt"],
        "bert": ["bert", "b e r t"],
        "stable diffusion": ["stable diffusion", "stable difusion"],
        "mlflow": ["ml flow", "mlflow"],
        "kubeflow": ["kube flow", "kubeflow"],
        "airflow": ["air flow", "airflow", "apache airflow"],
        "prefect": ["prefect", "prefect io"],
        "dagster": ["dagster", "dagster io"],
        "pandas": ["pandas", "pan das"],
        "numpy": ["num py", "numpy", "num pi"],
        "polars": ["polars", "polar rs"],
        "spark": ["spark", "apache spark", "pyspark"],
        "flink": ["flink", "apache flink"],
        "ray": ["ray", "ray io"],
        "dask": ["dask", "dask ml"],
        "modin": ["modin", "modin pandas"],

        # Security
        "oauth": ["o auth", "oauth", "o auth 2"],
        "oidc": ["o i d c", "oidc", "openid connect"],
        "saml": ["saml", "s a m l"],
        "jwt": ["j w t", "jwt", "jason web token"],
        "bcrypt": ["b crypt", "bcrypt"],
        "argon2": ["argon 2", "argon2"],
        "vault": ["vault", "hashicorp vault"],
        "cert-manager": ["cert manager", "certmanager"],
        "kyverno": ["kyverno", "kiverno"],
        "opa": ["o p a", "opa", "open policy agent"],
        "gatekeeper": ["gatekeeper", "gate keeper"],
        "falco": ["falco", "falco security"],
        "sysdig": ["sysdig", "sys dig"],
        "aquasec": ["aqua sec", "aquasec"],
        "trivy": ["trivy", "tri vy"],
        "snyk": ["snyk", "snyk io"],
        "dependabot": ["dependabot", "dependa bot"],

        # Metrics & Performance
        "rps": ["r p s", "rps", "requests per second", "req per sec"],
        "tps": ["t p s", "tps", "transactions per second", "txn per sec"],
        "qps": ["q p s", "qps", "queries per second"],
        "p99": ["p ninety nine", "p nine nine", "p 99", "percentile 99"],
        "p95": ["p ninety five", "p nine five", "p 95", "percentile 95"],
        "p50": ["p fifty", "p five zero", "p 50", "percentile 50", "median"],
        "latency": ["latency", "latencey", "response time"],
        "throughput": ["throughput", "through put", "thruput"],
        "availability": ["availability", "availablity", "uptime"],
        "sla": ["s l a", "sla", "service level agreement"],
        "slo": ["s l o", "slo", "service level objective"],
        "sli": ["s l i", "sli", "service level indicator"],
        "mttr": ["m t t r", "mttr", "mean time to recovery"],
        "mtbf": ["m t b f", "mtbf", "mean time between failures"],
        "rto": ["r t o", "rto", "recovery time objective"],
        "rpo": ["r p o", "rpo", "recovery point objective"],

        # Networking
        "dns": ["d n s", "dns", "domain name system"],
        "cdn": ["c d n", "cdn", "content delivery network"],
        "tcp": ["t c p", "tcp"],
        "udp": ["u d p", "udp"],
        "http": ["h t t p", "http", "http 1", "http 2", "http 3"],
        "grpc": ["g r p c", "grpc", "g rpc"],
        "graphql": ["graph ql", "graphql", "gql"],
        "rest": ["rest", "r e s t", "restful"],
        "websocket": ["web socket", "websocket", "ws"],
        "server-sent events": ["server sent events", "sse", "eventsource"],
        "mqtt": ["m q t t", "mqtt"],
        "ipv4": ["i p v 4", "ipv4"],
        "ipv6": ["i p v 6", "ipv6"],
        "cidr": ["c i d r", "cidr"],
        "vpc": ["v p c", "vpc", "virtual private cloud"],
        "subnet": ["subnet", "sub net"],
        "nat gateway": ["nat gateway", "nat gate way"],
        "vpn": ["v p n", "vpn"],
        "ssh": ["s s h", "ssh"],
        "tls": ["t l s", "tls", "ssl"],
        "mtls": ["m t l s", "mtls", "mutual tls"],

        # CI/CD
        "ci/cd": ["c i cd", "ci cd", "c i c d", "cd ci", "continuous integration"],
        "jenkins": ["jenkins", "jenkin"],
        "gitlab ci": ["gitlab ci", "gitlab c i", "gitlab pipeline"],
        "github actions": ["github actions", "github action", "gh actions"],
        "circleci": ["circle ci", "circleci"],
        "argocd": ["argo cd", "argocd"],
        "flux": ["flux", "flux cd", "fluxcd"],
        "spinnaker": ["spinnaker", "spinnaker cd"],
        "tekton": ["tekton", "tekton cd"],
        "buildkite": ["buildkite", "build kite"],
        "teamcity": ["team city", "teamcity"],
        "bamboo": ["bamboo", "atlassian bamboo"],
        "azure devops": ["azure devops", "azure dev ops", "ado"],
        "bitbucket pipelines": ["bitbucket pipelines", "bitbucket pipe lines"],

        # Testing
        "unit test": ["unit test", "unit testing", "unit tests"],
        "integration test": ["integration test", "integration testing"],
        "end-to-end test": ["end to end test", "e2e test", "e2e testing"],
        "load test": ["load test", "load testing", "performance test"],
        "stress test": ["stress test", "stress testing"],
        "chaos test": ["chaos test", "chaos testing", "chaos engineering"],
        "canary": ["canary", "canary deployment", "canary release"],
        "blue-green": ["blue green", "blue-green", "blue green deployment"],
        "feature flag": ["feature flag", "feature flags", "feature toggle"],
        "ab test": ["a b test", "ab test", "ab testing", "split test"],
    }

    def __init__(self):
        # Build reverse index for fast lookup
        self.reverse_index = {}
        for canonical, variants in self.TERM_DICTIONARY.items():
            for variant in variants:
                self.reverse_index[variant.lower()] = canonical
            self.reverse_index[canonical.lower()] = canonical

    def correct(self, text: str, context: dict = None) -> tuple[str, list[TermCorrection]]:
        """Correct technical terms in text."""
        corrections = []
        words = text.split()
        corrected_words = []
        i = 0

        while i < len(words):
            word = words[i]
            word_lower = word.lower().strip('.,!?;:')

            # Check for multi-word terms (up to 3 words)
            matched = False
            for n in range(3, 0, -1):
                if i + n <= len(words):
                    phrase = " ".join(words[i:i+n]).lower().strip('.,!?;:')
                    if phrase in self.reverse_index:
                        canonical = self.reverse_index[phrase]
                        # Preserve capitalization pattern
                        corrected_phrase = self._preserve_case(phrase, canonical, words[i:i+n])
                        corrected_words.append(corrected_phrase)
                        corrections.append(TermCorrection(
                            original=phrase,
                            corrected=canonical,
                            confidence=0.9,
                            context=self._get_context(text, i, n),
                        ))
                        i += n
                        matched = True
                        break

            if not matched:
                # Check single word
                if word_lower in self.reverse_index:
                    canonical = self.reverse_index[word_lower]
                    corrected_word = self._preserve_case(word_lower, canonical, [word])
                    corrected_words.append(corrected_word)
                    corrections.append(TermCorrection(
                        original=word,
                        corrected=canonical,
                        confidence=0.85,
                        context=self._get_context(text, i, 1),
                    ))
                else:
                    corrected_words.append(word)
                i += 1

        return " ".join(corrected_words), corrections

    def _preserve_case(self, original: str, canonical: str, words: list) -> str:
        """Preserve capitalization pattern from original."""
        if not words:
            return canonical

        # Check if all words are uppercase
        if all(w.isupper() for w in words):
            return canonical.upper()

        # Check if first word capitalized (title case)
        if words[0][0].isupper() and len(words[0]) > 1:
            return canonical.title()

        # Check if camelCase
        if len(words) == 1 and any(c.isupper() for c in words[0][1:]):
            # Convert to camelCase
            parts = canonical.split()
            return parts[0].lower() + "".join(p.title() for p in parts[1:])

        return canonical.lower()

    def _get_context(self, text: str, index: int, length: int) -> str:
        """Get surrounding context for a correction."""
        words = text.split()
        start = max(0, index - 3)
        end = min(len(words), index + length + 3)
        return " ".join(words[start:end])

    def add_custom_terms(self, terms: dict):
        """Add custom technical terms."""
        for canonical, variants in terms.items():
            if canonical not in self.TERM_DICTIONARY:
                self.TERM_DICTIONARY[canonical] = []
            self.TERM_DICTIONARY[canonical].extend(variants)
            for variant in variants:
                self.reverse_index[variant.lower()] = canonical
            self.reverse_index[canonical.lower()] = canonical

    def get_suggestions(self, partial: str, max_results: int = 5) -> list[str]:
        """Get term suggestions for partial input."""
        partial_lower = partial.lower()
        suggestions = []

        for term in self.reverse_index:
            if term.startswith(partial_lower):
                canonical = self.reverse_index[term]
                if canonical not in suggestions:
                    suggestions.append(canonical)
                if len(suggestions) >= max_results:
                    break

        return suggestions