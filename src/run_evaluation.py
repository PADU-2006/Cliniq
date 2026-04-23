import json
import sys
import time
sys.path.append(r'C:\Users\vinot\Projects\cliniq\src')

from rag_engine import ClinIQEngine

# ── Load engine ───────────────────────────────────────────
engine = ClinIQEngine()

# ── Load questions ────────────────────────────────────────
with open(r'C:\Users\vinot\Projects\cliniq\eval\questions.json') as f:
    questions = json.load(f)

# ── Trackers ──────────────────────────────────────────────
results        = []
latencies      = []

correct_answered   = 0   # answerable → got an answer (not abstained)
correct_abstained  = 0   # unanswerable → correctly said NOT FOUND

total_answerable   = sum(1 for q in questions if q['answerable'])
total_unanswerable = sum(1 for q in questions if not q['answerable'])

print("="*60)
print("CLINIQ — EVALUATION RUN")
print(f"Total questions : {len(questions)}")
print(f"Answerable      : {total_answerable}")
print(f"Unanswerable    : {total_unanswerable}")
print("="*60)

# ── Run all questions ─────────────────────────────────────
for q in questions:

    print(f"\nQ{q['id']:02d} | {q['question'][:55]}...")

    result = engine.query(q['question'])

    latencies.append(result['latency'])

    is_answerable = q['answerable']
    abstained     = result['abstained']

    # Score logic
    if is_answerable and not abstained:
        correct_answered += 1
        status = "✅ ANSWERED"
    elif not is_answerable and abstained:
        correct_abstained += 1
        status = "✅ CORRECTLY ABSTAINED"
    elif is_answerable and abstained:
        status = "❌ SHOULD HAVE ANSWERED"
    else:
        status = "❌ HALLUCINATED (should be NOT FOUND)"

    print(f"     Status  : {status}")
    print(f"     Latency : {result['latency']}s")
    print(f"     Answer  : {result['answer'][:80]}...")

    results.append({
        'id'          : q['id'],
        'question'    : q['question'],
        'answerable'  : is_answerable,
        'abstained'   : abstained,
        'status'      : status,
        'latency'     : result['latency'],
        'answer'      : result['answer'],
        'sources'     : [s['source'] for s in result['sources']]
    })

# ── Calculate final metrics ───────────────────────────────
accuracy         = (correct_answered  / total_answerable)   * 100
abstention_rate  = (correct_abstained / total_unanswerable) * 100

latencies_sorted = sorted(latencies)
p50 = latencies_sorted[len(latencies_sorted) // 2]
p95 = latencies_sorted[int(len(latencies_sorted) * 0.95)]

# ── Print summary ─────────────────────────────────────────
print("\n" + "="*60)
print("FINAL RESULTS")
print("="*60)
print(f"Answer Accuracy        : {accuracy:.1f}%   (target ≥70%)")
print(f"Abstention Correctness : {abstention_rate:.1f}%  (target 100%)")
print(f"Latency p50            : {p50:.1f}s")
print(f"Latency p95            : {p95:.1f}s")
print(f"Total queries run      : {len(questions)}")
print("="*60)

# ── Save results to file ──────────────────────────────────
summary = {
    'accuracy'        : round(accuracy, 2),
    'abstention_rate' : round(abstention_rate, 2),
    'p50_latency'     : round(p50, 2),
    'p95_latency'     : round(p95, 2),
    'total_questions' : len(questions),
    'details'         : results
}

with open(r'C:\Users\vinot\cliniq\eval\results.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("\nFull results saved → C:\\cliniq\\eval\\results.json")
print("Use these numbers directly in your Level 2 submission template.")