from leftovers.core.external.open_ai_client import client
from leftovers.core.config.config import settings

# OpenAI Responses API의 structured outputs 기능에서 쓰는 JSON Schema
# TIp SCHEMA의 형태로 응답을 제공함
TIP_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "title":   {"type": "string", "maxLength": 20},
                    "content": {"type": "string"}
                },
                "required": ["title", "content"]
            }
        }
    },
    "required": ["items"] # items 키는 필수
}

def chatForTip(messages, model=None, **kwargs) -> str:
    res = client.chat.completions.create(
        model=model or settings()["openai_model"],
        messages=messages,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "tip_list",
                "strict": True,
                "schema": TIP_SCHEMA
            }
        },
        **kwargs
    )
    return res.choices[0].message.content

