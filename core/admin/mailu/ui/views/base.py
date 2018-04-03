from mailu import dockercli, app, db, models, protos_client, protos_domain
from mailu.ui import ui, forms, access

import flask
import flask_login

from urllib import parse


@ui.route('/', methods=["GET"])
@access.authenticated
def index():
    return flask.redirect(flask.url_for('.user_settings'))


@ui.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = None
        if app.config['PROTOS_URL']:
            username, domain = form.email.data.split('@')
            if domain != protos_domain:
                flask.flash('Wrong e-mail or password', 'error')
            user_protos = protos_client.authenticate_user(username, form.pw.data)
            if user_protos:
                user = models.User.query.get(form.email.data)
                if not user:
                    user = create_user(username, domain, name=user_protos['name'], is_admin=user_protos['isadmin'])
        else:
            user = models.User.login(form.email.data, form.pw.data)
        if user:
            flask_login.login_user(user)
            endpoint = flask.request.args.get('next', '.index')
            return flask.redirect(flask.url_for(endpoint)
                or flask.url_for('.index'))
        else:
            flask.flash('Wrong e-mail or password', 'error')
    return flask.render_template('login.html', form=form)

def create_user(username, domain_name, name="", is_admin=False):
    domain = models.Domain.query.get(domain_name)
    if not domain:
        domain = models.Domain(name=domain_name)
        db.session.add(domain)
    user = models.User(
        localpart=username,
        domain=domain,
        displayed_name=name,
        global_admin=is_admin
    )
    user.set_password('randompassword', hash_scheme=app.config['PASSWORD_SCHEME'])
    db.session.add(user)
    db.session.commit()
    return user

@ui.route('/logout', methods=['GET'])
@access.authenticated
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('.index'))


@ui.route('/services', methods=['GET'])
@access.global_admin
def services():
    try:
        containers = dockercli.get()
    except Exception as error:
        return flask.render_template('docker-error.html', error=error)
    return flask.render_template('services.html', containers=containers)


@ui.route('/announcement', methods=['GET', 'POST'])
@access.global_admin
def announcement():
    form = forms.AnnouncementForm()
    if form.validate_on_submit():
        for user in models.User.query.all():
            user.sendmail(form.announcement_subject.data,
                form.announcement_body.data)
        # Force-empty the form
        form.announcement_subject.data = ''
        form.announcement_body.data = ''
        flask.flash('Your announcement was sent', 'success')
    return flask.render_template('announcement.html', form=form)
