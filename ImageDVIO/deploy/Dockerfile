FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ARG FLAG=DVCTF{DUMMY_FLAG}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/opt/venv/bin:$PATH \
    IMAGEDVIO_BIND=0.0.0.0 \
    IMAGEDVIO_PORT=8080 \
    IMAGEDVIO_BINARY=/home/ctf/bin/ImageDVIO \
    IMAGEDVIO_TIMEOUT=8 \
    IMAGEDVIO_MAX_REQUEST_BYTES=8388608 \
    IMAGEDVIO_MAX_FILES=8

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-venv ca-certificates \
    && python3 -m venv /opt/venv \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

RUN useradd -m -u 31337 -s /usr/sbin/nologin ctf \
    && mkdir -p /home/ctf/bin /home/ctf/web \
    && printf '%s\n' "${FLAG}" > /flag \
    && chmod 444 /flag

COPY ImageDVIO /home/ctf/bin/ImageDVIO
COPY --chown=ctf:ctf app.py index.html /home/ctf/web/
RUN chmod 0555 /home/ctf/bin/ImageDVIO \
    && chmod 0444 /home/ctf/web/app.py

USER ctf
WORKDIR /home/ctf/web

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2).read()" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "2", "--timeout", "15", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
