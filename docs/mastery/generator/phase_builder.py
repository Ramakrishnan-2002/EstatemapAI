# -*- coding: utf-8 -*-
import os, sys

def make_story(num, title, points, why, problem, req_s, req_c, deps, unls, readiness, objs, concepts, impl, files, data_flow, lab_s, lab_m, acs, evidence, out_c, out_i, out_v, mistakes, d_sym, d_inv, d_goal, tradeoffs, prod_c, prod_s, q_b, q_i, q_t, q_d, q_s, ans_f, conn_p, conn_n, chk):
    return {
        'num': num,
        'title': title,
        'points': points,
        'why_exists': why,
        'problem_solved': problem,
        'prereq_stories': req_s,
        'prereq_concepts': req_c,
        'depends_on': deps,
        'unlocks': unls,
        'readiness': readiness,
        'objectives': objs,
        'concepts': concepts,
        'impl': impl,
        'files': files,
        'data_flow': data_flow,
        'lab_standalone': lab_s,
        'lab_mapping': lab_m,
        'acceptance_criteria': acs,
        'evidence': evidence,
        'outcome_conceptual': out_c,
        'outcome_impl': out_i,
        'outcome_interview': out_v,
        'mistakes': mistakes,
        'debug_symptom': d_sym,
        'debug_investigate': d_inv,
        'debug_goal': d_goal,
        'tradeoffs': tradeoffs,
        'prod_current': prod_c,
        'prod_scale': prod_s,
        'q_basic': q_b,
        'q_impl': q_i,
        'q_tradeoff': q_t,
        'q_debug': q_d,
        'q_sysdesign': q_s,
        'ans_framework': ans_f,
        'conn_prev': conn_p,
        'conn_next': conn_n,
        'checklist': chk
    }

print('phase_builder.py initialized')
