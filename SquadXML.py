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
from flask_security import Security

from wtforms import validators

import flask_admin as admin
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config.from_pyfile('config.py')


# db = SQLAlchemy(app)


# Customized admin interface
class CustomView(ModelView):
    list_template = 'list.html'
    create_template = 'create.html'
    edit_template = 'edit.html'


# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     player_id = db.Column(db.Integer)
#     nick = db.Column(db.String(100), unique=True)
#     name = db.Column(db.String(100))
#     email = db.Column(db.String(100))
#     icq = db.Column(db.Integer)
#     remark = db.Column(db.String(128))


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                           title='Home')


# Create admin with custom base template
admin = admin.Admin(app, 'SquadXML: Layout', base_template='layout.html', template_mode='bootstrap3')

if __name__ == '__main__':
    app.run(debug=True)
