import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
import threading
from src.main import MainApp

class TranslatorGUI:
    def __init__(self, master):
        self.master = master
        master.title("PDF/Text Translator")

        self.mode = tk.StringVar(value="pdf")  # 默认pdf模式

        # 模式选择区域
        mode_frame = tk.LabelFrame(master, text="选择模式", padx=10, pady=10)
        mode_frame.pack(padx=10, pady=10, fill="x")

        self.pdf_radio = tk.Radiobutton(mode_frame, text="PDF模式", variable=self.mode, value="pdf",
                                        command=self.on_mode_change)
        self.pdf_radio.pack(anchor="w")

        self.text_radio = tk.Radiobutton(mode_frame, text="文本模式", variable=self.mode, value="text",
                                         command=self.on_mode_change)
        self.text_radio.pack(anchor="w")

        # PDF模式控件
        self.pdf_frame = tk.Frame(master)

        tk.Label(self.pdf_frame, text="选择PDF文件:").pack(side="left", padx=5)
        self.pdf_path_var = tk.StringVar()
        self.pdf_entry = tk.Entry(self.pdf_frame, textvariable=self.pdf_path_var, width=40)
        self.pdf_entry.pack(side="left", padx=5)
        self.pdf_browse_btn = tk.Button(self.pdf_frame, text="浏览...", command=self.browse_pdf)
        self.pdf_browse_btn.pack(side="left", padx=5)

        # 文本模式控件
        self.text_frame = tk.Frame(master)
        tk.Label(self.text_frame, text="输入待翻译英文文本:").pack(anchor="w", padx=5)
        self.text_input = tk.Text(self.text_frame, height=10, width=50)
        self.text_input.pack(padx=5, pady=5)

        # 默认先显示pdf模式控件
        self.pdf_frame.pack(fill="x", padx=10, pady=5)

        # 开始处理按钮
        self.start_btn = tk.Button(master, text="开始处理", command=self.start_processing)
        self.start_btn.pack(pady=10)

        # 正在处理的提示标签（初始不显示）
        self.processing_label = tk.Label(master, text="处理中，请稍候...", fg="blue")

        self.on_mode_change()

    def on_mode_change(self):
        mode = self.mode.get()
        if mode == "pdf":
            self.text_frame.forget()
            self.pdf_frame.pack(fill="x", padx=10, pady=5)
        else:
            self.pdf_frame.forget()
            self.text_frame.pack(fill="both", expand=True, padx=10, pady=5)

    def browse_pdf(self):
        pdf_file = filedialog.askopenfilename(filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")])
        if pdf_file:
            self.pdf_path_var.set(pdf_file)

    def start_processing(self):
        mode = self.mode.get()
        if mode == "pdf":
            pdf_path = self.pdf_path_var.get().strip()
            if not pdf_path:
                messagebox.showerror("错误", "请先选择PDF文件")
                return
            self.start_btn.config(state="disabled")
            self.processing_label.pack(pady=5)
            threading.Thread(target=self.run_app, args=(mode, pdf_path, None)).start()
        else:
            input_text = self.text_input.get("1.0", "end").strip()
            if not input_text:
                messagebox.showerror("错误", "请输入待翻译的英文文本")
                return
            self.start_btn.config(state="disabled")
            self.processing_label.pack(pady=5)
            threading.Thread(target=self.run_app, args=(mode, None, input_text)).start()

    def run_app(self, mode, pdf_path, input_text):
        try:
            app = MainApp(mode=mode, pdf_path=pdf_path, input_text=input_text)
            results, translated_full_text = app.run()
            self.master.after(0, self.processing_done_callback, results, translated_full_text)
        except Exception as e:
            self.master.after(0, self.processing_error_callback, e)

    def processing_done_callback(self, results, translated_full_text):
        self.processing_label.pack_forget()
        self.start_btn.config(state="normal")

        # 显示结果窗口
        self.show_result_window(results, translated_full_text)

        messagebox.showinfo("完成", "处理已完成，请查看 ../result 目录中结果文件")

    def processing_error_callback(self, error):
        self.processing_label.pack_forget()
        self.start_btn.config(state="normal")

        messagebox.showerror("错误", f"处理过程中出现问题: {error}")

    def show_result_window(self, results, translated_full_text):
        result_win = Toplevel(self.master)
        result_win.title("处理结果查看")
        result_win.geometry("600x400")

        # 全文翻译
        full_translation = "\n\n".join(translated_full_text)

        # 核心技术总结为所有summary_zh的合并
        core_summary = "\n".join([r["summary_zh"] for r in results if r.get("summary_zh")])

        # 关键词合并
        keywords = []
        for r in results:
            kw_zh = r.get("keywords_zh", [])
            if kw_zh:
                keywords.extend(kw_zh)
        keywords_str = ", ".join(keywords)

        text_box = tk.Text(result_win, wrap="word")
        text_box.pack(fill="both", expand=True)

        display_content = ("【全文翻译】\n" + full_translation + "\n\n"
                           "【核心技术总结】\n" + core_summary + "\n\n"
                           "【关键词】\n" + keywords_str)

        text_box.insert("1.0", display_content)
        text_box.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    gui = TranslatorGUI(root)
    root.mainloop()