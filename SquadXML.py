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
from flask import Flask, url_for, redirect, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
import flask_login as login

from wtforms import form, fields, validators
from werkzeug.security import check_password_hash

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



# NO FLASK-LOGIN AND ADMIN SHIT IN THIS CLASS GOD DAMNIT
class User(db.Model):

    # TODO: figure out how to have a bool for is_admin
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer)
    nick = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    icq = db.Column(db.Integer)
    remark = db.Column(db.String(128))

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


# Define login forms
class LoginForm(form.Form):

    login = fields.StringField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user

        if user is None:
            raise validators.ValidationError('Invalid User')

        #if user.is_admin is False:
        #    raise validators.ValidationError('User not admin')

        # compare plaintext to hashed version
        if not check_password_hash(user.password, self.password.data):
            raise validators.ValidationError('Invalid Password')

    def get_user(self):
        return app.config['USERNAME']


# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)


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

if __name__ == '__main__':
    app.run(debug=True)
