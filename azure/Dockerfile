FROM python:3.8
EXPOSE 3978
COPY requirements.txt /service/requirements.txt
RUN pip install -r service/requirements.txt
COPY .. /service/
WORKDIR /service/
ENTRYPOINT ["sh", "entrypoint.sh"]
