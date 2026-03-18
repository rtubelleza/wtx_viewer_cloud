FROM nginx:alpine

RUN sed -i 's/^worker_processes.*/worker_processes auto;/' /etc/nginx/nginx.conf && \
    sed -i 's/worker_connections.*/worker_connections 4096;/' /etc/nginx/nginx.conf

COPY server_config/index.html /usr/share/nginx/html/index.html
COPY server_config/nginx.conf /etc/nginx/conf.d/default.conf
COPY vitessce_config/config.json /usr/share/nginx/html/config.json