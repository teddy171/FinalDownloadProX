FROM debian:bullseye

RUN apt-get update
RUN apt-get install -y python3 python3-pip nginx redis ffmpeg

RUN mkdir /usr/local/src/FinalDownloadProX
ADD . /usr/local/src/FinalDownloadProX
ADD ./config/nginx.conf /etc/nginx/nginx.conf
WORKDIR /usr/local/src/FinalDownloadProX

RUN pip3 install -r requirements.txt
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate

CMD [ "supervisord", "-c", "config/supervisord.conf" ]
