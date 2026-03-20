FROM nginx:alpine

RUN sed -i 's/^worker_processes.*/worker_processes auto;/' /etc/nginx/nginx.conf && \
    sed -i 's/worker_connections.*/worker_connections 4096;/' /etc/nginx/nginx.conf

COPY server_config/index.html /usr/share/nginx/html/index.html
COPY server_config/nginx.conf /etc/nginx/conf.d/default.conf

ARG GIT_BRANCH=unknown
ARG GIT_HASH=unknown
ARG GIT_DATE=unknown
RUN sed -i \
    -e "s|__GIT_BRANCH__|${GIT_BRANCH}|g" \
    -e "s|__GIT_HASH__|${GIT_HASH}|g" \
    -e "s|__GIT_DATE__|${GIT_DATE}|g" \
    /usr/share/nginx/html/index.html