# ReferenceAI

Currently, the software takes an input sentence and a list of pdf research papers from the reference manager Zotero. It then uses embeddings to compare the input sentence to the research papers and return the top most similar sentences across the various papers. Once this has been accomplished it groups the returned sentences by the papers that they originate from and passes these along to an Ollama LLM that is hosted on a server of my own. This LLM tells the likelihood that the paper given supports, refutes, or is unrelated to the input sentences. 

The idea of this project, in the future, is to be able to integrate into microsoft word, powerpoint, google docs, and google slides where it will be able to input citations automatically while someone types. The benefit of this over a traditional reference manager is that for a traditional one, you still must select the paper which supports you which is not always easy to find if you have read hundreds of papers over the course of years. ReferenceAI has the ability to take papers you have already read and find where the information you have is coming from while also highlighting sentences that papers disagree with or that are contentious in the field. This solves a pervasive annoyance to researchers creating presentations, writing research papers, writing review papers, and many other types of scientific communication. 

Right now, I have a very ugly proof-of-concept that works in the VSCode (mostly) but I would like to try to create a microsoft word add in that is able to use this AI how I have described above. 

## What has been done
- Proof of concept sentence comparing in the code
- Tested various sentence-transformer models for encoding 
- Access to Zotero locally to find and save paper pdfs

## What needs to be done
- Turn backend into an API with Flask
- Create frontend UI 
