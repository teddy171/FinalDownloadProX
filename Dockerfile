FROM debian:bullseye

RUN apt-get update
RUN apt-get install -y python3 python3-pip nginx

RUN mkdir /usr/FinalDownloadProX
COPY . /usr/FinalDownloadProX
COPY ./config/nginx.conf /etc/nginx/nginx.conf
WORKDIR /usr/FinalDownloadProX

RUN /usr/FinalDownloadProX/config/
RUN pip3 install -r requirements.txt
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate

CMD "supervisor /usr/FinalDownloadProX/config/supervisord.conf"
