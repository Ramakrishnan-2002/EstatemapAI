import os, sys

def format_story(s):
    num = f"{s['num']:02d}"
    deps = ', '.join([f"Story {d:02d}" for d in s.get('depends_on', [])]) if s.get('depends_on') else 'None (Entry Point)'
    unls = ', '.join([f"Story {u:02d}" for u in s.get('unlocks', [])]) if s.get('unlocks') else 'None (Terminal Story)'
    
    lines = []
    lines.append(f"### Story {num} — {s['title']}")
    lines.append(f"* **Story Points**: {s['points']}")
    lines.append("* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered\n")
    
    lines.append("#### 1. Why This Story Exists")
    lines.append(s['why_exists'].strip() + "\n")
    
    lines.append("#### 2. Problem Being Solved")
    lines.append(s['problem_solved'].strip() + "\n")
    
    lines.append("#### 3. Prerequisites")
    req_s = ', '.join(s.get('prereq_stories', [])) if s.get('prereq_stories') else 'None'
    lines.append(f"- **Required Stories**: {req_s}")
    lines.append(f"- **Required Concepts**: {', '.join(s['prereq_concepts'])}")
    lines.append(f"- **Depends On**: {deps}")
    lines.append(f"- **Unlocks**: {unls}\n")
    
    lines.append("#### 4. Entry Readiness Check")
    for c in s['readiness']:
        lines.append(f"- [ ] {c}")
    lines.append("")
    
    lines.append("#### 5. Learning Objectives")
    for obj in s['objectives']:
        lines.append(f"- {obj}")
    lines.append("")
    
    lines.append("#### 6. Concepts to Master")
    for c in s['concepts']:
        lines.append(f"- {c}")
    lines.append("")
    
    lines.append("#### 7. EstateMap Implementation")
    lines.append(s['impl'].strip() + "\n")
    
    lines.append("#### 8. Files / Functions to Study")
    for f in s['files']:
        lines.append(f"- `{f}`")
    lines.append("")
    
    lines.append("#### 9. Request / Data Flow")
    lines.append(s['data_flow'].strip() + "\n")
    
    lines.append("#### 10. Build It Yourself")
    lines.append("**Standalone Lab:**")
    lines.append(s['lab_standalone'].strip() + "\n")
    lines.append("**EstateMap Codebase Mapping:**")
    lines.append(s['lab_mapping'].strip() + "\n")
    
    lines.append("#### 11. Acceptance Criteria")
    for i, ac in enumerate(s['acceptance_criteria'], 1):
        lines.append(f"- **AC{i}**: {ac}")
    lines.append("")
    
    lines.append("#### 12. Verification / Evidence")
    for v in s['evidence']:
        lines.append(f"- {v}")
    lines.append("")
    
    lines.append("#### 13. Final Outcome")
    lines.append(f"- **Conceptual Mastery**: {s['outcome_conceptual'].strip()}")
    lines.append(f"- **Implementation Capability**: {s['outcome_impl'].strip()}")
    lines.append(f"- **Interview Defense**: {s['outcome_interview'].strip()}\n")
    
    lines.append("#### 14. Common Mistakes")
    for m in s['mistakes']:
        lines.append(f"- {m}")
    lines.append("")
    
    lines.append("#### 15. Debugging Exercise")
    lines.append(f"- **Symptom**: {s['debug_symptom'].strip()}")
    lines.append(f"- **Investigate**: {s['debug_investigate'].strip()}")
    lines.append(f"- **Goal**: {s['debug_goal'].strip()}\n")
    
    lines.append("#### 16. Tradeoffs / Alternatives")
    for t in s['tradeoffs']:
        lines.append(f"- {t}")
    lines.append("")
    
    lines.append("#### 17. Production Considerations")
    lines.append(f"- **Current Implementation**: {s['prod_current'].strip()}")
    lines.append(f"- **At Scale**: {s['prod_scale'].strip()}\n")
    
    lines.append("#### 18. Interview Questions")
    lines.append(f"- **Basic Conceptual**: {s['q_basic'].strip()}")
    lines.append(f"- **Implementation Deep-Dive**: {s['q_impl'].strip()}")
    lines.append(f"- **Tradeoff / Architecture**: {s['q_tradeoff'].strip()}")
    lines.append(f"- **Debugging / Failure Mode**: {s['q_debug'].strip()}")
    lines.append(f"- **System Design Scenario**: {s['q_sysdesign'].strip()}\n")
    
    lines.append("#### 19. Interview Answer Framework")
    lines.append(s['ans_framework'].strip() + "\n")
    
    lines.append("#### 20. Connection to Previous Story")
    lines.append(s['conn_prev'].strip() + "\n")
    
    lines.append("#### 21. Connection to Next Story")
    lines.append(s['conn_next'].strip() + "\n")
    
    lines.append("#### 22. Mastery Checklist")
    for item in s['checklist']:
        lines.append(f"- [ ] {item}")
    lines.append("\n---\n")
    
    return '\n'.join(lines)
