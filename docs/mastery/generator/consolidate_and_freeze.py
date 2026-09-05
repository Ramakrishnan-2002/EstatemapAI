# -*- coding: utf-8 -*-
import os, sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
MASTERY_DIR = os.path.join(BASE_DIR, 'docs', 'mastery')

def read_file(name):
    path = os.path.join(MASTERY_DIR, name)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

def write_file(name, content):
    path = os.path.join(MASTERY_DIR, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Wrote {name} ({len(content)} bytes)')

def consolidate():
    print('Consolidating ARCHITECTURE.md...')
    canon = read_file('CANONICAL_ARCHITECTURE_TRUTH.md')
    if canon:
        write_file('ARCHITECTURE.md', f'# EstateMap AI — Canonical Architecture Truth & System Topology\n> **Document Status: Authoritative Architecture Specification (Canonical Truth)**\n\n{canon}\n')

    print('Consolidating MASTER_BOOK.md...')
    book = read_file('ESTATEMAP_MASTER_BOOK.md')
    if book:
        write_file('MASTER_BOOK.md', f'# EstateMap AI — System Design Master Book & Engineering Guide\n> **Document Status: Authoritative Textbook & System Design Case Study**\n\n{book}\n')

    print('Consolidating KNOW_YOUR_CODE.md...')
    inv = read_file('01-SYSTEM-INVENTORY.md')
    flows = read_file('DATA_FLOWS.md')
    traces = read_file('REQUEST_TRACES.md')
    write_file('KNOW_YOUR_CODE.md', f'# EstateMap AI — Codebase Inventory & Request Execution Traces\n> **Document Status: Authoritative Code Navigation & Request Tracing Guide**\n\n# Part 1: Complete Codebase Inventory & Symbol Catalog\n\n{inv}\n\n---\n\n# Part 2: End-to-End Data Flows & State Lifecycles\n\n{flows}\n\n---\n\n# Part 3: Step-by-Step Request Execution Traces\n\n{traces}\n')

    print('Consolidating SYSTEM_DESIGN_AND_TRADEOFFS.md...')
    tradeoffs = read_file('TRADEOFF_MATRIX.md')
    tech_matrix = read_file('TECHNOLOGY_NECESSITY_MATRIX.md')
    failures = read_file('FAILURE_MODES.md')
    perf = read_file('PERFORMANCE_AND_SCALABILITY.md')
    scaling = read_file('PRODUCTION_EVOLUTION.md')
    adrs = read_file('ADR_MASTER_INDEX.md')
    write_file('SYSTEM_DESIGN_AND_TRADEOFFS.md', f'# EstateMap AI — System Design, Tradeoffs & Architectural Decisions\n> **Document Status: Authoritative Tradeoff Analysis, Failure Modes, and ADR Index**\n\n# Part 1: Engineering Tradeoff Matrix (15 Core Architectural Decisions)\n\n{tradeoffs}\n\n---\n\n# Part 2: Technology Necessity Matrix (Why Each Component Is Essential)\n\n{tech_matrix}\n\n---\n\n# Part 3: Failure Modes, System Impact & Resiliency Mitigations\n\n{failures}\n\n---\n\n# Part 4: Performance Benchmarks & Service Level Objectives (SLOs)\n\n{perf}\n\n---\n\n# Part 5: Production Scaling Evolution (10k → 1M Concurrent Users)\n\n{scaling}\n\n---\n\n# Part 6: Architecture Decision Record (ADR) Master Index\n\n{adrs}\n')

    print('Consolidating INTERVIEW_PREP.md...')
    pitch = read_file('PROJECT_PITCH.md')
    questions = read_file('INTERVIEW_QUESTIONS.md')
    answers = read_file('INTERVIEW_ANSWERS.md')
    red_flags = read_file('INTERVIEW_RED_FLAGS.md')
    mock = read_file('MOCK_INTERVIEW.md')
    sys_interview = read_file('SYSTEM_DESIGN_INTERVIEW.md')
    write_file('INTERVIEW_PREP.md', f'# EstateMap AI — Senior Backend & System Design Interview Preparation Master Guide\n> **Document Status: Comprehensive Interview Preparation Resource**\n\n# Part 1: Project Elevator Pitches (30s, 2m, 5m Architecture Walk)\n\n{pitch}\n\n---\n\n# Part 2: Top 25 Backend & System Design Interview Questions\n\n{questions}\n\n---\n\n# Part 3: Deep Technical Interview Answers (30s Quick + 2m Comprehensive STAR Format)\n\n{answers}\n\n---\n\n# Part 4: 12 Interview Red Flags to Avoid & High-Signal Behavioral Responses\n\n{red_flags}\n\n---\n\n# Part 5: Complete Mock Interview Transcript (Senior Backend / SDE III)\n\n{mock}\n\n---\n\n# Part 6: System Design Interview Blueprint & Whiteboard Drills\n\n{sys_interview}\n')

    print('Consolidating ACTIVE_RECALL.md...')
    recall = read_file('ACTIVE_RECALL.md')
    answers = read_file('ACTIVE_RECALL_ANSWERS.md')
    labs = read_file('DEBUGGING_LABS.md')
    rebuild = read_file('REBUILD_CHALLENGES.md')
    write_file('ACTIVE_RECALL.md', f'# EstateMap AI — Active Recall Drills, Debugging Labs & Rebuild Challenges\n> **Document Status: Interactive Self-Testing & Practical Engineering Exercises**\n\n# Part 1: Active Recall Self-Testing Drills (50 Questions)\n\n{recall}\n\n---\n\n# Part 2: Comprehensive Active Recall Answer Keys\n\n{answers}\n\n---\n\n# Part 3: Live Debugging Labs (Break-It & Fix-It Scenarios)\n\n{labs}\n\n---\n\n# Part 4: Clean-Slate Rebuild Challenges\n\n{rebuild}\n')

    print('Deleting redundant files...')
    redundant_files = [
        '01-SYSTEM-INVENTORY.md', 'ACTIVE_RECALL_ANSWERS.md', 'ADR_MASTER_INDEX.md',
        'CANONICAL_ARCHITECTURE_TRUTH.md', 'CLAIM_EVIDENCE_MATRIX.md', 'combined_output.md',
        'DATA_FLOWS.md', 'DEBUGGING_LABS.md', 'ESTATEMAP_MASTER_BOOK.md', 'FAILURE_MODES.md',
        'INTERVIEW_ANSWERS.md', 'INTERVIEW_QUESTIONS.md', 'INTERVIEW_RED_FLAGS.md',
        'MOCK_INTERVIEW.md', 'PERFORMANCE_AND_SCALABILITY.md', 'PRODUCTION_EVOLUTION.md',
        'PROJECT_PITCH.md', 'REBUILD_CHALLENGES.md', 'REQUEST_TRACES.md',
        'SYSTEM_DESIGN_INTERVIEW.md', 'TECHNOLOGY_NECESSITY_MATRIX.md', 'TRADEOFF_MATRIX.md'
    ]
    for rf in redundant_files:
        p = os.path.join(MASTERY_DIR, rf)
        if os.path.exists(p):
            os.remove(p)
            print(f'Removed {rf}')

if __name__ == '__main__':
    consolidate()
