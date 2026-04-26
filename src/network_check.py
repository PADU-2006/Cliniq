import socket
import datetime
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__)))

print("=" * 55)
print("  CLINIQ — NETWORK ISOLATION VERIFICATION")
print(f"  {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 55)

# ── 1. Check Ollama is local ──────────────────────────────
print("\n[1] Checking Ollama...")
try:
    import ollama
    models  = ollama.list()
    names   = [m['model'] for m in models['models']]
    print(f"    ✅ Ollama running locally")
    print(f"    ✅ Models : {names}")
except Exception as e:
    print(f"    ❌ Ollama error : {e}")

# ── 2. Check ChromaDB is local ────────────────────────────
print("\n[2] Checking ChromaDB...")
try:
    import chromadb
    client     = chromadb.PersistentClient(
                    path=r'C:\Users\pband\OneDrive\Desktop\cliniciq\chroma_db')
    collection = client.get_collection("medical_docs")
    count      = collection.count()
    print(f"    ✅ ChromaDB running locally")
    print(f"    ✅ Total chunks in index : {count}")
except Exception as e:
    print(f"    ❌ ChromaDB error : {e}")

# ── 3. Check external APIs are blocked ───────────────────
print("\n[3] Testing external API endpoints...")
print("    (All should show BLOCKED)\n")

endpoints = [
    ('api.openai.com',    443, 'OpenAI API'),
    ('api.anthropic.com', 443, 'Anthropic API'),
    ('api.cohere.ai',     443, 'Cohere API'),
    ('api.together.xyz',  443, 'Together AI'),
    ('huggingface.co',    443, 'HuggingFace'),
]

all_blocked = True

for host, port, name in endpoints:
    try:
        socket.setdefaulttimeout(3)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
        print(f"    ⚠️  {name:20s} — REACHABLE (turn on Airplane Mode!)")
        all_blocked = False
    except:
        print(f"    ✅ {name:20s} — BLOCKED")

# ── 4. Verdict ────────────────────────────────────────────
print("\n" + "=" * 55)
if all_blocked:
    print("  ✅ VERDICT : FULLY OFFLINE")
    print("  Zero external API access confirmed.")
    print("  Safe to run demo.")
else:
    print("  ⚠️  VERDICT : NOT FULLY OFFLINE")
    print("  → Enable Airplane Mode then run this again.")
print("=" * 55)

# ── 5. Save log ───────────────────────────────────────────
os.makedirs(r'C:\Users\pband\OneDrive\Desktop\clinic\eval', exist_ok=True)

log = {
    'timestamp'          : str(datetime.datetime.now()),
    'verdict'            : 'OFFLINE' if all_blocked else 'NOT OFFLINE',
    'all_blocked'        : all_blocked,
    'endpoints_checked'  : [e[2] for e in endpoints]
}

with open(r'C:\Users\pband\OneDrive\Desktop\clinic\eval\network_log.json', 'w') as f:
    json.dump(log, f, indent=2)

print("\n  Log saved → eval/network_log.json")
print("  Screenshot this output for your submission.\n")
