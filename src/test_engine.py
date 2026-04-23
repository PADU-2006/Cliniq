import sys
sys.path.append(r'C:\Users\vinot\Projects\cliniq\src')

from rag_engine import ClinIQEngine

print("Loading engine...")
engine = ClinIQEngine()

# ── Debug: see raw scores first ───────────────────────────
print("\n--- DEBUG: Raw chunk scores ---")
chunks = engine.retrieve("What medications were prescribed for hypertension?")
for i, c in enumerate(chunks):
    print(f"  Chunk {i+1} | vector_score: {c['vector_score']:.4f} | source: {c['source']}")

# ── Real query ────────────────────────────────────────────
print("\nRunning full query...")
result = engine.query("What medications were prescribed for hypertension?")

print("\n--- RESULTS ---")
print("Answer   :", result['answer'])
print("Latency  :", result['latency'], "seconds")
print("Abstained:", result['abstained'])

if result['sources']:
    print("Source   :", result['sources'][0]['source'])
else:
    print("Source   : Empty (still abstaining - check scores above)")