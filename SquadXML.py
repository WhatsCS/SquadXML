"""
SquadXML is a project that will be generating a squad xml with some custumization for community name. Users will also
be able to add in users and delete users.

1. Create ability to edit a simple config file
2. Add MySQL database configuration options
3. Add community name option
4. Create ability to add and remove users: email, username, etc.
5. Creation of users is on main website (not allowed to log in as they aren't "real users"
6. Create Admin pages
7. Create single use user that is_admin and allow other users in the database to become one as well.
8. Generate required XML file and what not from the database
9. Publish under /squad/squad.xml;/squad/squad.dtd
10. If I have time and aren't a lazy bum I'll make a restful api but atm idgaf
"""
import os
from flask import Flask, url_for, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
import flask_login as login

from wtforms import form, fields, validators
from werkzeug.security import generate_password_hash, check_password_hash

import flask_admin as admin
from flask_admin import BaseView, helpers, expose
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)


# PUT ADMIN STUFF IN HERE, IS ADMIN TABLE MAGIC
class Admins(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username



# NO FLASK-LOGIN AND ADMIN SHIT IN THIS CLASS GOD DAMNIT
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer)
    nick = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    icq = db.Column(db.Integer)
    remark = db.Column(db.String(128))


# Define login forms
class LoginForm(form.Form):

    login = fields.StringField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user

        if user is None:
            raise validators.ValidationError('Invalid User')

        # compare plaintext to hashed version
        if not check_password_hash(user.password, self.password.data):
            raise validators.ValidationError('Invalid Password')

    def get_user(self):
        return db.session.query(Admins).filter_by(username=self.login.data).first()


# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(Admins).get(user_id)


# Create customized model view class
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated


# Create the index view on admin for login
class SquadXMLIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(SquadXMLIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        self._template_args['form'] = form
        return super(SquadXMLIndexView, self).index()

    @expose('/logout')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


@app.route('/')
def index():
    return render_template('index.html')


# Initialize Flask-Login
init_login()


# Customized admin interface
class CustomView(ModelView):

    list_template = 'squad_list.html'
    create_template = 'squad_create.html'
    edit_template = 'squad_edit.html'

# Create admin with custom base template
admin = admin.Admin(app,
                    'SquadXML: Layout',
                    index_view=SquadXMLIndexView(),
                    base_template='layout.html',
                    template_mode='bootstrap3'
                    )

admin.add_view(MyModelView(Admins, db.session))
admin.add_view(MyModelView(User, db.session))


# TODO: Remove this before production
def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    db.drop_all()
    db.create_all()
    # passwords are hashed, to use plaintext passwords instead:
    # test_user = User(login="test", password="test")
    test_user = Admins(username="test", password=generate_password_hash("test"))
    db.session.add(test_user)

    name = [
        'Harry', 'Amelia', 'Oliver', 'Jack', 'Isabella', 'Charlie','Sophie', 'Mia',
        'Jacob', 'Thomas', 'Emily', 'Lily', 'Ava', 'Isla', 'Alfie', 'Olivia', 'Jessica',
        'Riley', 'William', 'James', 'Geoffrey', 'Lisa', 'Benjamin', 'Stacey', 'Lucy'
    ]
    nick = [
        'Brown', 'Smith', 'Patel', 'Jones', 'Williams', 'Johnson', 'Taylor', 'Thomas',
        'Roberts', 'Khan', 'Lewis', 'Jackson', 'Clarke', 'James', 'Phillips', 'Wilson',
        'Ali', 'Mason', 'Mitchell', 'Rose', 'Davis', 'Davies', 'Rodriguez', 'Cox', 'Alexander'
    ]

    for i in range(len(name)):
        user = User()
        user.name = name[i]
        user.nick = nick[i]
        db.session.add(user)

    db.session.commit()
    return

if __name__ == '__main__':

    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db()

    app.run(debug=True)
