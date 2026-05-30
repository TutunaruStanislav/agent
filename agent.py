"""Build and return a LangChain 1.x agent wrapping the User Management API tools."""
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_ollama import ChatOllama

from tools.api_tool import create_user, get_user, list_users, update_user_status
from tools.llm_tool import ask_llm

load_dotenv()

_SYSTEM_PROMPT = """\
You are a User Management API Operator with access to five tools.

API tools (interact with the User Management service):
1. create_user(name, email)              – create a new user
2. get_user(user_id)                     – retrieve user by numeric ID
3. update_user_status(user_id, status)   – change status: active | inactive | banned
4. list_users()                          – return all users and total count

LLM proxy tool:
5. ask_llm(prompt, system="")           – forward any free-form question or text task
                                          to the language model and return its answer.
                                          Use this for questions, explanations, or tasks
                                          that do NOT require an API operation.

Constraints:
- Use an API tool for every data-changing or data-fetching request.
- Use ask_llm for open-ended questions, summaries, or anything outside the API scope.
- You CANNOT perform API operations not listed above (no delete, no auth, no bulk updates).
- If required parameters are missing, ask the user before calling a tool.
- Never invent or guess user IDs; use only values provided by the user or returned by a tool.

Always reply in exactly this format (no extra keys, no Markdown headers):

Status: success | error
Action: <one-sentence description of what was done>
Data: <tool result or "none">
Errors: <error details, or "none">
"""


def build_agent():
    llm = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "qwen3.5:9b"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0,
    )

    tools = [create_user, get_user, update_user_status, list_users, ask_llm]

    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=_SYSTEM_PROMPT,
    )


def run_query(query: str) -> str:
    """Run a single natural-language query and return the agent's text response."""
    agent = build_agent()
    result = agent.invoke({"messages": [{"role": "user", "content": query}]})
    # LangChain 1.x returns AgentState; last message is the final answer
    return result["messages"][-1].content
