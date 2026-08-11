FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# `gosu` para bajar de privilegios al arrancar el servidor: los pasos previos
# (crear la base, migrar) corren como root porque en Windows necesitan escribir
# sobre el volumen montado.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser && useradd -r -g appuser -d /app -s /usr/sbin/nologin appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Copia del entrypoint fuera de /app: el bind-mount de desarrollo tapa /app y
# se llevaría por delante el original. El `sed` quita los CRLF que mete Git en
# Windows y que impiden ejecutarlo.
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN sed -i 's/\r$//' /usr/local/bin/docker-entrypoint.sh \
    && chmod +x /usr/local/bin/docker-entrypoint.sh

RUN mkdir -p /app/media /app/staticfiles && chown -R appuser:appuser /app

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
