FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8090 SEATLINE_DB=/data/seatline.sqlite3
WORKDIR /app
COPY app.py index.html ./
RUN mkdir -p /data && useradd --system --uid 10001 seatline \
    && chown -R seatline:seatline /app /data
USER seatline
EXPOSE 8090
CMD ["python3", "app.py"]
