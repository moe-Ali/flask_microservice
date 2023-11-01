from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_graphql import GraphQLView
from graphene import ObjectType, ID, String, Int, List, Field, Schema, Mutation
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from sqlalchemy import MetaData, Table,exc
import os

username = os.environ.get("PYTHON_USERNAME")
password = os.environ.get("PYTHON_PASSWORD")
host = os.environ.get("PYTHON_HOST")
port = os.environ.get("PYTHON_PORT")
database_name = os.environ.get("PYTHON_DATABASE_NAME")
table_name = os.environ.get("PYTHON_TABLE_NAME")

app= Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = f'mysql://{username}:{password}@{host}:{port}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
metadata = MetaData()

with app.app_context():
    reflected_users = Table('users', metadata, autoload_with=db.engine)
    class ReflectedUser(db.Model): #to get the schema of the existing database
        __table__ = reflected_users

class Users(SQLAlchemyObjectType):
    class Meta:
        model = ReflectedUser

# Display user
class Query(ObjectType):
    user = Field(Users, username=String(required=True))
    
    def resolve_user(self, info, username):
        return db.session.query(ReflectedUser).filter(ReflectedUser.username == username).first()

# Create user
class CreateUser(Mutation):
    class Arguments:
        username = String()
        email = String()
        password = String()

    user = Field(Users)

    def mutate(self, info, username,email,password):
        new_user = ReflectedUser(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return CreateUser(user=new_user)

# Update user
class UpdateUser(Mutation):
    class Arguments:
        username = String()
        money = String()
    user = Field(Users)

    def mutate(self, info, username,money):
        user = db.session.query(ReflectedUser).filter_by(username=username).first()
        user.money = money
        db.session.commit()
        return UpdateUser(user=user)


class Mutation(ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()


schema = Schema(query=Query, mutation=Mutation)


app.add_url_rule('/graphql', view_func=GraphQLView.as_view(
    'graphql',
    schema=schema,
    graphiql=True,
))

if __name__ == '__main__':
    app.run()