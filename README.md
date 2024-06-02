
#   🐲Xplorer🐲 

Xplorer is the simple version of GPT researcher,  an autonomous agent that takes care of the tedious task and writes a detailed and well-structured research report with MarkDown format, by scraping, filtering, aggregating and organising information. 

Compared with [gpt-researcher](https://github.com/assafelovic/gpt-researcher), Xplorer is much simpler and easy to implement with the 200 lines of code in the main file.

  * ## **⭐Features**
	  * Chinese well-supported with a number of mainstream LLMs, like QianFan, Qwen, Kimi, Deepseek, chatGLM, OpenRouter, etc.
	  * Multiple Internet search engines supported, like Serper, Serp, SearchAPI, etc.
	  * AutoGen supported for subtopic consultation by putting human-in-the-loop.
	  * Persistence management to deal with the exceptional breakout.
	  * Local files retrieval along with Internet search.

* ## **🔥How to use**

- ### **Create and activate virtual environment**
```bash


git clone https://github.com/13331112522/git-xplorer.git

cd git-xplorer

python -m venv xplorer

cd xplorer 

cd bin

source activate

cd ..

cd ..

python -m pip install -r requirements.txt

cp .env.example .env

cp OAI_CONFIG_LIST_example OAI_CONFIG_LIST


```

- ### **Environment variables setting**
	- Fill the LLM and search API key according to your needs in .env and OAI_CONFIG_LIST.
	- Put the related files in the _source_ folder if you want.
	- Change the _llm.generate_text()_ accordingly. Using Kimi for AutoGen, Qwen for query generation, feedbacks and subtopic report generation, and GLM for comprehensive report generation by default.


- ### **Run**

```bash

python main.py

```

* **Firstly, you have to input the topic you want to explore.**
* **Agent generates sub-topics for you to consider. You can agree by inputting 'exit' or change them by inputting your opinions.**
* **Search and retrieval are carried out based on the sub-topics round and round again.**
* **Subtopic reports are generated before the final comprehensive report is produced.**

* ## **🍺Discussion**

- The breakout of running could occurred due to some reasons like LLM censorship, or rate limit or connection error, we adopt persistence management, which save the stage states during the running. If breakout, run again and it resumes without repeating the process successfully executed.

- The App consumes a lot of Tokens quickly, so it would be better to choose different LLMs for different tasks. We provide a lot of LLMs you can select. Currently, we recommend Qwen and GLM for report generation due to their stability and low cost.

* ## **🎉Structure**
```bash
Git-Xplorer/
│
├── modules              # Utils files
│  ├── _init_.py              
│  ├── llm_gen.py        # text generation by LLMs         
│  ├── search.py         # online search
│  └── retriever.py      # local retrieval       
├── source				 # Source files directory
│  ├── ...
├── faiss_index			 # VectorDB (created Automately)
│  ├── ...
├── state.json			 # state store for persistence (created Automately)
├── OAI_CONFIG_LIST		 # configuration list of LLMs for Autogen
├── OAI_CONFIG_LIST_example
├── .env.example
├── .env				 # Environment variables
├── README.md
├── main.py                
└── requirements.txt      # Project dependencies file
```
* ## **❤️Acknowledgement**
	* [AI researcher](https://github.com/mshumer/ai-researcher)
	* [gpt-researcher](https://github.com/assafelovic/gpt-researcher)
	* [PrivateGPT](https://github.com/zylon-ai/private-gpt)
	* [langchain](https://python.langchain.com/v0.2/docs/introduction/)
	* [lepton search](https://github.com/leptonai/search_with_lepton)
	* [STORM](https://github.com/stanford-oval/storm)
	* [AutoGen](https://github.com/microsoft/autogen)
