import re


def camel_case_to_sentence(string: str) -> str:
    return re.sub('([a-z]+)([A-Z])', r'\1 \2', string).lower()
