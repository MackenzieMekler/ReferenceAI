import sqlite3
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, models

# Load model (same one you used for embedding)

# query = "Cytotoxic lymphocytes kill target cells by forming an immmune synapse with the target cell"

def search_similar_sentences(query, db_path='rag_sentences.db', top_k=10, mod='cambridgeltl/SapBERT-from-PubMedBERT-fulltext'):
    # Encode the query
    word_embedding_model = models.Transformer(mod)
    pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
    model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

    query_vec = model.encode([query])[0]

    # Connect to the DB and load all sentences and embeddings
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT sentence, embedding, paper FROM sentences')
    
    similarities = []
    for sentence, embedding_json, paper in cursor.fetchall():
        embedding = np.array(json.loads(embedding_json))
        sim = cosine_similarity([query_vec], [embedding])[0][0]
        similarities.append((sim, sentence, paper))

    # Sort by similarity score
    similarities.sort(reverse=True)
    return similarities[:top_k]
