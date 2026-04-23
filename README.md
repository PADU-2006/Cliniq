# ClinIQ — Local Medical Document Intelligence

**TNSDC Naan Mudhalvan 2026 Advanced AI/ML Hackathon**
**Problem Statement 02 — Healthcare AI · On-premises Intelligence**

> A fully offline, privacy-preserving RAG pipeline that lets clinicians
> in Tamil Nadu hospitals query patient records in natural language —
> with zero patient data leaving the hospital network.

---

## The Problem

Clinicians in Tamil Nadu hospitals spend 20–30 minutes per shift
manually searching through unstructured clinical documents.
Cloud-based AI tools are legally blocked under India's DPDP Act 2023.
No existing tool can search free-text clinical notes by meaning.

## Our Solution

ClinIQ is a fully local Retrieval-Augmented Generation system.
The doctor types a question. The system searches 100+ local medical
documents using hybrid search, then a locally running LLM generates
a cited answer. Everything runs on the hospital's own hardware.
No internet. No cloud. No data leaves the machine.

---

## Tech Stack

| Component      | Tool                          |
|----------------|-------------------------------|
| LLM            | Phi-3 Mini via Ollama (local) |
| Embeddings     | BioBERT (BioSentenceBERT)     |
| Vector DB      | ChromaDB (local)              |
| Keyword Search | BM25 (rank-bm25)              |
| UI             | Streamlit                     |
| Dataset        | MTSamples (Kaggle)            |
| Language       | Python 3.10                   |

---

## Project Structure

```
cliniq/
├── src/
│   ├── prepare_corpus.py     # Download + save 100 documents
│   ├── chunker.py            # Medical-aware text splitter
│   ├── build_index.py        # Build ChromaDB vector index
│   ├── rag_engine.py         # Core RAG pipeline (ML)
│   ├── app.py                # Streamlit UI (Frontend)
│   ├── run_evaluation.py     # 30-question evaluation
│   └── network_check.py      # Offline verification
├── eval/
│   └── questions.json        # 30 evaluation questions
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup — Run This Once

### 1. Clone the repository
```bash
git clone https://github.com/VinothanaBalakrishnan05/cliniq.git
cd cliniq
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Ollama
Download from https://ollama.com and install.
Then pull the model:
```bash
ollama pull phi3:mini-q4_0
```

### 4. Download the dataset
- Go to https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions
- Download `mtsamples.csv`
- Place it inside `data/` folder

### 5. Prepare the corpus
```bash
python src/prepare_corpus.py
```
Saves 100 clinical documents into `corpus/`

### 6. Build the vector index
```bash
python src/build_index.py
```
Takes ~20 minutes on CPU. Run once only.
Stores the index in `chroma_db/`

---

## Run the App

Start Ollama in one terminal:
```bash
ollama serve
```

Start the app in another terminal:
```bash
streamlit run src/app.py
```

Opens at http://localhost:8501

---

## Run Evaluation
```bash
python src/run_evaluation.py
```
Runs 30 clinical questions automatically.
Saves results to `eval/results.json`

---

## Verify Offline Mode
```bash
# Turn on Windows Airplane Mode first, then:
python src/network_check.py
```
Screenshot the output for submission proof.

---

## Evaluation Results

| Metric                  | Score         | Target   |
|-------------------------|---------------|----------|
| Answer Accuracy         | TBD%          | ≥ 70%    |
| Abstention Correctness  | TBD%          | 100%     |
| Latency p50             | TBDs          | < 60s    |
| Latency p95             | TBDs          | < 60s    |
| Network Isolation       | ✅ Verified   | Zero API |




---

## Compliance

- Zero external API calls during inference
- All model weights stored locally on device
- Patient data never leaves the hospital machine
- Fully compliant with DPDP Act 2023
- Network isolation verified and logged

---

## Team

| Name | Role |
|------|------|
| [Nikitha] | System Architect |
| [Vinothana] | ML Engineer |
| [Anfi Jo Rajan] | Backend Developer |
| [Padmini] | Frontend Developer |
| [Kaviyanjali] | Testing & Research |

---

## Problem Statement

**PS02 — Belsterns Technologies / Bot Ventures Private Limited**
Healthcare AI — On-premises Intelligence
TNSDC Naan Mudhalvan 2026 Advanced AI/ML Hackathon