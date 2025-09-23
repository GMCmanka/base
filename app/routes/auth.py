# app/routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import User

auth_bp = Blueprint('auth', __name__, template_folder='../templates/authan')

@auth_bp.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashboard/index.html')

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash("Login successful", "success")
            return redirect(url_for('auth.home'))
        flash("Invalid username or password", "danger")
    return render_template('authan/login.html')

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        user_type = request.form['user_type']

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash("Username already exists", "danger")
            return redirect(url_for('auth.register'))

        new_user = User(username=username, full_name=full_name, email=email, user_type=user_type)
        new_user.set_password(password)
        new_user.save()
        flash("Account created successfully", "success")
        return redirect(url_for('auth.login'))

    return render_template('authan/register.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash("Logged out successfully", "success")
    return redirect(url_for('auth.login'))
