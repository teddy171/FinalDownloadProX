FROM debian:bullseye

RUN apt-get update
RUN apt-get install -y python3 python3-pip nginx sudo

RUN mkdir /usr/FinalDownloadProX -p
COPY . /usr/src/FinalDownloadProX
COPY ./config/nginx.conf /etc/nginx/nginx.conf
WORKDIR /usr/src/FinalDownloadProX

RUN pip3 install -r requirements.txt
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate

CMD "ls /usr/src/FinalDownloadProX/config/"
