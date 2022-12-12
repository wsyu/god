FROM mcr.microsoft.com/playwright/python:v1.28.0-focal
COPY . /app
WORKDIR ./app
# RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN pip install --no-cache-dir --upgrade -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

CMD ["python", "main.py"]
