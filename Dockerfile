
# https://testdriven.io/blog/deploying-django-to-heroku-with-docker/

#FROM python:3.8-alpine AS build-python
#FROM python:alpine3.17 AS build-python
FROM python:3.10.10-slim-bullseye AS build-python

RUN apt-get update && apt-get install apt-utils && apt-get install --assume-yes wget build-essential fakeroot devscripts autoconf automake libtool;



FROM build-python AS build-python2

# https://github.com/yongaru/alpine-mecab-ko/blob/master/Dockerfile
#LABEL maintainer "Yongaru <akira76@gmail.com>"
# MECAB 버전 및 파일 경로
ENV MECAB_KO_FILENAME "mecab-0.996-ko-0.9.2"
ENV MECAB_KO_URL "https://bitbucket.org/eunjeon/mecab-ko/downloads/$MECAB_KO_FILENAME.tar.gz"

ENV MECAB_KO_DIC_FILENAME "mecab-ko-dic-2.1.1-20180720"
ENV MECAB_KO_DIC_URL "https://bitbucket.org/eunjeon/mecab-ko-dic/downloads/$MECAB_KO_DIC_FILENAME.tar.gz"

#if building mecab-ko outside this docker purpose, ie for running uncontainered locally, may need to install autoconf automake, then do ./configure, make, sudo make install
# and for the dictionary, may need libtool which cna then be used to run: (thanks https://stackoverflow.com/questions/40962711/configure-warning-missing-script-is-too-old-or-missing)
# autoreconf -fi
# sh ./autogen.sh
# ./configure
# make
# #which suggests "To enable dictionary, rewrite /usr/local/etc/mecabrc as "dicdir = /usr/local/lib/mecab/dic/mecab-ko-dic"", although not clear this is needed
# sudo make install
# that should do it and now you should have "mecab" command in path which is then used by mecab-python3 python package

RUN wget -O - $MECAB_KO_URL | tar zxfv - &&\
    cd $MECAB_KO_FILENAME && ./configure && make && make install && cd .. && ldconfig ;
#ldconfig above so /usr/local/lib library path is included in lib search path



FROM build-python2 AS build-python2p5
    
RUN wget -O - $MECAB_KO_DIC_URL | tar zxfv - &&\
    cd $MECAB_KO_DIC_FILENAME && autoreconf -fi && sh ./autogen.sh && ./configure && make && make install && cd .. ;

#RUN apk add --no-cache libstdc++ ;\
#    apk --no-cache add --virtual .builddeps build-base autoconf automake ;\
#    wget -O - $MECAB_KO_URL | tar zxfv - ;\
#    cd $MECAB_KO_FILENAME; ./configure; make; make install ;cd .. ;\
#    wget -O - $MECAB_KO_DIC_URL | tar zxfv - ;\
#    cd $MECAB_KO_DIC_FILENAME; sh ./autogen.sh ; ./configure; make; make install ; cd ..; \
#    rm -rf mecab-* \
#    apk del .builddeps ;    

    

    
    
FROM build-python2p5 AS build-python3

COPY ./requirements.txt .

RUN pip install "setuptools<58.0.0"

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt ;

    
# https://testdriven.io/blog/deploying-django-to-heroku-with-docker/

#FROM python:3.8-alpine AS stage1
#FROM python:alpine3.17 AS stage1
FROM python:3.10.10-slim-bullseye AS stage1


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

COPY --from=build-python3 /usr/local/bin/mecab* /usr/local/bin/
COPY --from=build-python3 /usr/local/etc/mecab* /usr/local/etc/
COPY --from=build-python3 /usr/local/include/mecab* /usr/local/include/
COPY --from=build-python3 /usr/local/lib/libmecab* /usr/local/lib/
COPY --from=build-python3 /usr/local/lib/mecab/dic/mecab-ko-dic/* /usr/local/lib/mecab/dic/mecab-ko-dic/
COPY --from=build-python3 /usr/local/libexec/mecab/mecab* /usr/local/libexec/mecab/
#COPY --from=build-python /usr/local/share/man/man1/mecab* /usr/local/share/man/man1/

COPY --from=build-python3 /wheels /wheels
COPY --from=build-python3 requirements.txt .

#old:
#&& apk add postgresql-dev
#&& pip install psycopg2 
#and unclear if some of below can be removed as well as these were beteween the adding and removing of build-deps
#RUN apk update \
#    && apk add --virtual build-deps gcc python3-dev musl-dev \
#    && apk del build-deps \
#    && pip install --no-cache /wheels/*

RUN pip install --no-cache /wheels/*




FROM stage1 AS stage2

#WORKDIR /app
#COPY . .

#RUN python manage.py collectstatic --noinput
#RUN adduser -D myuser

RUN useradd -ms /bin/bash myuser
USER myuser
WORKDIR /home/myuser

WORKDIR ./app
COPY . .

CMD gunicorn app:app --bind 0.0.0.0:$PORT


