FROM ubuntu

USER root
RUN apt update -y
RUN apt install python3 python3-pip python3-dev -y
RUN pip install flask requests
COPY ./money_app /tmp/money_app
RUN chmod 777 /tmp/money_app

RUN useradd python_flask
USER python_flask

ENV API_HOST=
ENV API_PORT=

CMD [ "python3", "/tmp/money_app/main.py" ]