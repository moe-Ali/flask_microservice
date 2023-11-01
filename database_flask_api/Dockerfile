FROM ubuntu

USER root
RUN apt update -y
RUN apt install python3 python3-pip python3-dev libmysqlclient-dev pkg-config-y
RUN pip install flask Flask-SQLAlchemy mysqlclient flask-graphql graphene-sqlalchemy
COPY ./money_app_api /tmp/money_app_api
RUN chmod 777 /tmp/money_app_api

RUN useradd python_flask
USER python_flask

ENV PYTHON_USERNAME=
ENV PYTHON_PASSWORD=
ENV PYTHON_HOST=
ENV PYTHON_PORT=
ENV PYTHON_DATABASE_NAME=
ENV PYTHON_TABLE_NAME=

CMD [ "python3", "/tmp/money_app_api/main.py" ]