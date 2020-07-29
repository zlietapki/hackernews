FROM python:3.8-slim
WORKDIR /app
COPY ["hackernews", "./hackernews"]
COPY ["main.py", "requirements.txt", "./"]
RUN ["pip", "install", "-r", "requirements.txt"]
EXPOSE 8080
CMD ["python", "main.py"]