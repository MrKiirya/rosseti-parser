FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY rosseti_parser/ rosseti_parser/

CMD ["python", "-m", "rosseti_parser"]
