import os

from openai import AsyncOpenAI

from .config import get_oauth_token, get_workspace_host, IS_DATABRICKS_APP

SERVING_ENDPOINT = os.environ.get("SERVING_ENDPOINT", "databricks-claude-sonnet-4-5")


def get_llm_client() -> AsyncOpenAI:
    host = get_workspace_host()

    if IS_DATABRICKS_APP:
        token = os.environ.get("DATABRICKS_TOKEN") or get_oauth_token()
    else:
        token = get_oauth_token()

    return AsyncOpenAI(
        api_key=token,
        base_url=f"{host}/serving-endpoints",
    )


async def chat_completion(
    messages: list,
    model: str | None = None,
    temperature: float = 0.1,
    max_tokens: int = 4096,
) -> str:
    client = get_llm_client()
    response = await client.chat.completions.create(
        model=model or SERVING_ENDPOINT,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content
