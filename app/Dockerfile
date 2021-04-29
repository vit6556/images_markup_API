FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7
RUN apk --update add bash nano
ENV STATIC_URL /static
ENV STATIC_PATH /root/ai_ijc/Images-mark-up-API/app/static
COPY ./requirements.txt /root/ai_ijc/Images-mark-up-API/requirements.txt
RUN pip install -r /root/ai_ijc/Images-mark-up-API/requirements.txt
