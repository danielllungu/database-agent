from langchain_openai import ChatOpenAI
from agent.config import settings

def make_llm(model = None, temperature = 0.1):
    return ChatOpenAI(
        model=model or settings.openai_model,
        temperature=temperature,
        api_key=settings.openai_api_key,
        base_url=settings.openai_api_base or None,
    )
