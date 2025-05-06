from paperprocessing import *
from retrieve import search_similar_sentences
import requests
from pathlib import Path
from collections import defaultdict


url = "http://server_address/api/generate"
s1 = "The BCL2 family proteins are able to protect cells from apoptosis that is instigated by multiple mechanisms including immune cells"
s2 = "The immune synapse is crucial to effective killing of target cells by CD8s."

pdf_folder = Path.cwd() / "zotero_pdfs"
rag_db = Path.cwd() / "rag_sentences.db"

# on startup
check_database()
missing_titles = get_unencoded_titles(pdf_folder, rag_db)

print(f"📝 Titles in folder but not in RAG DB: {missing_titles}")

for title in missing_titles:
    print(f"Encoding {title}")
    encode(article=get_article(link=f"zotero_pdfs/{title}.pdf"), title=title)
    print(f"{title}: encoded")


results = search_similar_sentences(s1)

for result in results:
    print(result)
    print("\n")

if len(results) > 0:
    grouped = defaultdict(list)
    for result in results:
        key = result[2]
        grouped[key].append(result[1])

        final_groups = dict(grouped)

    print('Results from Ollama')

    """for result in results: 
        prompt = f\"""
        You will be given a reference sentence and then a comparison sentence. Your job is to tell 
        if the comparison sentence 1) supports, 2) refutes, or 3) is not related to the reference sentence.
        The boundary for related to is related enough that it could be used as a citation either for or against 
        the reference sentence. Please respond with just 1, 2, or 3 with 1 meaning supports, 2 meaning refutes 
        and 3 meaning unrelated and a single sentence explaining your reasoning concisely.

        reference sentence: {s1}
        comparison sentence: {result}
        \"""
        if float(result[0]) > 0.74:
            res = requests.post(url, json={
                "model": "nous-hermes2",
                "prompt": prompt,
                "stream": False
            })

            print(res.json()['response'])
            print(result[1])
            print('\n')
            
    """

    
    for key in final_groups:
        prompt = f"""
            You will be given a reference sentence and then a list of sentences from a paper that have been filtered 
            so they should be similar to the reference. Your job is to decide if the paper as a whole 1) supports, 
            2) refutes, or 3) is not related to the reference sentence. The boundary for related to is related enough 
            that it could be used as a citation either for or against the reference sentence. Please respond with just 
            1, 2, or 3 with 1 meaning supports, 2 meaning refutes and 3 meaning unrelated.

            reference sentence: {s1}
            comparison sentences: {final_groups[key]}
            """
        res = requests.post(url, json={
            "model": "nous-hermes2",
            "prompt": prompt,
            "stream": False
        })

        print(key)
        print('\n')
        print(res.json()['response'])
        print('\n')
        print('\n')