import pandas as pd
import os

df = pd.read_csv('data/mtsamples.csv')

# Strip whitespace from the specialty column
df['medical_specialty'] = df['medical_specialty'].str.strip()

type_map = {
    'Discharge Summary': 'discharge_summary',
    'Lab Medicine - Pathology': 'lab_report',
    'Consult - History and Phy.': 'consultation_note',
    'General Medicine': 'treatment_protocol'
}

selected = []
for specialty, doc_type in type_map.items():
    subset = df[df['medical_specialty'] == specialty].head(25).copy()
    print(f"{specialty}: {len(subset)} rows found")  # verify each type matches
    subset['doc_type'] = doc_type
    selected.append(subset)

corpus = pd.concat(selected).reset_index(drop=True)
corpus = corpus[['sample_name', 'transcription', 'doc_type', 'medical_specialty']]
corpus = corpus.dropna(subset=['transcription'])

print(f"\nTotal rows after dropna: {len(corpus)}")

os.makedirs('corpus', exist_ok=True)
for i, row in corpus.iterrows():
    filename = f"doc_{i:03d}_{row['doc_type']}.txt"
    filepath = os.path.join('corpus', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"DOCUMENT TYPE: {row['doc_type']}\n")
        f.write(f"TITLE: {row['sample_name']}\n")
        f.write("---\n")
        f.write(row['transcription'])

print(f"Saved {len(corpus)} documents to corpus folder")