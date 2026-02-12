FROM n8nio/n8n:latest

USER root

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENV N8N_USER_FOLDER=/data
ENV N8N_PORT=5678

ENTRYPOINT ["/docker-entrypoint.sh"]
