import tiktoken

from CababasBot import env_secrets

async def prompt_to_tokens(prompt: str) -> int:
    model_name = env_secrets.OPENAI_MOD

    encoding = tiktoken.encoding_for_model(model_name=model_name)

    tokens = encoding.encode(prompt)
    return len(tokens)