FROM python:3.8-slim
LABEL maintainer="pat.edwards@pm.me"
USER root
WORKDIR /app
ADD . /app
RUN pip install --trusted-host pypi.python.org -r requirements.txt
EXPOSE 80
CMD ["python", "app.py"]