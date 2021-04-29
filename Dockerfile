FROM tiangolo/meinheld-gunicorn-flask:python3.7
COPY app/ /app
ENV STATIC_PATH /app/static
RUN pip install -r /app/requirements.txt