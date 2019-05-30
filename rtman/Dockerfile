FROM python:2.7-alpine

# install python packages
RUN apk add --no-cache libxml2-dev libxslt-dev build-base \
    && pip install --user requests jinja2 freeopcua numpy \
    && apk del build-base

WORKDIR /rtman/rtman
ENTRYPOINT [ "/bin/ash" ]
