# -*- coding: utf-8 -*-
"""
EstateMap AI — Procedural Story Expansion & Rendering Engine
Enforces 100% compliance with the 22-section Master Contract.
"""

def build_full_story(d):
    num = d['num']
    num_str = f"{num:02d}"
    title = d['title']
    points = d['points']
    why = d['why']
    problem = d['problem']
    deps = d.get('deps', [])
    unls = d.get('unls', [])
    req_s = d.get('req_stories', [])
    req_c = d.get('req_concepts', [])
    files = d.get('files', [])
    impl = d['impl']
    data_flow = d.get('data_flow', '')
    lab = d.get('lab', '')
    acs = d.get('acs', [])
    evidence = d.get('evidence', [])
    mistakes = d.get('mistakes', [])
    debug = d.get('debug', {})
    tradeoffs = d.get('tradeoffs', [])
    prod = d.get('prod', {})
    iq = d.get('iq', {})
    ans = d.get('ans', '')
    prev_s = d.get('prev_s', '')
    next_s = d.get('next_s', '')
    checklist = d.get('checklist', [])
    concepts = d.get('concepts', [])
    objectives = d.get('objectives', [])
    readiness = d.get('readiness', [])
    outcomes = d.get('outcomes', {})

    dep_str = ", ".join([f"Story {x:02d}" for x in deps]) if deps else "None (Entry Point)"
    unl_str = ", ".join([f"Story {x:02d}" for x in unls]) if unls else "None (Terminal Story)"
    req_s_str = ", ".join(req_s) if req_s else "None"

    lines = []
    lines.append(f"### Story {num_str} — {title}")
    lines.append(f"* **Story Points**: {points}")
    lines.append("* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered\n")

    # 1. Why This Story Exists
    lines.append("#### 1. Why This Story Exists")
    lines.append(why.strip() + "\n")

    # 2. Problem Being Solved
    lines.append("#### 2. Problem Being Solved")
    lines.append(problem.strip() + "\n")

    # 3. Prerequisites
    lines.append("#### 3. Prerequisites")
    lines.append(f"- **Required Stories**: {req_s_str}")
    lines.append(f"- **Required Concepts**: {', '.join(req_c)}")
    lines.append(f"- **Depends On**: {dep_str}")
    lines.append(f"- **Unlocks**: {unl_str}\n")

    # 4. Entry Readiness Check
    lines.append("#### 4. Entry Readiness Check")
    for r in readiness:
        lines.append(f"- [ ] {r}")
    lines.append("")

    # 5. Learning Objectives
    lines.append("#### 5. Learning Objectives")
    for obj in objectives:
        lines.append(f"- {obj}")
    lines.append("")

    # 6. Concepts to Master
    lines.append("#### 6. Concepts to Master")
    for c in concepts:
        lines.append(f"- {c}")
    lines.append("")

    # 7. EstateMap Implementation
    lines.append("#### 7. EstateMap Implementation")
    lines.append(impl.strip() + "\n")

    # 8. Files / Functions to Study
    lines.append("#### 8. Files / Functions to Study")
    for f in files:
        lines.append(f"- `{f}`")
    lines.append("")

    # 9. Request / Data Flow
    lines.append("#### 9. Request / Data Flow")
    lines.append(data_flow.strip() + "\n")

    # 10. Build It Yourself
    lines.append("#### 10. Build It Yourself")
    lines.append(f"**Standalone Lab:**\n{lab.strip()}\n")
    lines.append(f"**EstateMap Codebase Mapping:**\nInspect `{files[0] if files else 'backend/app/'}` to see the production implementation in action.\n")

    # 11. Acceptance Criteria
    lines.append("#### 11. Acceptance Criteria")
    for i, ac in enumerate(acs, 1):
        lines.append(f"- **AC{i}**: {ac}")
    lines.append("")

    # 12. Verification / Evidence
    lines.append("#### 12. Verification / Evidence")
    for ev in evidence:
        lines.append(f"- {ev}")
    lines.append("")

    # 13. Final Outcome
    lines.append("#### 13. Final Outcome")
    lines.append(f"- **Conceptual Mastery**: {outcomes.get('conceptual', 'Deep understanding of core engineering principles.')}")
    lines.append(f"- **Implementation Capability**: {outcomes.get('implementation', 'Ability to implement this subsystem from scratch.')}")
    lines.append(f"- **Interview Defense**: {outcomes.get('interview', 'Ability to defend architectural tradeoffs and failure modes.')}\n")

    # 14. Common Mistakes
    lines.append("#### 14. Common Mistakes")
    for m in mistakes:
        lines.append(f"- {m}")
    lines.append("")

    # 15. Debugging Exercise
    lines.append("#### 15. Debugging Exercise")
    lines.append(f"- **Symptom**: {debug.get('symptom', 'Observable failure mode.')}")
    lines.append(f"- **Investigate**: {debug.get('investigate', 'Steps to isolate root cause.')}")
    lines.append(f"- **Goal**: {debug.get('goal', 'Resolution and preventive safeguards.')}\n")

    # 16. Tradeoffs / Alternatives
    lines.append("#### 16. Tradeoffs / Alternatives")
    for t in tradeoffs:
        lines.append(f"- {t}")
    lines.append("")

    # 17. Production Considerations
    lines.append("#### 17. Production Considerations")
    lines.append(f"- **Current Implementation**: {prod.get('current', 'Production-ready baseline in Docker.')}")
    lines.append(f"- **At Scale**: {prod.get('scale', 'Horizontal scaling and distributed caching.')}\n")

    # 18. Interview Questions
    lines.append("#### 18. Interview Questions")
    lines.append(f"- **Basic Conceptual**: {iq.get('basic', 'Core concept explanation.')}")
    lines.append(f"- **Implementation Deep-Dive**: {iq.get('impl', 'Specific implementation detail.')}")
    lines.append(f"- **Tradeoff / Architecture**: {iq.get('tradeoff', 'Design tradeoff analysis.')}")
    lines.append(f"- **Debugging / Failure Mode**: {iq.get('debug', 'Diagnosing edge-case failure.')}")
    lines.append(f"- **System Design Scenario**: {iq.get('sysdesign', 'Scaling to high throughput.')}\n")

    # 19. Interview Answer Framework
    lines.append("#### 19. Interview Answer Framework")
    lines.append(ans.strip() + "\n")

    # 20. Connection to Previous Story
    lines.append("#### 20. Connection to Previous Story")
    lines.append(prev_s.strip() + "\n")

    # 21. Connection to Next Story
    lines.append("#### 21. Connection to Next Story")
    lines.append(next_s.strip() + "\n")

    # 22. Mastery Checklist
    lines.append("#### 22. Mastery Checklist")
    for chk in checklist:
        lines.append(f"- [ ] {chk}")
    lines.append("\n---\n")

    return "\n".join(lines)
