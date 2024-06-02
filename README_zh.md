#   🐲Xplorer🐲 

Xplorer 是一个自主代理，负责繁琐的任务，并通过抓取、过滤、聚合和组织信息，编写详细且结构良好的MarkDown格式的研究报告。可以看成是GPT researcher的简化版本。

与 [gpt-researcher](https://github.com/assafelovic/gpt-researcher) 相比，Xplorer 更简单，易于实现，主文件只有 200 行代码。

  * ## **⭐功能特点**
	  * 中文支持良好，兼容众多主流 LLM，如千帆、Qwen、Kimi、Deepseek、chatGLM、OpenRouter 等。
	  * 支持多种互联网搜索引擎，如 Serper、Serp、SearchAPI 等。
	  * 支持 AutoGen，通过人机交互进行子主题咨询。
	  * 持久化管理，处理异常中断。
	  * 本地文件检索与互联网搜索相结合。

* ## **🔥使用方法**

- ### **创建并激活虚拟环境**
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

- ### **环境变量设置**
	- 根据需要在 .env 和 OAI_CONFIG_LIST 中填写 LLM 和搜索 API 密钥。
	- 如果需要，将相关文件放在 _source_ 文件夹中。
	- 相应地更改 _llm.generate_text()_。默认情况下使用 Kimi 进行 AutoGen，使用 Qwen 进行查询生成、反馈和子主题报告生成，使用 GLM 进行综合报告生成。

- ### **运行**
```bash

python main.py

```

* **首先，输入你想探索的主题。**
* **AutoGen生成供您考虑的子主题。你可以通过输入 'exit' 同意，或通过输入你的意见修改它们。**
* **基于子主题进行一轮又一轮的搜索和检索。**
* **在生成最终综合报告之前，生成子主题报告。**

* ## **🍺讨论**

- 运行过程中可能会由于某些原因发生中断，如 LLM 审查、速率限制或连接错误，我们采用持久化管理，在运行期间保存阶段状态。如果中断，重新运行并恢复而不会重复已成功执行的过程。

- 该应用程序消耗大量 Token，因此最好为不同任务选择不同的 LLM。我们提供了许多可供选择的 LLM。目前，我们推荐使用 Qwen 和 GLM 生成报告，因为它们稳定且成本低。


* ## **🎉文件结构**

```bash

Git-Xplorer/
│
├── modules               # 工具文件
│   ├── init.py
│   ├── llm_gen.py        # 通过 LLM 生成文本
│   ├── search.py         # 在线搜索
│   └── retriever.py      # 本地检索
├── source                # 源文件目录
│   ├── ...
├── faiss_index           # 向量数据库（自动创建）
│   ├── ...
├── state.json            # 持久化状态存储（自动创建）
├── OAI_CONFIG_LIST       # Autogen 的 LLM 配置列表
├── OAI_CONFIG_LIST_example
├── .env.example
├── .env                  # 环境变量
├── README.md
├── main.py
└── requirements.txt      # 项目依赖文件
```

* ## **❤️致谢**
	* [AI researcher](https://github.com/mshumer/ai-researcher)
	* [gpt-research](https://github.com/assafelovic/gpt-researcher)
	* [PrivateGPT](https://github.com/zylon-ai/private-gpt)
	* [langchain](https://python.langchain.com/v0.2/docs/introduction/)
	* [lepton search](https://github.com/leptonai/search_with_lepton)
	* [STORM](https://github.com/stanford-oval/storm)
    * [AutoGen](https://github.com/microsoft/autogen)


