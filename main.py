#Combine ai-researcher and autogen to do the Xplorer in Chinese. Simple-version of gpt-researcher.

import os
import glob
import autogen
import requests
import json
import time
import ast
import re
from modules.llm_gen import LLM_Gen
from modules.retriever import RETRIEVER
from dotenv import load_dotenv
import os
from modules.search import Search_Web
load_dotenv()


folder=os.environ.get('DB')

#Initialize the search, retriever and LLM engines.

search=Search_Web()

llm=LLM_Gen()

retriever=RETRIEVER()

#retriever.save_db(folder=folder)

llm_config = autogen.config_list_from_json(env_or_file="OAI_CONFIG_LIST",filter_dict = {"model": "moonshot-v1-128k"}) # Define the LLM configuration for Autogen for sub-topics.
gpt_config = {
    "timeout": 600,
    "seed": 42,  # change the seed for different trials
    "temperature": 0.2,
    "config_list": llm_config,
    #"request_timeout": 120,
}
user_proxy = autogen.UserProxyAgent(
    name="Boss",
    human_input_mode="ALWAYS",
    llm_config=gpt_config,
    code_execution_config=False,
)

planner = autogen.AssistantAgent(
    name="Planner",
    llm_config=gpt_config,
)

STATE_FILE = 'state.json' 

# Persistence management functions
def save_state(state): 
	with open(STATE_FILE, 'w') as f: 
		json.dump(state, f) 
          
def load_state(): 

    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'w') as f:
        #    f.write("{"current_item": 0}")
            return {'current_item': 0}  # 如果文件不存在，返回初始状态
    try:
        with open(STATE_FILE, 'r') as f:
            print("Loading state...")
            state=json.load(f)
    # 代码块
    except Exception as e: 
        print(f"Err: {e}") 
        state = {}
    return state
    # 异常处理代码
    

# Subtopic generation function
def generate_subtopic_report(subtopic):
    search_data = []
    all_queries = []

    print(f"Generating initial search queries in Chinese for subtopic: {subtopic}...")
    initial_queries_prompt = f"Generate 3 search queries in Chinese to gather information on the subtopic '{subtopic}'. Return your queries in a Python-parseable list. Return nothing but the list. Do so in one line. Start your response with [\""
    try:
        initial_queries = ast.literal_eval('[' + llm.generate_text(model="moonshot",prompt=initial_queries_prompt,max_tokens=100).split('[')[1]) # Generate the initial search queries for subtopics.
    except Exception as e:
        print(f"Error parsing initial queries: {e}")
        initial_queries = ast.literal_eval('[' + llm.generate_text(model="moonshot",prompt=initial_queries_prompt,max_tokens=100).strip('"').split('[')[1])
    print(initial_queries)
    all_queries.extend(initial_queries)

    for i in range(3):
        print(f"Performing search round {i+1} for subtopic: {subtopic}...")
        for query in initial_queries:
            search_results = search.search_web(query,"serper") # Perform a search using the searching API online.
            retrieve_results=retriever.retrieve_db(query,folder) # Perform a retrieval using RAG.
            search_data.append(search_results)  # Add both results from local and onine into the search data.
            search_data.append(retrieve_results)

    print(f"Generating initial report for subtopic: {subtopic}...")
    report_prompt = f"When writing your report in Chinese, make it incredibly logic, detailed, thorough, specific in a whole and integrated paragraph over 500 words and less than 1000 words, do not make a list of points or subtitles. Use Markdown for formatting. Analyze the following search data and generate a comprehensive report on the subtopic '{subtopic}':\n\n{str(search_data)}"
    report = llm.generate_text(model="qwen",prompt=report_prompt, max_tokens=1000) # Generate the initial report for subtopics.
    #report = generate_text(report_prompt)
    #print(report)
    print(f"Generating boss feedback for subtopic: {subtopic}...")
    feedback_prompt = f"Imagine you are the boss reviewing the following report on the subtopic '{subtopic}':\n\n{report}\n\n---\n\nProvide constructive feedback on what information is missing or needs further elaboration in the report. Be specific and detailed in your feedback."
    feedback = llm.generate_text(model="qwen",prompt=feedback_prompt, max_tokens=500) # Critical feedback from the boss.
    #feedback = generate_text(feedback_prompt)

    print(f"Generating final round of searches based on feedback for subtopic: {subtopic}...")
    final_queries_prompt = f"Based on the following feedback from the boss regarding the subtopic '{subtopic}':\n\n{feedback}\n\n---\n\nGenerate 3 search queries in Chinese to find the missing information and address the areas that need further elaboration. Return your queries in a Python-parseable list. Return nothing but the list. Do so in one line. Start your response with [\""
    #final_queries = ast.literal_eval('[' + generate_text(final_queries_prompt).strip(';').split('[')[1])
    try:
        final_queries = ast.literal_eval('[' + llm.generate_text(model="qwen",prompt=final_queries_prompt,max_tokens=1000).strip(';').split('[')[1]) # Start search again based on the boss's feedback.
    except Exception as e:
        print(f"Error parsing initial queries: {e}")
        final_queries = ast.literal_eval('[' + llm.generate_text(model="qwen",prompt=final_queries_prompt,max_tokens=1000).split('[')[1])
    #final_queries = '[' + generate_text(final_queries_prompt).split('[')[1]
    all_queries.extend(final_queries) # Add the final queries to the all_queries list.

    final_search_data = []
    for query in final_queries: # Perform the final search round.
        search_results = search.search_web(query,"serper")
        final_search_data.append(search_results)
        retrieve_results=retriever.retrieve_db(query,folder)
        final_search_data.append(retrieve_results)

    print(f"Updating report with final information for subtopic: {subtopic}...")
    final_update_prompt = f"Update the following report on the subtopic '{subtopic}' by incorporating the new information from the final round of searches based on the boss's feedback:\n\n{report}\n\n---\n\nFinal search data:\n\n{str(final_search_data)}\n\n---\n\nGenerate the final report in Chinese that addresses the boss's feedback and includes the missing information in an integrated paragraph. Use Markdown for formatting."
    final_report = llm.generate_text(model="glm",prompt=final_update_prompt, max_tokens=4000) # Updating and revising the initial report based on the final search data.
    #final_report = generate_text(final_update_prompt)

    print(f"Final report generated for subtopic: {subtopic}!")
    with open("subtopic_report.md", "a") as file:
        file.write(final_report) # Saving the subtopic report.
    return final_report

# Comprehensive report generation.
def generate_comprehensive_report(topic, subtopic_reports):
    print("Generating comprehensive report...")
    comprehensive_report_prompt = f"Generate a comprehensive report in Chinese on the topic '{topic}' by combining the following reports on various subtopics:\n\n{subtopic_reports}\n\n---\n\nEnsure that the final report is well-structured, coherent, and covers all the important aspects of the topic. Make sure that it includes EVERYTHING in each of the reports, in a better structured, more info-heavy manner. Nothing -- absolutely nothing, should be left out. If you forget to include ANYTHING from any of the previous reports, you will face the consequences. Include a table of contents. Leave nothing out. make each subtopic incredibly logic, detailed, thorough, specific in a whole and integrated paragraph at least over 800 words, do not make a list of points or subtitles. Use Markdown for formatting."
    #comprehensive_report = generate_final_text(comprehensive_report_prompt, max_tokens=4000)
    comprehensive_report = llm.generate_text(model="glm",prompt=comprehensive_report_prompt,max_tokens=4000) # Generating the comprehensive report within 4000 words based on subtopic reports.

    print("Comprehensive report generated!")
    return comprehensive_report

# Main function.
if __name__ == '__main__':

    
    #Initialize the topic. Autogen will list the possible sub-topics. You can modified them or agree with them by typing 'exit'.
    research_topic = input("Enter the research topic: ")
    subtopic_checklist_prompt = f"Generate a detailed checklist of subtopics to research for the topic '{research_topic}' in Chinese. Return your checklist in a Python-parseable list. Return nothing but the list. Do so in one line. Maximum four sub-topics. Start your response with [\""
    
    #subtopic_checklist = ast.literal_eval('[' + generate_text(subtopic_checklist_prompt).split('[')[1])
    chat_results=user_proxy.initiate_chat(
        planner,
        message=subtopic_checklist_prompt,
    )
    try:
        subtopic_checklist = ast.literal_eval('[' + str(chat_results.summary).split('[')[1])
    except Exception as e:
        print(f"Error parsing initial queries: {e}")
        subtopic_checklist = ast.literal_eval('[' + str(chat_results.summary).strip(';').split('[')[1])
    #subtopic_checklist = chat_results
    print(f"Subtopic Checklist: {subtopic_checklist}")
    #input()

    #Ingest the local documents for retrieval to store vectorDB in the folder
    retriever.save_db(folder)
    
    subtopic_reports = []

    # Persistence state management
    state = load_state()

    if state is None:
        state = {"current_item": 0}

    total_items = len(subtopic_checklist)
    
    while state['current_item'] < total_items:
        item = state["current_item"]
        # Generate a subtopic report
        subtopic_report = generate_subtopic_report(subtopic_checklist[item])

        # Append the subtopic report to the list
        subtopic_reports.append(subtopic_report)
        
        state["current_item"] += 1

        # Save the state
        save_state(state)
    
    # Combine subtopic reports into a comprehensive report
    comprehensive_report = generate_comprehensive_report(research_topic, "\n\n".join(subtopic_reports))

    # Save the comprehensive report to a file, could be used in Obsidian.
    with open("comprehensive_report.md", "w") as file:
        file.write(comprehensive_report)

    print("Comprehensive report saved as 'comprehensive_report.md'.")
    
    # Return to Zero
    state["current_item"] = 0

    save_state(state)