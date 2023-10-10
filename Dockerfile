FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.txt .

RUN apt-get update && \
    apt-get install -y tzdata gcc libxml2-dev libxslt1-dev && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    pip3 install --no-cache-dir -r requirements.txt && \
    apt-get remove -y tzdata && \
    rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 5010

ENTRYPOINT [ "sh", "start.sh" ]
