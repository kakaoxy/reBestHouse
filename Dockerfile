FROM node:18.12.0-alpine3.16 AS web

WORKDIR /opt/reBestHouse
COPY /web ./web
RUN cd /opt/reBestHouse/web && npm i --registry=https://registry.npmmirror.com && npm run build


FROM python:3.11-slim-bullseye

WORKDIR /opt/reBestHouse
ADD . .
COPY /deploy/entrypoint.sh .

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=core-apt \
    --mount=type=cache,target=/var/lib/apt,sharing=locked,id=core-apt \
    sed -i "s@http://.*.debian.org@http://mirrors.ustc.edu.cn@g" /etc/apt/sources.list \
    && rm -f /etc/apt/apt.conf.d/docker-clean \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone \
    && apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev bash nginx vim curl procps net-tools

RUN pip install poetry -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && poetry config virtualenvs.create false \
    && poetry install

COPY --from=web /opt/reBestHouse/web/dist /opt/reBestHouse/web/dist
ADD /deploy/web.conf /etc/nginx/sites-available/web.conf
RUN rm -f /etc/nginx/sites-enabled/default \ 
    && ln -s /etc/nginx/sites-available/web.conf /etc/nginx/sites-enabled/ 

ENV LANG=zh_CN.UTF-8
EXPOSE 80 443

ENTRYPOINT [ "sh", "entrypoint.sh" ]