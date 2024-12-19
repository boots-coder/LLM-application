import os

# 从环境变量中读取Ark API Key，如果环境变量未设置则报错
ARK_API_KEY = os.environ["ARK_API_KEY"]
# Ark推理接入点ID（替换为你的实际ID）
ARK_MODEL_ID = "ep-20241219220308-mtmr8"

# tesseract的可执行文件路径，根据实际情况修改
TESSERACT_CMD = "/usr/bin/tesseract"

# latexocr命令行工具路径（假设已编译安装）
LATEXOCR_CMD = "/usr/local/bin/latexocr"