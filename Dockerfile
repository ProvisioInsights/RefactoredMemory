FROM python:3.12-slim
WORKDIR /app
COPY refactoredmemory /app/refactoredmemory
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
EXPOSE 8765
ENTRYPOINT ["python", "-m", "refactoredmemory", "--db", "/data/memory.sqlite3"]
CMD ["serve", "--host", "127.0.0.1"]
