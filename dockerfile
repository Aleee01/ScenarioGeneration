FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y git bash build-essential cmake python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN git clone https://github.com/IBM/forbiditerative.git /app/forbiditerative && \
    cd /app/forbiditerative && \
    python build.py && \
    chmod +x /app/forbiditerative/*.sh

ENTRYPOINT ["python", "tool.py"]