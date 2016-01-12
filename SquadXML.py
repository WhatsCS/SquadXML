"""
SquadXML is a project that will be generating a squad xml with some custumization for community name. Users will also
be able to add in users and delete users.

Created by WhatsCS of the 32nd Ranger Battalion: http://32ndrangerbattalion.com
"""
import os
import flask_login as login
import flask_admin as admin
from flask import Flask, url_for, redirect, render_template, request, make_response, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import generate_password_hash, check_password_hash
from sqlalchemy.ext.hybrid import hybrid_property
from wtforms import form, fields, validators
from flask_admin import helpers, expose
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import ModelView


app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)

# PUT ADMIN STUFF IN HERE, IS ADMIN TABLE MAGIC
class Admins(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), unique=True)
    _password = db.Column(db.String(128))

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        self._password = generate_password_hash(plaintext)

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
class Personnel(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer)
    nick = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    icq = db.Column(db.String(5))
    remark = db.Column(db.String(128))


# Define login forms
class LoginForm(form.Form):

    login = fields.StringField(u'Username:', validators=[validators.required()])
    password = fields.PasswordField(u'Password:', validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError(u'Invalid User')

        # compare plaintext to hashed version
        if not check_password_hash(user.password, self.password.data):
            raise validators.ValidationError(u'Invalid Password')

    def get_user(self):
        return db.session.query(Admins).filter_by(login=self.login.data).first()


# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(Admins).get(user_id)


# Create customized Admin Model view class
class AdminModelView(sqla.ModelView):

    def scaffold_form(self):
        form_class = super(AdminModelView, self).scaffold_form()
        form_class.password = fields.PasswordField(u'Password')
        return form_class

    def is_accessible(self):
        return login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('.login_view', next=request.url))


# Create customized model view class
class UserModelView(sqla.ModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('.login_view', next=request.url))


# Create the index view on admin for login
class SquadXMLIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(SquadXMLIndexView, self).index()

    @expose('/login/', methods=['GET', 'POST'])
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


@app.route('/squad/squad.xml')
def xml():
    data = db.session.query(Personnel).all()
    squad_xml = render_template('xml/squad.xml', app=app, data=data)
    response = make_response(squad_xml)
    response.headers["Content-Type"] = "application/xml"

    return response


@app.route('/squad/<path:path>')
def send_squad_pic():
    return send_from_directory(app.config['SQUAD_PICTURE'])


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html',
                           title='404'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html',
                           title='500'), 500



# Initialize Flask-Login
init_login()


# Customized admin interface
class CustomView(ModelView):

    list_template = 'squad_list.html'
    create_template = 'squad_create.html'
    edit_template = 'squad_edit.html'

# Create admin with custom base template
admin = admin.Admin(app,
                    'SquadXML',
                    index_view=SquadXMLIndexView(),
                    base_template='squad_layout.html',
                    template_mode='bootstrap3'
                    )

admin.add_view(AdminModelView(Admins, db.session))
admin.add_view(UserModelView(Personnel, db.session))


# TODO: Remove this before production
def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    db.drop_all()
    db.create_all()
    test_user = Admins(login='admin', password='password')
    db.session.add(test_user)
    db.session.commit()
    return

if __name__ == '__main__':

    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db()

    app.run()
