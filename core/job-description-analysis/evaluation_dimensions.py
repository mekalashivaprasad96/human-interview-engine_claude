"""
Evaluation Dimensions - Defines how candidates are evaluated for the target role.
"""

from dataclasses import dataclass, field
from typing import Optional
from .requirements_extractor import JobRequirements


@dataclass
class EvaluationDimension:
    name: str
    weight: float
    description: str
    evaluation_methods: list = field(default_factory=list)
    key_questions: list = field(default_factory=list)
    red_flags: list = field(default_factory=list)
    strong_signals: list = field(default_factory=list)


@dataclass
class EvaluationFramework:
    dimensions: list = field(default_factory=list)
    overall_weights: dict = field(default_factory=dict)
    passing_thresholds: dict = field(default_factory=dict)
    interview_stages: list = field(default_factory=list)


class EvaluationDimensions:
    """Defines evaluation dimensions based on job requirements."""

    # Standard dimension definitions
    STANDARD_DIMENSIONS = {
        'technical_competence': EvaluationDimension(
            name='Technical Competence',
            weight=0.30,
            description='Depth and breadth of technical knowledge relevant to the role',
            evaluation_methods=['coding_exercise', 'technical_questions', 'system_design', 'code_review'],
            key_questions=[
                'Can they solve the coding problem efficiently?',
                'Do they understand the tradeoffs in their solution?',
                'Can they explain complex technical concepts clearly?',
            ],
            red_flags=['Cannot explain basic concepts', 'No awareness of tradeoffs', 'Rigid thinking'],
            strong_signals=['Elegant solutions', 'Deep technical knowledge', 'Teaches interviewer'],
        ),
        'system_design': EvaluationDimension(
            name='System Design & Architecture',
            weight=0.20,
            description='Ability to design scalable, maintainable systems',
            evaluation_methods=['system_design_exercise', 'architecture_discussion', 'tradeoff_analysis'],
            key_questions=[
                'Can they gather requirements and clarify constraints?',
                'Do they make reasonable technology choices?',
                'Can they identify bottlenecks and failure modes?',
            ],
            red_flags=['Over-engineering', 'Ignoring non-functional requirements', 'No operational thinking'],
            strong_signals=['Clear requirements gathering', 'Thoughtful tradeoffs', 'Operational maturity'],
        ),
        'problem_solving': EvaluationDimension(
            name='Problem Solving & Reasoning',
            weight=0.15,
            description='Structured approach to ambiguous and complex problems',
            evaluation_methods=['case_study', 'debugging_exercise', 'hypothetical_scenarios'],
            key_questions=[
                'Do they structure the problem before solving?',
                'Can they identify root causes vs symptoms?',
                'Do they consider multiple approaches?',
            ],
            red_flags=['Jumping to solutions', 'No hypothesis-driven approach', 'Cannot handle ambiguity'],
            strong_signals=['Structured frameworks', 'Data-driven decisions', 'Pragmatic recommendations'],
        ),
        'behavioral_leadership': EvaluationDimension(
            name='Behavioral & Leadership',
            weight=0.15,
            description='Past behavior predicting future performance; leadership potential',
            evaluation_methods=['behavioral_interview', 'leadership_scenarios', 'conflict_resolution'],
            key_questions=[
                'Do they take ownership of outcomes?',
                'How do they handle disagreement and conflict?',
                'Can they influence without authority?',
            ],
            red_flags=['Blaming others', 'No self-reflection', 'Rigid communication'],
            strong_signals=['Clear ownership', 'Growth from failure', 'Empathetic leadership'],
        ),
        'domain_knowledge': EvaluationDimension(
            name='Domain & Business Knowledge',
            weight=0.10,
            description='Understanding of industry, business context, and customer needs',
            evaluation_methods=['domain_questions', 'business_case', 'customer_scenario'],
            key_questions=[
                'Do they understand the business model?',
                'Can they connect technical decisions to business outcomes?',
                'Do they know industry regulations and constraints?',
            ],
            red_flags=['Purely technical view', 'No customer empathy', 'Unaware of regulations'],
            strong_signals=['Business-technical translation', 'Customer-centric thinking', 'Regulatory awareness'],
        ),
        'communication': EvaluationDimension(
            name='Communication & Collaboration',
            weight=0.10,
            description='Ability to communicate effectively with technical and non-technical audiences',
            evaluation_methods=['all_interactions', 'presentation', 'cross_functional_scenario'],
            key_questions=[
                'Can they explain complex ideas simply?',
                'Do they listen actively?',
                'Can they adapt communication to audience?',
            ],
            red_flags=['Jargon overload', 'Not answering the question', 'Dismissive of others'],
            strong_signals=['Clear explanations', 'Active listening', 'Audience adaptation'],
        ),
    }

    # Role-specific weight adjustments
    ROLE_WEIGHTS = {
        'software_engineer': {
            'technical_competence': 0.35,
            'system_design': 0.20,
            'problem_solving': 0.15,
            'behavioral_leadership': 0.15,
            'domain_knowledge': 0.05,
            'communication': 0.10,
        },
        'senior_engineer': {
            'technical_competence': 0.25,
            'system_design': 0.25,
            'problem_solving': 0.15,
            'behavioral_leadership': 0.20,
            'domain_knowledge': 0.05,
            'communication': 0.10,
        },
        'staff_engineer': {
            'technical_competence': 0.20,
            'system_design': 0.30,
            'problem_solving': 0.15,
            'behavioral_leadership': 0.20,
            'domain_knowledge': 0.10,
            'communication': 0.05,
        },
        'engineering_manager': {
            'technical_competence': 0.15,
            'system_design': 0.15,
            'problem_solving': 0.15,
            'behavioral_leadership': 0.35,
            'domain_knowledge': 0.10,
            'communication': 0.10,
        },
        'architect': {
            'technical_competence': 0.20,
            'system_design': 0.35,
            'problem_solving': 0.15,
            'behavioral_leadership': 0.15,
            'domain_knowledge': 0.10,
            'communication': 0.05,
        },
        'solutions_architect': {
            'technical_competence': 0.20,
            'system_design': 0.25,
            'problem_solving': 0.15,
            'behavioral_leadership': 0.15,
            'domain_knowledge': 0.15,
            'communication': 0.10,
        },
        'technical_account_manager': {
            'technical_competence': 0.15,
            'system_design': 0.10,
            'problem_solving': 0.15,
            'behavioral_leadership': 0.20,
            'domain_knowledge': 0.20,
            'communication': 0.20,
        },
        'data_engineer': {
            'technical_competence': 0.35,
            'system_design': 0.25,
            'problem_solving': 0.15,
            'behavioral_leadership': 0.10,
            'domain_knowledge': 0.05,
            'communication': 0.10,
        },
        'ml_engineer': {
            'technical_competence': 0.35,
            'system_design': 0.20,
            'problem_solving': 0.15,
            'behavioral_leadership': 0.10,
            'domain_knowledge': 0.10,
            'communication': 0.10,
        },
        'security_engineer': {
            'technical_competence': 0.35,
            'system_design': 0.20,
            'problem_solving': 0.15,
            'behavioral_leadership': 0.10,
            'domain_knowledge': 0.10,
            'communication': 0.10,
        },
        'devops_engineer': {
            'technical_competence': 0.30,
            'system_design': 0.25,
            'problem_solving': 0.15,
            'behavioral_leadership': 0.10,
            'domain_knowledge': 0.05,
            'communication': 0.15,
        },
        'product_manager': {
            'technical_competence': 0.10,
            'system_design': 0.10,
            'problem_solving': 0.20,
            'behavioral_leadership': 0.20,
            'domain_knowledge': 0.20,
            'communication': 0.20,
        },
    }

    def build_framework(self, requirements: JobRequirements, role_type: str = 'software_engineer') -> EvaluationFramework:
        """Build evaluation framework for the role."""
        framework = EvaluationFramework()

        # Get base weights for role
        weights = self.ROLE_WEIGHTS.get(role_type, self.ROLE_WEIGHTS['software_engineer'])

        # Build dimensions with adjusted weights
        for dim_name, base_dim in self.STANDARD_DIMENSIONS.items():
            dim = EvaluationDimension(
                name=base_dim.name,
                weight=weights.get(dim_name, base_dim.weight),
                description=base_dim.description,
                evaluation_methods=base_dim.evaluation_methods.copy(),
                key_questions=base_dim.key_questions.copy(),
                red_flags=base_dim.red_flags.copy(),
                strong_signals=base_dim.strong_signals.copy(),
            )

            # Customize based on requirements
            self._customize_dimension(dim, requirements)

            framework.dimensions.append(dim)

        # Set overall weights
        framework.overall_weights = {dim.name: dim.weight for dim in framework.dimensions}

        # Set passing thresholds
        framework.passing_thresholds = {
            'technical_competence': 0.6,
            'system_design': 0.6,
            'problem_solving': 0.5,
            'behavioral_leadership': 0.6,
            'domain_knowledge': 0.5,
            'communication': 0.6,
        }

        # Infer interview stages
        framework.interview_stages = self._infer_stages(requirements)

        return framework

    def _customize_dimension(self, dim: EvaluationDimension, requirements: JobRequirements):
        """Customize dimension based on job requirements."""
        # Add domain-specific questions
        if requirements.business_domains:
            dim.key_questions.append(f'How have you applied your skills in {", ".join(requirements.business_domains[:2])}?')

        # Add scale-specific questions
        if requirements.scale_expectations.get('requests_per_second'):
            dim.key_questions.append(f'How would you design for {requirements.scale_expectations["requests_per_second"]:,.0f} RPS?')

        # Add leadership questions if needed
        if requirements.leadership_expectations.get('people_management'):
            dim.key_questions.append('Describe a time you had to make a tough people decision.')

        # Add customer-facing questions
        if requirements.customer_facing:
            dim.key_questions.append('How do you handle a situation where customer needs conflict with technical constraints?')

    def _infer_stages(self, requirements: JobRequirements) -> list:
        """Infer interview stages from requirements."""
        stages = ['recruiter_screen']

        # Technical phone screen
        if 'coding' in requirements.interview_format or 'coding_challenge' in requirements.interview_format:
            stages.append('technical_phone_screen')

        # On-site stages
        onsite = []
        if 'coding' in requirements.interview_format:
            onsite.append('coding')
        if 'system_design' in requirements.interview_format:
            onsite.append('system_design')
        if 'behavioral' in requirements.interview_format:
            onsite.append('behavioral')
        if 'debugging_exercise' in requirements.interview_format:
            onsite.append('debugging')
        if 'presentation' in requirements.interview_format:
            onsite.append('presentation')
        if 'pair_programming' in requirements.interview_format:
            onsite.append('pair_programming')

        if onsite:
            stages.append('on_site:' + ','.join(onsite))

        stages.append('hiring_review')

        return stages

    def get_dimension(self, name: str) -> Optional[EvaluationDimension]:
        """Get a standard dimension by name."""
        return self.STANDARD_DIMENSIONS.get(name)

    def get_all_dimensions(self) -> dict:
        """Get all standard dimensions."""
        return self.STANDARD_DIMENSIONS.copy()