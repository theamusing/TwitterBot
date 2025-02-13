# 选择基础镜像，例如 Python 3.9
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件到容器
COPY . .

# 安装依赖（假设有 requirements.txt）
RUN pip install --no-cache-dir -r requirements.txt

# 运行 Python 程序（如果是 Flask 或 Django 应用，请修改相应的启动命令）
CMD ["python", "app.py"]
