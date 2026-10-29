FROM brainicism/bgutil-ytdlp-pot-provider:2.0.2

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-venv python3-pip \
    && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=10000

WORKDIR /srv/app

COPY requirements.txt .
RUN python3 -m venv "$VIRTUAL_ENV" \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh \
    && chown -R node:node /srv/app

USER node

EXPOSE 10000

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD []
