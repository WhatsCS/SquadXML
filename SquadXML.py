"""
SquadXML is a project that will be generating a squad xml with some custumization for community name. Users will also
be able to add in users and delete users.

Created by WhatsCS of the 32nd Ranger Battalion: http://32ndrangerbattalion.com
"""
import os
import flask_admin as admin
from flask import Flask, url_for, redirect, render_template, \
    request, make_response, send_from_directory, abort
from flask_admin import helpers as admin_helpers
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, current_user
from flask_security.forms import LoginForm
from flask_security.utils import encrypt_password
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import generate_password_hash, check_password_hash
from sqlalchemy.ext.hybrid import hybrid_property
from wtforms import form, fields, validators, StringField, PasswordField
from wtforms.validators import InputRequired
from flask_admin import helpers, expose
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import ModelView


app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config['PIC_DIR'] = 'templates/xml'

db = SQLAlchemy(app)

# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class Unit(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(512))

    def __str__(self):
        return self.name


# Contains all personnel information including administrators
# username and password are optional as they are only required for login,
# same with active.
class Personnel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(128))
    active = db.Column(db.Boolean())
    player_id = db.Column(db.Integer)
    nick = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    icq = db.Column(db.String(5))
    remark = db.Column(db.String(128))
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('personnel', lazy='dynamic'))
    #unit = db.relationship('Unit', backref=db.backref('personnel', lazy='dynamic'))

    def __str__(self):
        return self.username


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, Personnel, Role)


class FixedLoginForm(LoginForm):
    email = StringField('Username', [InputRequired()])

security = Security(app, user_datastore,
                    login_form=FixedLoginForm)


# Create customized Admin Model view class
class UserModelView(sqla.ModelView):

    # Don't display the password
    column_exclude_list = ('password',)

    #don't include the standard password field
    form_excluded_columns = ('password',)

    # display human-readable names
    column_auto_select_related = True

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        if current_user.has_role('administrator'):
            return True
        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect
        users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('security.login', next=request.url))

    def scaffold_form(self):
        form_class = super(UserModelView, self).scaffold_form()
        form_class.password2 = PasswordField('Password')
        return form_class

    def on_model_change(self, form, model, is_created):
        if len(model.password2):
            model.password = encrypt_password(model.password2)


# Create the index view on admin for login
# class SquadXMLIndexView(admin.AdminIndexView):
#
#     @expose('/')
#     def index(self):
#         if not current_user.is_authenticated:
#             return redirect(url_for('.login_view'))
#         return super(SquadXMLIndexView, self).index()
#
#     @expose('/login/', methods=['GET', 'POST'])
#     def login_view(self):
#         # handle user login
#         form = LoginForm(request.form)
#         if helpers.validate_form_on_submit(form):
#             user = form.get_user()
#             login_user(user)
#
#         if current_user.is_authenticated:
#             return redirect(url_for('.index'))
#         self._template_args['form'] = form
#         return super(SquadXMLIndexView, self).index()
#
#     @expose('/logout')
#     def logout_view(self):
#         logout_user()
#         return redirect(url_for('.index'))

# TODO: build out custom html views for the new admin sections
# Customized admin interface
#class CustomView(ModelView):
    """
    Will be used for managing separate groups
    """

# Create admin with custom base template
admin = admin.Admin(app,
                    'SquadXML',
                    #index_view=SquadXMLIndexView(),
                    #base_template='squad_layout.html',
                    template_mode='bootstrap3'
                    )

admin.add_view(UserModelView(Personnel, db.session))

# fix flask admin and security compat issues
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
    )

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/squad/<unit>/squad.xml')
def xml(unit):
    data = db.session.query(Personnel).all()
    squad_xml = render_template('xml/%s/squad.xml' % unit, app=app, data=data)
    response = make_response(squad_xml)
    response.headers["Content-Type"] = "application/xml"

    return response


@app.route('/squad/<unit>/<path:filename>')
def uploaded_file(unit, filename):
    return send_from_directory(app.config['PIC_DIR'], filename)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html',
                           title='404'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html',
                           title='500'), 500


if __name__ == '__main__':
    app.run()
