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
            self.full_text = "\n\n".join(text_pages)
            logging.info("PDF文本提取完成")
        except Exception as e:
            logging.error(f"解析PDF失败: {e}")
            raise

    def split_into_paragraphs(self):
        try:
            paragraphs = [p.strip() for p in self.full_text.split('\n\n') if p.strip()]
            logging.info(f"PDF文本分段完成，共分割出 {len(paragraphs)} 段")
            return paragraphs
        except Exception as e:
            logging.error(f"分段失败: {e}")
            raise
