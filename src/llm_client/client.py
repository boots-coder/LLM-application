import logging
from volcenginesdkarkruntime import Ark

class LLMClient:
    """封装与远程大模型API（Ark）的交互"""

    def __init__(self, api_key, model_id):
        self.client = Ark(api_key=api_key)
        self.model_id = model_id

    def call_api(self, messages):
        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages
            )
            response = completion.choices[0].message.content
            logging.info("LLM API调用成功")
            return response
        except Exception as e:
            logging.error(f"LLM API调用失败: {e}")
            raise
