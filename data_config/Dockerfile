FROM nginx:stable-alpine-perl

COPY data_config/cache.conf /etc/nginx/conf.d/cache.conf
COPY data_config/nginx.conf /etc/nginx/conf.d/default.conf.template
COPY data_config/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && \
    mkdir -p /var/cache/nginx/zarr

ENTRYPOINT ["/entrypoint.sh"]
