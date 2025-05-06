import re
from sentence_transformers import models, SentenceTransformer
import sqlite3
import json
import fitz

def check_database():
    conn = sqlite3.connect('rag_sentences.db')
    cursor = conn.cursor()

    # Create table if not exists
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


def encode(article, title, model="cambridgeltl/SapBERT-from-PubMedBERT-fulltext"):
    sentences = re.split(r'(?<=[.!?])\s+', article)
    sentences = [s for s in sentences if s]

    word_embedding_model = models.Transformer('cambridgeltl/SapBERT-from-PubMedBERT-fulltext')
    pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
    model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

    embeddings = model.encode(sentences).tolist()

    conn = sqlite3.connect('rag_sentences.db')
    cursor = conn.cursor()

    # Insert all rows
    for sentence, embedding in zip(sentences, embeddings):
        cursor.execute('''
            INSERT INTO sentences (sentence, embedding, paper) VALUES (?, ?, ?)
        ''', (sentence, json.dumps(embedding), title))

    conn.commit()
    conn.close()


def get_article(file = None, link = None):
    if file != None: 
        # process an entire file 
        pdf = file
    elif link != None:
        # process a file from a link 
        pdf = fitz.open(link)
    else: 
        raise ValueError("file or link must be provided")
    
    # print(pdf)
    text = ""
    for page in pdf:
        text += page.get_text()

    return text

import os
import sqlite3
from pathlib import Path

def get_unencoded_titles(pdf_dir: Path, rag_db_path: Path):
    # 1. Get all PDF titles from the folder (stem removes ".pdf")
    pdf_titles = {f.stem.lower() for f in pdf_dir.glob("*.pdf")}
    
    # 2. Connect to the RAG sentence database and get all encoded titles
    conn = sqlite3.connect(rag_db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT paper FROM sentences")
    encoded_titles = {row[0].lower() for row in cursor.fetchall()}
    
    conn.close()
    
    # 3. Compare and get titles not yet encoded
    unencoded_titles = pdf_titles - encoded_titles
    return list(unencoded_titles)