import json
import logging

class ResultSaver:
    """负责保存结果到JSON和文本文件"""

    @staticmethod
    def save_to_json(results, json_path="result.json"):
        try:
            with open(json_path, "w", encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logging.info(f"结果保存为JSON: {json_path}")
        except Exception as e:
            logging.error(f"保存结果为JSON失败: {e}")
            raise

    @staticmethod
    def save_translated_text(translated_paragraphs, txt_path="translated_paper.txt"):
        try:
            translated_text = "\n\n".join(translated_paragraphs)
            with open(txt_path, "w", encoding='utf-8') as f:
                f.write(translated_text)
            logging.info(f"翻译全文保存为文本文件: {txt_path}")
        except Exception as e:
            logging.error(f"保存翻译全文失败: {e}")
            raise
