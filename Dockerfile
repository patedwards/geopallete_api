FROM python:3.8-slim
LABEL maintainer="pat.edwards@pm.me"
USER root
WORKDIR /app
ADD . /app
RUN pip install --trusted-host pypi.python.org -r requirements.txt
EXPOSE 8000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000", "--timeout", "120"]
