from dataclasses import dataclass, field
import typing as t

dataclass=dataclass
@dataclass
class Story:
    number: int
    title: str
    points: int
    why_exists: str
    problem_solved: str
    prerequisites_stories: t.List[str]
    prerequisites_concepts: t.List[str]
    depends_on: t.List[int]
    unlocks: t.List[int]
    entry_readiness: t.List[str]
    learning_objectives: t.List[str]
    concepts_to_master: t.List[str]
    estatemap_implementation: str
    files_functions_to_study: t.List[str]
    request_data_flow: str
    lab_standalone: str
    lab_estatemap_mapping: str
    acceptance_criteria: t.List[str]
    verification_evidence: t.List[str]
    outcome_conceptual: str
    outcome_implementation: str
    outcome_interview: str
    common_mistakes: t.List[str]
    debugging_symptom: str
    debugging_investigate: str
    debugging_goal: str
    tradeoffs_alternatives: t.List[str]
    production_current: str
    production_at_scale: str
    interview_basic: str
    interview_implementation: str
    interview_tradeoff: str
    interview_debugging: str
    interview_system_design: str
    interview_answer_framework: str
    connection_previous: str
    connection_next: str
    mastery_checklist: t.List[str]

    def to_markdown(self) -> str:
        num = f"{self.number:02d}"
        deps = ", ".join([f"Story {d:02d}" for d in self.depends_on]) if self.depends_on else "None (Entry Point)"
        unls = ", ".join([f"Story {u:02d}" for u in self.unlocks]) if self.unlocks else "None (Terminal Story)"
        
        l = []
        l.append(f"### Story {kum} — {self.title}")
        l.append(f"* **Story Points**: {self.points}")
        l.append(f"* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered")
        l.append("")
        
        l.append(f"#### 1. Why This Story Exists")
        l.append(self.why_exists.strip())
        l.append("")
        
        l.append(f"#### 2. Problem Being Solved")
        l.append(self.problem_solved.strip())
        l.append("")
        
        l.append(f"#### 3. Prerequisites")
        l.append(f"- **Required Stories**: {', '.join(self.prerequisites_stories) if self.prerequisites_stories else 'None'}")
        l.append(f"- **Required Concepts**: {', '.join(self.prerequisites_concepts)}")
        l.append(f"- **Depends On**: {deps}")
        l.append(f"- **Unlocks**: {unls}")
        l.append("")
        
        l.append(f"#### 4. Entry Readiness Check")
        for chk in self.entry_readiness:
            l.append(f"- [ ] {chk}")
        l.append("")
        
        l.append(f"#### 5. Learning Objectives")
        for obj in self.learning_objectives:
            l.append(f"- {obj}")
        l.append("")
        
        l.append(f"#### 6. Concepts to Master")
        for c in self.concepts_to_master:
            l.append(f"- {c}")
        l.append("")
        
        l.append(f"#### 7. EstateMap Implementation")
        l.append(self.estatemap_implementation.strip())
        l.append("")
        
        l.append(f"#### 8. Files / Functions to Study")
        for f in self.files_functions_to_study:
            l.append(f"- `{f}`")
        l.append("")
        
        l.append(f"#### 9. Request / Data Flow")
        l.append(self.request_data_flow.strip())
        l.append("")
        
        l.append(f"#### 10. Build It Yourself")
        l.append(f"**Standalone Lab:** \n{self.lab_standalone.strip()}")
        l.append("")
        l.append(f"**EstateMap Codebase Mapping:** \n{self.lab_estatemap_mapping.strip()}")
        l.append("")
        
        l.append(f"#### 11. Acceptance Criteria")
        for i, ac in enumerate(self.acceptance_criteria, 1):
            l.append(f"- **AC{i}**: {ac}")
        l.append("")
        
        l.append(f"#### 12. Verification / Evidence")
        for v in self.verification_evidence:
            l.append(f"- {v}")
        l.append("")
        
        l.append(f"#### 13. Final Outcome")
        l.append(f"- **Conceptual Mastery**: {self.outcome_conceptual.strip()}")
        l.append(f"- **Implementation Capability**: {self.outcome_implementation.strip()}")
        l.append(f"- **Interview Defense**: {self.outcome_interview.strip()}")
        l.append("")
        
        l.append(f"#### 14. Common Mistakes")
        for m in self.common_mistakes:
            l.append(f"- {m}")
        l.append("")
        
        l.append(f"#### 15. Debugging Exercise")
        l.append(f"- **Symptom**: {self.debugging_symptom.strip()}")
        l.append(f"- **Investigate**: {self.debugging_investigate.strip()}")
        l.append(f"- **Goal**: {self.debugging_goal.strip()}")
        l.append("")
        
        l.append(f"#### 16. Tradeoffs / Alternatives")
        for t in self.tradeoffs_alternatives:
            l.append(f"- {t}")
        l.append("")
        
        l.append(f"#### 17. Production Considerations")
        l.append(f"- **Current Implementation**: {self.production_current.strip()}")
        l.append(f"- **At Scale**: {self.production_at_scale.strip()}")
        l.append("")
        
        l.append(f"#### 18. Interview Questions")
        l.append(f"- **Basic Conceptual**: {self.interview_basic.strip()}")
        l.append(f"- **Implementation Deep-Dive**: {self.interview_implementation.strip()}")
        l.append(f"- **Tradeoff / Architecture**: {self.interview_tradeoff.strip()}")
        l.append(f"- **Debugging / Failure Mode**: {self.interview_debugging.strip()}")
        l.append(f"- **System Design Scenario**: {self.interview_system_design.strip()}")
        l.append("")
        
        l.append(f"#### 19. Interview Answer Framework")
        l.append(self.interview_answer_framework.strip())
        l.append("")
        
        l.append(f"#### 20. Connection to Previous Story")
        l.append(self.connection_previous.strip())
        l.append("")
        
        l.append(f"#### 21. Connection to Next Story")
        l.append(self.connection_next.strip())
        l.append("")
        
        l.append(f"#### 22. Mastery Checklist")
        for item in self.mastery_checklist:
            l.append(f"- [ ] {item}")
        l.append("")
        l.append("---")
        l.append("")
        
        return "\n".join(l)
