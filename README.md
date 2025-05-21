# ReferenceAI

ReferenceAI is a software that is created to aid scientists, researchers, and scientific communicators in the writing process. This resource allows for the background handling of sources and citations from personal libraries and automatically decides which sources are related to sentences while writing. 

This document outlines the current development of the project as well as the roadmap for the future. 

## Concept
It has been found that sentence comparisons as well as LLMs can accurately return sentences related to a sample sentence, even when they are both filled with niche scientific jargon. In this project, we have chosen an open-source sentence embedding model that seems to work very well with scientific texts and found an Ollama LLM that can work in conjunction with this to analyze returned text. 
By lining up the similar sentence AI and the LLM we are able to reduce the number of tokens sent to our LLM while simultaneously allowing for the complex comparison of our sentences which allows for an output of "they agree", "they disagree", and "they are not directly related" rather than just semantic similarity. This allows for our software to intelligently select the papers that would be best to cite or re-read after writing a sentence in a text. 

## Current Status
1. Backend API - Started. The basic routes are designed but additions and testing will be needed
2. LLM Integration - Started. Prompt made and the LLM is functional. Currently limited by the server hosting it.
3. Zotero Integration - Started. Works locally, needs to be updated and integrated better. Should also make it so this can work off of Zotero API as well.

## Next Steps
1. Continue backend testing and improvements
2. Create frontend and begin integrating it with the back
3. Dockerize the backend? 
