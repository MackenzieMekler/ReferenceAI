import re
from sentence_transformers import models, SentenceTransformer
from flask import Flask, request, redirect, render_template
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, models
import numpy as np
import sqlite3
import requests
import random
import datetime
import json

app = Flask(__name__)


@app.route('/')
def index():
    return json.dumps({"message": "homepage"})

@app.route('/add_source', methods=['POST'])
def add_source():
    data = request.get_json()

    conn = sqlite3.connect(f'./dbs/{data['project']}.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sentences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sentence TEXT, 
            embedding TEXT,
            paper TEXT
        )
    ''')

    conn.commit()
    conn.close()

    sentences = re.split(r'(?<=[.!?])\s+', data["paper"])
    sentences = [s for s in sentences if s]

    word_embedding_model = models.Transformer('cambridgeltl/SapBERT-from-PubMedBERT-fulltext')
    pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
    model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

    embeddings = model.encode(sentences).tolist()

    conn = sqlite3.connect(f'/dbs/{data['project']}.db')
    cursor = conn.cursor()

    # Insert all rows
    for sentence, embedding in zip(sentences, embeddings):
        cursor.execute('''
            INSERT INTO sentences (sentence, embedding, paper) VALUES (?, ?, ?)
        ''', (sentence, json.dumps(embedding), data['title']))

    conn.commit()
    conn.close()

    return json.dumps({'message': f"added {data["title"]} to {data['project']}.db"})

@app.route('/sources/', methods=["GET"])
def get_sources():
    data = request.get_json()

    conn = sqlite3.connect(f'/dbs/{data['project']}.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT paper FROM sentences")
    sources = {row[0].lower() for row in cursor.fetchall()}
    
    conn.close()

    return json.dumps({'current sources': sources})

@app.route('/newtarget/<query>', methods=['POST'])
def compare_sentence(query):
    data = request.get_json()
    # Encode the query
    word_embedding_model = models.Transformer('cambridgeltl/SapBERT-from-PubMedBERT-fulltext')
    pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
    model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

    query_vec = model.encode([query])[0]

    # Connect to the DB and load all sentences and embeddings
    conn = sqlite3.connect(f'/dbs/{data['project']}.db')
    cursor = conn.cursor()
    cursor.execute('SELECT sentence, embedding, paper FROM sentences')
    
    similarities = []
    for sentence, embedding_json, paper in cursor.fetchall():
        embedding = np.array(json.loads(embedding_json))
        sim = cosine_similarity([query_vec], [embedding])[0][0]
        similarities.append((sim, sentence, paper))

    # Sort by similarity score
    similarities.sort(reverse=True)

    results = similarities[:15]

    if len(results) > 0:
        grouped = defaultdict(list)
        for result in results:
            key = result[2]
            grouped[key].append(result[1])

            final_groups = dict(grouped)
    
    return json.dumps(final_groups)

@app.route('/ollama_ping/', methods=['GET'])
def ollama_status(base_url="http://192.168.68.57:11434"):
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=3)
        if response.status_code == 200:
            print("✅ Ollama is running and accessible.")
            return json.dumps({"status_code": 200})
        else:
            print(f"⚠️ Received unexpected status code: {response.status_code}")
            return json.dumps({"status_code": response.status_code})
    except requests.ConnectionError:
        print("❌ Ollama is not running or not accessible.")
        return json.dumps({"message": "connection error"})
    except requests.Timeout:
        print("⏱️ Connection to Ollama timed out.")
        return json.dumps({"message": 'timed out'})

@app.route('/ollama_connector/<sentences>', methods=['POST'])
def askAI():
    data = request.get_json()

    sentences = data['sentences']
    results = []
    for key in sentences:
        prompt = f"""
            You will be given a reference sentence and then a list of sentences from a paper that have been filtered 
            so they should be similar to the reference. Your job is to decide if the paper as a whole 1) supports, 
            2) refutes, or 3) is not related to the reference sentence. The boundary for related to is related enough 
            that it could be used as a citation either for or against the reference sentence. Please respond with just 
            1, 2, or 3 with 1 meaning supports, 2 meaning refutes and 3 meaning unrelated.

            reference sentence: {data['query']}
            comparison sentences: {sentences[key]}
            """
        res = requests.post("http://192.168.68.57:11434/api/generate", json={
            "model": "nous-hermes2",
            "prompt": prompt,
            "stream": False
        })

        results.append((key, res.json()["response"]))
    
    return json.dumps({'responses': results})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8008)