import os
import csv
import pdfplumber
import logging

class TableExtractor:
    """负责提取PDF中的表格并保存为CSV"""

    def __init__(self, pdf_path, output_dir='/Users/bootscoder/PycharmProjects/LLM-application/tables'):
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
