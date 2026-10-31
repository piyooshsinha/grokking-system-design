FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY . .
RUN mkdir -p /var/lib/workbench \
    && python3 tools/study-assistant/study_assistant.py build \
    && useradd --system --uid 10001 workbench \
    && chown -R workbench:workbench /app /var/lib/workbench

USER workbench
EXPOSE 8000
CMD ["python3", "tools/study-assistant/study_assistant.py", "serve", "--host", "0.0.0.0", "--port", "8000", "--no-open"]
