FROM nginx:stable-alpine-perl

RUN sed -i 's/^worker_processes.*/worker_processes auto;/' /etc/nginx/nginx.conf && \
    sed -i 's/worker_connections.*/worker_connections 4096;/' /etc/nginx/nginx.conf

COPY data_config/cache.conf /etc/nginx/conf.d/cache.conf
COPY data_config/nginx.conf /etc/nginx/conf.d/default.conf.template
COPY data_config/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && \
    mkdir -p /var/cache/nginx/zarr

ENTRYPOINT ["/entrypoint.sh"]
