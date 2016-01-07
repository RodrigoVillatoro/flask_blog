from flask import flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user

import tasks

from my_app import app, db, login_manager
from forms import LoginForm, ResetPasswordForm
from models import User


@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form = LoginForm(request.form)
        if form.validate():
            login_user(form.user, remember=form.remember_me.data)
            flash(
                'Successfully logged in as {}'.format(form.user.email),
                'success'
            )
            return redirect(request.args.get('next') or url_for('homepage'))
    else:
        form = LoginForm()
    return render_template('login.html', form=form)


@app.route('/logout/')
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(request.args.get('next') or url_for('homepage'))


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        user_email = request.form.get('email')
        user = User.query.filter(User.email == user_email).first()
        if user:
            new_password = 'something'
            user.password_hash = user.make_password(new_password)
            db.session.add(user)
            db.session.commit()
            tasks.send_password_verification(user.email, new_password)
            flash('Verification email sent', 'success')
        else:
            flash('User not found', 'danger')
        return redirect(url_for('homepage'))
    else:
        form = ResetPasswordForm()
    return render_template('reset.html', form=form)
