"""LangChain tool that proxies any free-form request through a sub-agent to the LLM."""
import json
import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langchain.tools import tool


def _build_llm() -> ChatOllama:
    return ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "qwen3.5:9b"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=float(os.getenv("LLM_TOOL_TEMPERATURE", "0.7")),
    )


@tool
def ask_llm(prompt: str, system: str = "") -> str:
    """Proxy any free-form question or text task through the LLM and return a custom response.

    Use this tool when the user asks something that is NOT an API operation —
    explanations, summaries, translations, code snippets, creative text, etc.

    Args:
        prompt: The question or instruction to send to the LLM.
        system: Optional system instruction that steers the model's behaviour
                (e.g. "Answer only in Russian", "Be concise", "Act as a poet").
    """
    llm = _build_llm()

    messages = []
    if system:
        messages.append(SystemMessage(content=system))
    messages.append(HumanMessage(content=prompt))

    sys_preview = repr(system[:40]) if system else ""
    print(f"[TOOL:ask_llm] prompt={prompt[:80]!r}  system={sys_preview}")

    try:
        response = llm.invoke(messages)
        content = response.content
        print(f"[TOOL:ask_llm] response length={len(content)} chars")
        return json.dumps({"success": True, "response": content}, ensure_ascii=False)
    except Exception as exc:
        print(f"[TOOL:ask_llm] error: {exc}")
        return json.dumps({"success": False, "error": str(exc)})
