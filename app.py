
import os
from dotenv import load_dotenv

from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool

import streamlit as st

from pathlib import Path
from datetime import datetime

# Load API keys from .env
load_dotenv()

# Configure the language model
llm = LLM(
    model="openai/gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Web search tool
search_tool = SerperDevTool()

# --------------------------------
# AGENT 1: Assistant
# --------------------------------
assistant = Agent(
    role="Assistant",
    goal="Answer the user's query directly using your own knowledge.",
    backstory=(
        "You are a helpful customer support assistant. "
        "Provide a clear, accurate, and friendly answer "
        "based on your existing knowledge."
    ),
    llm=llm,
    verbose=True,
)

# --------------------------------
# AGENT 2: Web Search Assistant
# --------------------------------
web_assistant = Agent(
    role="Web Search Assistant",
    goal="Search the web and provide a useful answer to the user's query.",
    backstory=(
        "You are a customer support research assistant. "
        "You search the web for relevant information and "
        "write a clear answer based on the search results."
    ),
    tools=[search_tool],
    llm=llm,
    verbose=True,
)

# --------------------------------
# AGENT 3: Entry Agent
# --------------------------------
entry_agent = Agent(
    role="Entry Agent",
    goal="Record the user's query and both answers in a text file.",
    backstory=(
        "You are a careful record-keeping assistant. "
        "You receive the user's query, the Assistant's answer, "
        "and the Web Search Assistant's answer. "
        "You organize them clearly in a text report."
    ),
    llm=llm,
    verbose=True,
)

# --------------------------------
# TASK 1: Direct answer
# --------------------------------
assistant_task = Task(
    description=(
        "Answer the following user query using your own knowledge. "
        "Do not search the web.\n\n"
        "User query: {query}"
    ),
    expected_output="A clear and helpful answer to the user's query.",
    agent=assistant,
)

# --------------------------------
# TASK 2: Web-based answer
# --------------------------------
web_task = Task(
    description=(
        "Search the web for the user's query and write a useful answer "
        "based on the search results.\n\n"
        "User query: {query}\n\n"
        "Consider the first Assistant's answer as context, "
        "but produce your own web-supported answer."
    ),
    expected_output="A clear answer based on relevant web search results.",
    agent=web_assistant,
    context=[assistant_task],
)

# --------------------------------
# TASK 3: Save both answers
# --------------------------------
entry_task = Task(
    description=(
        "Create a text report containing all of the following:\n"
        "1. The original user query\n"
        "2. The Assistant's answer\n"
        "3. The Web Search Assistant's answer\n\n"
        "User query: {query}\n\n"
        "Use the outputs of the two previous tasks as context. "
        "Keep both answers complete and clearly labeled."
    ),
    expected_output=(
        "A text report containing the original query and both answers."
    ),
    agent=entry_agent,
    context=[assistant_task, web_task],
    output_file="support_log.txt",
)

# --------------------------------
# CREATE THE SEQUENTIAL CREW
# --------------------------------
crew = Crew(
    agents=[assistant, web_assistant, entry_agent],
    tasks=[assistant_task, web_task, entry_task],
    process=Process.sequential,
    verbose=True,
)

# -----------------------------
# Streamlit User Interface
# -----------------------------

st.set_page_config(
    page_title="CrewAI Customer Support",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 CrewAI Customer Support")
st.write(
    "Enter your query below. Two assistants will answer it, "
    "and the Entry Agent will save both answers to a text file."
)

query = st.text_area(
    "Enter your query:",
    placeholder="Example: What are the benefits of using Python?",
    height=120,
)

if st.button("Get Answers", type="primary"):
    if not query.strip():
        st.warning("Please enter a query first.")
    else:
        with st.spinner("Agents are working. Please wait..."):
            try:
                result = crew.kickoff(inputs={"query": query})

                # Get the outputs from the first two tasks
                answer1 = result.tasks_output[0].raw
                answer2 = result.tasks_output[1].raw

                st.success("All three agents have finished!")

                st.subheader("1. Assistant's Answer")
                st.markdown(answer1)

                st.subheader("2. Web Search Assistant's Answer")
                st.markdown(answer2)

                # Read the text report created by the Entry Agent
                report_path = "support_log.txt"

                if os.path.exists(report_path):
                    with open(report_path, "r", encoding="utf-8") as file:
                        report_content = file.read()

                    st.download_button(
                        label="Download Text Report",
                        data=report_content,
                        file_name="support_log.txt",
                        mime="text/plain",
                    )
                else:
                    st.warning(
                        "The answers were generated, but the text report "
                        "was not found."
                    )

            except Exception as e:
                st.error(f"Something went wrong: {e}")