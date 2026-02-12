#!/bin/sh
# Fix permissions on volume mount (Railway mounts as root)
mkdir -p /data/.n8n
chown -R node:node /data

# Drop to node user and start n8n
exec su-exec node n8n start
