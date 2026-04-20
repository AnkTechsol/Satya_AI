FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml /app/
RUN pip install .[test]
COPY . /app/
CMD ["uvicorn", "satya.main:app", "--host", "0.0.0.0", "--port", "8000"]
