FROM n8nio/n8n:latest

USER root
RUN mkdir -p /data/.n8n && chown -R node:node /data
USER node

ENV N8N_USER_FOLDER=/data
ENV N8N_PORT=5678
