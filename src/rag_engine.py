import chromadb
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import ollama
import json
import time
import os

from shapely import distance

class ClinIQEngine:
    def __init__(self):
        print("Loading ClinIQ Engine...")
        
        # Load embedding model
        self.embedder = SentenceTransformer('pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb')
        
        # Load ChromaDB
        self.client = chromadb.PersistentClient(path=r'C:\Users\vinot\Projects\cliniq\chroma_db')
        self.collection = self.client.get_collection("medical_docs")
        
        # Build BM25 index (keyword search)
        print("Building BM25 keyword index...")
        self._build_bm25()
        
        print("Engine ready!")
    
    def _build_bm25(self):
        """Build BM25 keyword search index from all stored chunks."""
        results = self.collection.get(include=['documents', 'metadatas'])
        self.all_docs = results['documents']
        self.all_ids = results['ids']
        self.all_meta = results['metadatas']
        
        # Tokenize for BM25
        tokenized = [doc.lower().split() for doc in self.all_docs]
        self.bm25 = BM25Okapi(tokenized)
    
    def retrieve(self, query, top_k=5):
        """Hybrid retrieval: BM25 + Vector search merged."""
        
        # --- Vector Search ---
        query_embedding = self.embedder.encode([query]).tolist()
        vector_results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=10,
            include=['documents', 'metadatas', 'distances']
        )
        
        vector_scores = {}
        for i, doc_id in enumerate(vector_results['ids'][0]):
               # Normalize distance to 0-1 score properly
               distance = vector_results['distances'][0][i]
               score = 1 / (1 + distance)   # always gives value between 0 and 1
               vector_scores[doc_id] = {
                   'text': vector_results['documents'][0][i],
                    'meta': vector_results['metadatas'][0][i],
                    'vector_score': score
            }
        
        # --- BM25 Keyword Search ---
        tokenized_query = query.lower().split()
        bm25_scores_raw = self.bm25.get_scores(tokenized_query)
        
        # Get top 10 BM25 results
        top_bm25_indices = sorted(range(len(bm25_scores_raw)), 
                                   key=lambda i: bm25_scores_raw[i], 
                                   reverse=True)[:10]
        
        bm25_max = max(bm25_scores_raw) if max(bm25_scores_raw) > 0 else 1
        
        # --- Reciprocal Rank Fusion ---
        combined = {}
        
        # Add vector scores
        for rank, doc_id in enumerate(vector_results['ids'][0]):
            combined[doc_id] = combined.get(doc_id, 0) + 1/(rank + 1)
        
        # Add BM25 scores
        for rank, idx in enumerate(top_bm25_indices):
            doc_id = self.all_ids[idx]
            combined[doc_id] = combined.get(doc_id, 0) + 1/(rank + 1)
            if doc_id not in vector_scores:
                vector_scores[doc_id] = {
                    'text': self.all_docs[idx],
                    'meta': self.all_meta[idx],
                    'vector_score': bm25_scores_raw[idx] / bm25_max
                }
        
        # Sort by combined RRF score
        top_ids = sorted(combined.keys(), key=lambda x: combined[x], reverse=True)[:top_k]
        
        results = []
        for doc_id in top_ids:
            info = vector_scores[doc_id]
            results.append({
                'text': info['text'],
                'source': info['meta']['doc_id'],
                'doc_type': info['meta']['doc_type'],
                'score': combined[doc_id],
                'vector_score': info['vector_score']
            })
        
        return results
    
    def check_confidence(self, results, threshold=0.05):
        """Return False (low confidence) if best chunk is too far from query."""
        if not results:
            return False
        best_score = max(chunk['vector_score'] for chunk in results)
        return best_score >= threshold
    
    def generate_answer(self, query, retrieved_chunks):
        """Generate a cited answer using Phi-3 Mini via Ollama."""
        
        # Build context from retrieved chunks
        context = ""
        for i, chunk in enumerate(retrieved_chunks):
            context += f"\n[SOURCE {i+1}: {chunk['source']} | Type: {chunk['doc_type']}]\n"
            context += chunk['text'] + "\n"
        
        prompt = f"""You are a clinical document assistant for a hospital in Tamil Nadu. 
Answer the question ONLY using the provided context.

STRICT RULES:
1. If the answer is in the context, give a clear answer and cite the source like [SOURCE 1]
2. If the answer is NOT clearly in the context, respond EXACTLY: "NOT FOUND: This information is not available in the retrieved documents."
3. Never invent drug dosages, diagnoses, or patient information
4. Be concise and clinical

CONTEXT:
{context}

QUESTION: {query}

ANSWER:"""
        
        start_time = time.time()
        
        response = ollama.chat(
            model='phi3:mini',
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.1, 'num_predict': 300}
        )
        
        latency = time.time() - start_time
        answer = response['message']['content']
        
        return answer, latency
    
    def query(self, question):
        """Full RAG pipeline for one question."""
        
        # Step 1: Retrieve
        chunks = self.retrieve(question, top_k=5)
        
        # Step 2: Confidence check — abstain if nothing relevant found
        if not self.check_confidence(chunks):
            return {
                'answer': 'NOT FOUND: No relevant documents found in the corpus for this query.',
                'sources': [],
                'latency': 0,
                'abstained': True
            }
        
        # Step 3: Generate
        answer, latency = self.generate_answer(question, chunks)
        
        # Step 4: Check if model itself said NOT FOUND
        abstained = 'NOT FOUND' in answer.upper()
        
        return {
            'answer': answer,
            'sources': chunks,
            'latency': round(latency, 2),
            'abstained': abstained
        }