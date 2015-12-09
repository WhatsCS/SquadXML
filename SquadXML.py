"""
SquadXML is a project that will be generating a squad xml with some custumization for community name. Users will also
be able to add in users and delete users.

1. Create ability to edit a simple config file
2. Add MySQL database configuration options
3. Add community name option
4. Create ability to add and remove users: email, username, etc.
5. Creation of users is on main website (not allowed to log in as they aren't "real users"
6. Create Admin pages
7. Generate required XML file and what not from the database
8. Publish under /squad/squad.xml;/squad/squad.dtd
9. If I have time and aren't a lazy bum I'll make a restful api but atm idgaf
"""
from flask import Flask, url_for, redirect, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
import flask_admin
from flask_admin.contrib import sqla
from flask_admin import helpers as admin_helpers

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

# Define Roles
roles_uesrs = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Interger(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String255))
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


    def __str__(self):
        return self.email

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
