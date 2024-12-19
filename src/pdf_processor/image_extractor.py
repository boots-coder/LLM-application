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
