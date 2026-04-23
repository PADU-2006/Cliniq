import os
import chromadb
from sentence_transformers import SentenceTransformer
from chunker import chunk_document
import time

# Load BioSentenceBERT — runs locally, no internet needed at demo
print("Loading embedding model...")
embedder = SentenceTransformer('pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb')
# Alternative if above fails: 'sentence-transformers/all-MiniLM-L6-v2'

# Setup ChromaDB (local, stored on disk)
client = chromadb.PersistentClient(path=r'\Users\vinot\Projects\cliniq\chroma_db')

# Delete and recreate collection (fresh start)
try:
    client.delete_collection("medical_docs")
except:
    pass
collection = client.create_collection("medical_docs")

# Load all documents from corpus folder
corpus_dir = r'C:\Users\vinot\Projects\cliniq\corpus'
all_files = [f for f in os.listdir(corpus_dir) if f.endswith('.txt')]

print(f"Found {len(all_files)} documents. Building index...")

all_chunks = []
all_ids = []
all_embeddings = []
all_metadata = []

for file_idx, filename in enumerate(all_files):
    filepath = os.path.join(corpus_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Get doc type from filename
    doc_type = 'unknown'
    for dtype in ['discharge_summary', 'lab_report', 'consultation_note', 'treatment_protocol']:
        if dtype in filename:
            doc_type = dtype
            break
    
    # Chunk this document
    chunks = chunk_document(text, doc_type, filename)
    
    for chunk in chunks:
        chunk_id = f"{filename}_chunk{chunk['chunk_index']}"
        all_chunks.append(chunk['text'])
        all_ids.append(chunk_id)
        all_metadata.append({
            'doc_id': filename,
            'doc_type': doc_type,
            'chunk_index': chunk['chunk_index']
        })
    
    if (file_idx + 1) % 10 == 0:
        print(f"  Processed {file_idx + 1}/{len(all_files)} documents...")

# Generate embeddings in batches
print("Generating embeddings (this takes ~10-20 mins on CPU)...")
batch_size = 32

for i in range(0, len(all_chunks), batch_size):
    batch = all_chunks[i:i+batch_size]
    batch_ids = all_ids[i:i+batch_size]
    batch_meta = all_metadata[i:i+batch_size]
    
    embeddings = embedder.encode(batch, show_progress_bar=False).tolist()
    
    collection.add(
        documents=batch,
        embeddings=embeddings,
        ids=batch_ids,
        metadatas=batch_meta
    )
    
    if (i // batch_size + 1) % 5 == 0:
        print(f"  Embedded {min(i+batch_size, len(all_chunks))}/{len(all_chunks)} chunks...")

print(f"\nDONE! Index built with {len(all_chunks)} total chunks from {len(all_files)} documents.")
print("Saved to C:\\cliniq\\chroma_db\\")