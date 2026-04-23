import re

# Medical abbreviation expander
ABBREV_MAP = {
    'SOB': 'shortness of breath',
    'HTN': 'hypertension',
    'DM2': 'type 2 diabetes mellitus',
    'DM': 'diabetes mellitus',
    'CABG': 'coronary artery bypass graft',
    'MI': 'myocardial infarction',
    'CHF': 'congestive heart failure',
    'COPD': 'chronic obstructive pulmonary disease',
    'hx': 'history',
    'h/o': 'history of',
    'c/o': 'complains of',
    'k/o': 'known case of',
    'prn': 'as needed',
    'qid': 'four times daily',
    'bid': 'twice daily',
    'tid': 'three times daily',
    'SPO2': 'oxygen saturation',
    'GRBS': 'glucometer random blood sugar',
    'BP': 'blood pressure',
    'HR': 'heart rate',
    'RR': 'respiratory rate',
}

def expand_abbreviations(text):
    """Expand medical abbreviations for better search."""
    for abbrev, full_form in ABBREV_MAP.items():
        # Replace whole-word abbreviations only
        pattern = r'\b' + re.escape(abbrev) + r'\b'
        text = re.sub(pattern, f"{abbrev} ({full_form})", text, flags=re.IGNORECASE)
    return text

def chunk_document(text, doc_type, doc_id, chunk_size=400, overlap=80):
    """
    Smart chunker that:
    - Splits by sentences (not arbitrary tokens)
    - Preserves drug/dosage entities together
    - Adds overlap between chunks
    """
    # Expand abbreviations first
    text = expand_abbreviations(text)
    
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = []
    current_len = 0
    
    for sentence in sentences:
        sentence_words = len(sentence.split())
        
        # If adding this sentence exceeds chunk_size, save current chunk
        if current_len + sentence_words > chunk_size and current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'doc_id': doc_id,
                'doc_type': doc_type,
                'chunk_index': len(chunks)
            })
            
            # Keep last few sentences as overlap
            overlap_sentences = current_chunk[-3:]
            current_chunk = overlap_sentences
            current_len = sum(len(s.split()) for s in overlap_sentences)
        
        current_chunk.append(sentence)
        current_len += sentence_words
    
    # Add final chunk
    if current_chunk:
        chunk_text = ' '.join(current_chunk)
        chunks.append({
            'text': chunk_text,
            'doc_id': doc_id,
            'doc_type': doc_type,
            'chunk_index': len(chunks)
        })
    
    return chunks

if __name__ == "__main__":
    sample = """Patient is a 65-year-old male with HTN and DM2. 
    He c/o SOB on exertion. BP was 160/90, HR 88, SPO2 94%. 
    Known h/o MI and CHF. Currently on medications prn."""

    chunks = chunk_document(sample, doc_type="clinical_note", doc_id="note_001")
    
    for chunk in chunks:
        print(f"\n--- Chunk {chunk['chunk_index']} ---")
        print(chunk['text'])