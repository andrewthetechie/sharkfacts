FROM python:2.7.13-slim
COPY app.py /app.py
COPY facts.txt /facts.txt
RUN pip install bottle pyyaml

EXPOSE 5000

ENTRYPOINT python /app.py