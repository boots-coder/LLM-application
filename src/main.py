import logging
import os
import datetime
from config.config import ARK_API_KEY, ARK_MODEL_ID, TESSERACT_CMD, LATEXOCR_CMD
from src.pdf_processor.processor import PDFProcessor
from src.pdf_processor.image_extractor import ImageExtractor
from src.table_extractor.extractor import TableExtractor
from src.llm_client.client import LLMClient
from src.translator.translator import Translator
from src.result_saver.saver import ResultSaver

def setup_logging():
    log_dir = os.path.join("..", "log")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"log_{current_time}.log")

    logging.basicConfig(
        filename=log_file,
        filemode='w',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

class MainApp:
    """主控制器，可根据模式（pdf 或 text）选择处理PDF或直接翻译文本。"""

    def __init__(self, mode="pdf", pdf_path=None, input_text=None):
        self.mode = mode
        self.pdf_path = pdf_path
        self.input_text = input_text

        self.llm_client = LLMClient(api_key=ARK_API_KEY, model_id=ARK_MODEL_ID)
        self.translator = Translator(self.llm_client)
        self.result_saver = ResultSaver()

        self.result_dir = os.path.join("..", "result")
        if not os.path.exists(self.result_dir):
            os.makedirs(self.result_dir)

        if self.mode == "pdf" and self.pdf_path:
            self.pdf_processor = PDFProcessor(self.pdf_path)
            self.table_extractor = TableExtractor(self.pdf_path)
            self.image_extractor = ImageExtractor(self.pdf_path)
            pdf_basename = os.path.splitext(os.path.basename(self.pdf_path))[0]
            self.result_json_path = os.path.join(self.result_dir, f"{pdf_basename}_result.json")
            self.translated_text_path = os.path.join(self.result_dir, f"{pdf_basename}_translated_paper.txt")
        else:
            current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.result_json_path = os.path.join(self.result_dir, f"text_input_{current_time}_result.json")
            self.translated_text_path = os.path.join(self.result_dir, f"text_input_{current_time}_translated_paper.txt")

    def run_pdf_mode(self):
        if not self.pdf_path:
            raise ValueError("PDF路径未提供")
        self.pdf_processor.extract_text()
        paragraphs = self.pdf_processor.split_into_paragraphs()

        self.table_extractor.extract_tables()
        if self.table_extractor.table_descriptions:
            paragraphs[-1] += "\n" + "\n".join(self.table_extractor.table_descriptions)

        results, translated_full_text = self.process_paragraphs(paragraphs)
        self.result_saver.save_to_json(results, self.result_json_path)
        self.result_saver.save_translated_text(translated_full_text, self.translated_text_path)

        logging.info(f"处理完成，结果已保存到 {self.result_json_path} 和 {self.translated_text_path}")
        return results, translated_full_text

    def run_text_mode(self):
        if not self.input_text:
            raise ValueError("No input text provided.")
        paragraphs = [self.input_text.strip()]
        results, translated_full_text = self.process_paragraphs(paragraphs)

        self.result_saver.save_to_json(results, self.result_json_path)
        self.result_saver.save_translated_text(translated_full_text, self.translated_text_path)

        logging.info(f"文本处理完成，结果已保存到 {self.result_json_path} 和 {self.translated_text_path}")
        return results, translated_full_text

    def process_paragraphs(self, paragraphs):
        results = []
        translated_full_text = []

        for idx, p in enumerate(paragraphs):
            logging.info(f"正在处理第 {idx + 1} 段落，共 {len(paragraphs)} 段落")
            summary_en, keywords_en = self.translator.summarize_and_extract_keywords(p)

            text_to_translate = f"English Paragraph:\n{p}\n\nEnglish Summary:\n{summary_en}\n\nEnglish Keywords:\n{keywords_en}"
            zh_paragraph, zh_summary, zh_keywords = self.translator.translate_to_chinese(text_to_translate)

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

            translated_full_text.append(zh_paragraph)

        return results, translated_full_text

    def run(self):
        if self.mode == "pdf":
            return self.run_pdf_mode()
        elif self.mode == "text":
            return self.run_text_mode()
        else:
            raise ValueError("Invalid mode. Please choose 'pdf' or 'text'.")


if __name__ == "__main__":
    setup_logging()
    user_input_text = "This is a sample English paragraph that I want to translate."
    app = MainApp(mode="text", input_text=user_input_text)
    results, translated_full_text = app.run()