#!/usr/bin/env bash

# 要创建的项目根目录名称
PROJECT_ROOT="readPaper-forCHINESE"

# 创建项目主目录
mkdir -p $PROJECT_ROOT
cd $PROJECT_ROOT

# 创建基础目录
mkdir -p src/{pdf_processor,table_extractor,llm_client,translator,result_saver,utils} \
         config \
         tests

# 创建 __init__.py 文件以使各目录成为Python包
touch src/__init__.py
touch src/pdf_processor/__init__.py
touch src/table_extractor/__init__.py
touch src/llm_client/__init__.py
touch src/translator/__init__.py
touch src/result_saver/__init__.py
touch src/utils/__init__.py
touch config/__init__.py
touch tests/__init__.py

# 创建主文件
touch src/main.py
touch requirements.txt
touch README.md
touch .gitignore

# 创建配置文件
cat > config/config.py <<EOF
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Ark API 配置
ARK_API_KEY = os.getenv("ARK_API_KEY")
ARK_MODEL_ID = "ep-20241219220308-mtmr8"  # 替换为你的实际模型ID

# OCR 工具配置
TESSERACT_CMD = "/usr/bin/tesseract"  # 根据实际情况修改
LATEXOCR_CMD = "/usr/local/bin/latexocr"  # 根据实际情况修改
EOF

# 创建 pdf_processor 模块文件
cat > src/pdf_processor/processor.py <<EOF
import fitz  # PyMuPDF
import logging

class PDFProcessor:
    """负责解析PDF文本和分段"""

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.full_text = ""
        self.doc = None

    def extract_text(self):
        try:
            self.doc = fitz.open(self.pdf_path)
            text_pages = [page.get_text("text") for page in self.doc]
            self.full_text = "\\n\\n".join(text_pages)
            logging.info("PDF文本提取完成")
        except Exception as e:
            logging.error(f"解析PDF失败: {e}")
            raise

    def split_into_paragraphs(self):
        try:
            paragraphs = [p.strip() for p in self.full_text.split('\\n\\n') if p.strip()]
            logging.info(f"PDF文本分段完成，共分割出 {len(paragraphs)} 段")
            return paragraphs
        except Exception as e:
            logging.error(f"分段失败: {e}")
            raise
EOF

cat > src/pdf_processor/image_extractor.py <<EOF
import fitz
import os
import logging

class ImageExtractor:
    """负责提取PDF中的图像并保存"""

    def __init__(self, pdf_path, output_dir='images'):
        self.pdf_path = pdf_path
        self.output_dir = output_dir

    def extract_images(self):
        try:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
            with fitz.open(self.pdf_path) as doc:
                for page_num, page in enumerate(doc, start=1):
                    images = page.get_images(full=True)
                    for img_index, img in enumerate(images):
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        image_path = os.path.join(self.output_dir, f"page_{page_num}_img_{img_index}.{image_ext}")
                        with open(image_path, "wb") as f:
                            f.write(image_bytes)
                        logging.info(f"图像保存为: {image_path}")
            logging.info(f"图像提取完成，保存至 {self.output_dir}")
        except Exception as e:
            logging.error(f"图像提取失败: {e}")
            raise
EOF

# 创建 table_extractor 模块文件
cat > src/table_extractor/extractor.py <<EOF
import os
import csv
import pdfplumber
import logging

class TableExtractor:
    """负责提取PDF中的表格并保存为CSV"""

    def __init__(self, pdf_path, output_dir='tables'):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.table_descriptions = []

    def extract_tables(self):
        try:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)

            table_count = 0
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    tables = page.extract_tables()
                    for table in tables:
                        if table:
                            csv_path = os.path.join(self.output_dir, f"table_{table_count}.csv")
                            self.write_table_to_csv(table, csv_path)
                            first_row = table[0]
                            desc = f"Table {table_count}: contains columns {first_row}"
                            self.table_descriptions.append(desc)
                            logging.info(f"表格保存为CSV: {csv_path}")
                            table_count += 1
                        else:
                            self.table_descriptions.append(f"Table {table_count}: empty or no header")
                            table_count += 1
            logging.info(f"表格提取完成，共提取出 {table_count} 个表格")
        except Exception as e:
            logging.error(f"提取表格失败: {e}")
            raise

    @staticmethod
    def write_table_to_csv(table_data, csv_path):
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(table_data)
        except Exception as e:
            logging.error(f"保存表格为CSV失败: {e}")
            raise
EOF

# 创建 llm_client 模块文件
cat > src/llm_client/client.py <<EOF
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
EOF

# 创建 translator 模块文件
cat > src/translator/translator.py <<EOF
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
EOF

# 创建 result_saver 模块文件
cat > src/result_saver/saver.py <<EOF
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
EOF

# 创建 utils 模块文件
cat > src/utils/helpers.py <<EOF
import logging

def setup_logging(log_file='app.log'):
    logging.basicConfig(
        filename=log_file,
        filemode='w',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
EOF

# 创建 main.py
cat > src/main.py <<EOF
import logging
from config.config import ARK_API_KEY, ARK_MODEL_ID, TESSERACT_CMD, LATEXOCR_CMD
from pdf_processor.processor import PDFProcessor
from pdf_processor.image_extractor import ImageExtractor
from table_extractor.extractor import TableExtractor
from llm_client.client import LLMClient
from translator.translator import Translator
from result_saver.saver import ResultSaver
from utils.helpers import setup_logging

class MainApp:
    """主控制器，协调各个组件的工作"""

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.pdf_processor = PDFProcessor(pdf_path)
        self.table_extractor = TableExtractor(pdf_path)
        self.image_extractor = ImageExtractor(pdf_path)  # 可选使用
        self.llm_client = LLMClient(api_key=ARK_API_KEY, model_id=ARK_MODEL_ID)
        self.translator = Translator(self.llm_client)
        self.result_saver = ResultSaver()

    def run(self):
        try:
            # 解析PDF全文
            self.pdf_processor.extract_text()
            paragraphs = self.pdf_processor.split_into_paragraphs()

            # 表格解析
            self.table_extractor.extract_tables()
            if self.table_extractor.table_descriptions:
                paragraphs[-1] += "\n" + "\n".join(self.table_extractor.table_descriptions)

            # 图像提取（如有需要）
            # self.image_extractor.extract_images()

            results = []
            translated_full_text = []

            for idx, p in enumerate(paragraphs):
                logging.info(f"正在处理第 {idx + 1} 段落，共 {len(paragraphs)} 段落")
                # 提取英文摘要和关键词
                summary_en, keywords_en = self.translator.summarize_and_extract_keywords(p)
                logging.debug(f"Parsed Summary (EN): {summary_en}")
                logging.debug(f"Parsed Keywords (EN): {keywords_en}")

                # 翻译为中文
                text_to_translate = f"English Paragraph:\\n{p}\\n\\nEnglish Summary:\\n{summary_en}\\n\\nEnglish Keywords:\\n{keywords_en}"
                zh_paragraph, zh_summary, zh_keywords = self.translator.translate_to_chinese(text_to_translate)
                logging.debug(f"Parsed Paragraph (ZH): {zh_paragraph}")
                logging.debug(f"Parsed Summary (ZH): {zh_summary}")
                logging.debug(f"Parsed Keywords (ZH): {zh_keywords}")

                # 处理关键词列表
                keywords_en_list = [kw.strip() for kw in keywords_en.split(",") if kw.strip()]
                keywords_zh_list = [kw.strip() for kw in zh_keywords.split(",") if kw.strip()]

                results.append({
                    "original_paragraph_en": p,
                    "summary_en": summary_en,
                    "keywords_en": keywords_en_list,
                    "paragraph_zh": zh_paragraph,
                    "summary_zh": zh_summary,
                    "keywords_zh": keywords_zh_list
                })

                # 累积翻译后的段落
                translated_full_text.append(zh_paragraph)

            # 保存结果
            self.result_saver.save_to_json(results, "result.json")
            self.result_saver.save_translated_text(translated_full_text, "translated_paper.txt")

            print("Processing completed. Results saved to result.json and translated_paper.txt")
            logging.info("处理完成，结果已保存到 result.json 和 translated_paper.txt")

        except Exception as e:
            logging.error(f"主程序运行失败: {e}")
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    setup_logging()
    app = MainApp("paper.pdf")
    app.run()
EOF

# 创建简单的测试文件作为示例
cat > tests/test_pdf_processor.py <<EOF
import unittest
from src.pdf_processor.processor import PDFProcessor

class TestPDFProcessor(unittest.TestCase):

    def setUp(self):
        self.pdf_path = "test_paper.pdf"  # 假设测试文件名
        self.processor = PDFProcessor(self.pdf_path)

    def test_extract_text(self):
        # 这里仅作为示例，实际测试需提供测试用pdf文件
        # self.processor.extract_text()
        # self.assertTrue(len(self.processor.full_text) > 0)
        pass

    def test_split_into_paragraphs(self):
        # 同上，此处仅示例
        pass

if __name__ == '__main__':
    unittest.main()
EOF

echo "项目结构已创建完成！"