FROM python:3.9.0

LABEL maintainer="Bachir Belkhiri"

ENV USERNAME=achour_ar
ENV PASSWORD=AdelAchourTokenPassWord

RUN apt-get update
RUN apt-get install -y libsasl2-dev libldap2-dev libssl-dev

WORKDIR /app

#RUN git clone https://github.com/Barakadz/ldap_api.git
#RUN git clone https://oauth2:glpat-iyHrBjHHBeq3L9VUox13@gitlab.com/anis.ameziane/gsh-ldap-api.git

WORKDIR /app/gsh-ldap-api
COPY . .
RUN pip install --upgrade pip
RUN pip  install -r requirements
RUN pip --no-cache-dir install uwsgi

ENV TZ=Africa/Algiers
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENTRYPOINT ["uwsgi"]

CMD [ "app.ini" ]

EXPOSE 5000