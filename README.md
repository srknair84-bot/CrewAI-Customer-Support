# 🤖 CrewAI Customer Support

A multi-agent customer support demo built with [CrewAI](https://www.crewai.com/) and Streamlit. You type a question, two agents answer it in different ways, and a third agent records both answers in a text report you can download.

## How it works

Three agents run one after another (`Process.sequential`):

| # | Agent | What it does | Tools |
|---|---|---|---|
| 1 | **Assistant** | Answers the question from the model's own knowledge, with no web search | none |
| 2 | **Web Search Assistant** | Searches the web and writes an answer from the results, using Agent 1's answer as context | Serper web search (`SerperDevTool`) |
| 3 | **Entry Agent** | Combines the question and both answers into a labelled report and saves it to `support_log.txt` | none |

```
Question ─► Assistant ─► Web Search Assistant ─► Entry Agent ─► support_log.txt
            (own knowledge)   (live web results)    (report)
```

The Streamlit page shows both answers side by side in order and offers a **Download Text Report** button. All agents use `openai/gpt-4o-mini`.

`support_log.txt` in this repo is a sample report from one run. It is overwritten each time you submit a question.

## Tech stack

Python · CrewAI · crewai-tools (Serper) · OpenAI `gpt-4o-mini` · Streamlit · python-dotenv

## Getting started

### Prerequisites

- Python 3.10 or newer
- An [OpenAI API key](https://platform.openai.com/)
- A [Serper API key](https://serper.dev/) for web search

### Install

```bash
git clone https://github.com/srknair84-bot/CrewAI-Customer-Support.git
cd CrewAI-Customer-Support
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configure

Create a `.env` file in the project folder:

```env
OPENAI_API_KEY=your-openai-key
SERPER_API_KEY=your-serper-key
```

### Run

```bash
streamlit run app.py
```

Open the local URL Streamlit prints (usually http://localhost:8501), enter a question and click **Get Answers**.

## Project structure

```
app.py             agents, tasks, crew and Streamlit UI
requirements.txt   dependencies
support_log.txt    sample output report
```

## Ideas for next steps

- Let the user choose between the direct answer and the web answer, or have a reviewer agent compare them
- Add a knowledge base (RAG) for company-specific support answers
- Keep a history of past questions instead of overwriting one report
