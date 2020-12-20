

# https://testdriven.io/blog/deploying-django-to-heroku-with-docker/

FROM python:3.8-alpine AS build-python

# https://github.com/yongaru/alpine-mecab-ko/blob/master/Dockerfile

#FROM alpine:3.8
#LABEL maintainer "Yongaru <akira76@gmail.com>"

# MECAB 버전 및 파일 경로
ENV MECAB_KO_FILENAME "mecab-0.996-ko-0.9.2"
ENV MECAB_KO_URL "https://bitbucket.org/eunjeon/mecab-ko/downloads/$MECAB_KO_FILENAME.tar.gz"

ENV MECAB_KO_DIC_FILENAME "mecab-ko-dic-2.1.1-20180720"
ENV MECAB_KO_DIC_URL "https://bitbucket.org/eunjeon/mecab-ko-dic/downloads/$MECAB_KO_DIC_FILENAME.tar.gz"

COPY ./requirements.txt /

RUN apk add --no-cache libstdc++ ;\
    apk --no-cache add --virtual .builddeps build-base autoconf automake ;\
    wget -O - $MECAB_KO_URL | tar zxfv - ;\
    cd $MECAB_KO_FILENAME; ./configure; make; make install ;cd .. ;\
    wget -O - $MECAB_KO_DIC_URL | tar zxfv - ;\
    cd $MECAB_KO_DIC_FILENAME; sh ./autogen.sh ; ./configure; make; make install ; cd ..; \
    pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt ; \
    apk del .builddeps ;\
    rm -rf mecab-*

    
# https://testdriven.io/blog/deploying-django-to-heroku-with-docker/

FROM python:3.8-alpine AS stage1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

COPY --from=build-python /usr/local/bin/mecab* /usr/local/bin/
COPY --from=build-python /usr/local/etc/mecab* /usr/local/etc/
COPY --from=build-python /usr/local/include/mecab* /usr/local/include/
COPY --from=build-python /usr/local/lib/libmecab* /usr/local/lib/
COPY --from=build-python /usr/local/lib/mecab/dic/mecab-ko-dic/* /usr/local/lib/mecab/dic/mecab-ko-dic/
COPY --from=build-python /usr/local/libexec/mecab/mecab* /usr/local/libexec/mecab/
#COPY --from=build-python /usr/local/share/man/man1/mecab* /usr/local/share/man/man1/

COPY --from=build-python /wheels /wheels
COPY --from=build-python requirements.txt .

RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install psycopg2 \
    && apk del build-deps \
    && pip install --no-cache /wheels/*

    
FROM stage1 AS stage2

WORKDIR /app
COPY . .

#RUN python manage.py collectstatic --noinput
RUN adduser -D myuser
USER myuser
CMD gunicorn app:app --bind 0.0.0.0:$PORT


