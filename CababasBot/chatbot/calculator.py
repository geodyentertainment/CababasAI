import tiktoken

from CababasBot import env_secrets


async def prompt_to_tokens(prompt: str) -> int:
    model_name = env_secrets.OPENAI_MOD

    encoding = tiktoken.encoding_for_model(model_name=model_name)

    tokens = encoding.encode(prompt)
    return len(tokens)


def input_tokens_to_cost(input_tokens: int) -> float:
    return (0.003 / 1000) * input_tokens


def output_tokens_to_cost(input_tokens: int) -> float:
    return (0.012 / 1000) * input_tokens


def tokens_to_cost(input_tokens: int, output_tokens: int) -> float:
    return input_tokens_to_cost(input_tokens) + output_tokens_to_cost(output_tokens)


def to_string(number: float) -> str:
    return f'{number:.6f}'