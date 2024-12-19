import json
import logging

class Translator:
    """负责摘要、关键词提取和翻译"""

    def __init__(self, llm_client):
        self.llm_client = llm_client

    def summarize_and_extract_keywords(self, paragraph):
        prompt = f"""Please read the following English paragraph and provide a summary and keywords in JSON format.

Paragraph:
{paragraph}

Output format:
{{
    "Summary": "...",
    "Keywords": "keyword1, keyword2, keyword3, keyword4, keyword5"
}}
"""
        messages = [{"role": "user", "content": prompt}]
        reply = self.llm_client.call_api(messages)
        logging.debug(f"摘要与关键词响应: {reply}")
        return self.parse_summary_keywords_en(reply)

    def translate_to_chinese(self, text):
        prompt = f"""Translate the following English text into Chinese and keep the same structure:

{text}

Output format should be a JSON object with the following keys:
{{
    "Chinese Paragraph": "...",
    "Chinese Summary": "...",
    "Chinese Keywords": "..."
}}
"""
        messages = [{"role": "user", "content": prompt}]
        zh = self.llm_client.call_api(messages)
        logging.debug(f"翻译响应: {zh}")
        return self.parse_chinese_translation(zh)

    @staticmethod
    def parse_summary_keywords_en(response_text):
        try:
            response_json = json.loads(response_text)
            summary = response_json.get("Summary", "").strip()
            keywords = response_json.get("Keywords", "").strip()
            return summary, keywords
        except json.JSONDecodeError as e:
            logging.error(f"JSON解析错误 (英文摘要与关键词): {e}")
            logging.error(f"响应文本: {response_text}")
            return "", ""

    @staticmethod
    def parse_chinese_translation(translation_text):
        try:
            translation_json = json.loads(translation_text)
            zh_paragraph = translation_json.get("Chinese Paragraph", "").strip()
            zh_summary = translation_json.get("Chinese Summary", "").strip()
            zh_keywords = translation_json.get("Chinese Keywords", "").strip()
            return zh_paragraph, zh_summary, zh_keywords
        except json.JSONDecodeError as e:
            logging.error(f"JSON解析错误 (中文翻译): {e}")
            logging.error(f"翻译文本: {translation_text}")
            return "", "", ""
