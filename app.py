import streamlit as st
import time

# ---------------- Mock Engine ----------------
class ClinIQEngine:
    def query(self, query):
        time.sleep(1)

        sample_answers = {
            "What medications were prescribed for hypertension?": {
                "answer": "The patient was prescribed Amlodipine 5mg once daily and Losartan 50mg once daily.",
                "sources": [
                    {
                        "source": "prescription.pdf",
                        "doc_type": "Prescription",
                        "score": 0.91,
                        "text": "Patient diagnosed with hypertension. Prescribed Amlodipine 5mg OD and Losartan 50mg OD."
                    }
                ],
                "abstained": False,
                "latency": 2.4
            },
            "What is the patient's history of diabetes?": {
                "answer": "Patient has Type 2 Diabetes since 2019 and is taking Metformin 500mg twice daily.",
                "sources": [
                    {
                        "source": "history_report.pdf",
                        "doc_type": "Medical History",
                        "score": 0.88,
                        "text": "Patient diagnosed with Type 2 Diabetes in 2019. Metformin prescribed."
                    }
                ],
                "abstained": False,
                "latency": 1.8
            },
            "What were the lab results for CBC?": {
                "answer": "Hemoglobin: 12.4 g/dL, WBC: 8500 cells/mm³, Platelets: 2.3 lakh/mm³.",
                "sources": [
                    {
                        "source": "lab_report.pdf",
                        "doc_type": "Lab Report",
                        "score": 0.93,
                        "text": "CBC report shows Hemoglobin 12.4, WBC 8500, Platelets 2.3 lakh."
                    }
                ],
                "abstained": False,
                "latency": 2.1
            }
        }

        return sample_answers.get(query, {
            "answer": "No relevant medical document found for this query.",
            "sources": [],
            "abstained": True,
            "latency": 1.2
        })


# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="ClinIQ", page_icon="🏥", layout="wide")

@st.cache_resource
def load_engine():
    return ClinIQEngine()

st.title("🏥 ClinIQ")
st.caption("Fully Offline · DPDP Act Compliant · Zero data leaves this machine")

with st.sidebar:
    st.header("Settings")
    role = st.selectbox("Select Role", ["Doctor", "Nurse", "Admin"])

    st.divider()
    st.markdown("**System Status**")
    st.error("🔴 Network: OFFLINE")
    st.success("✅ LLM : Phi-3 Mini (Mock)")
    st.success("✅ DB  : ChromaDB (Mock)")
    st.success("✅ Embed: BioBERT (Mock)")

with st.spinner("Loading AI engine..."):
    engine = load_engine()

st.success("Engine ready. Ask a clinical question below.")

query = st.text_input(
    "Type your clinical question:",
    placeholder="e.g. What medications were prescribed for hypertension?"
)

if st.button("🔍 Search") and query:
    result = engine.query(query)

    st.subheader("Answer")

    if result['abstained']:
        st.warning(result['answer'])
    else:
        st.success(result['answer'])

    col1, col2, col3 = st.columns(3)
    col1.metric("Response Time", f"{result['latency']}s")
    col2.metric("Sources Found", len(result['sources']))
    col3.metric("Status", "NOT FOUND" if result['abstained'] else "ANSWERED")

    if result['sources']:
        st.subheader("Source Documents")
        for i, chunk in enumerate(result['sources']):
            with st.expander(f"Source {i+1} - {chunk['source']}"):
                st.write(chunk['text'])

st.subheader("Example Questions")
examples = [
    "What medications were prescribed for hypertension?",
    "What is the patient's history of diabetes?",
    "What were the lab results for CBC?",
    "What is the hospital MRI machine serial number?"
]

for ex in examples:
    st.code(ex)
