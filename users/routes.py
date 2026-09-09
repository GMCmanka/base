from flask import render_template, request, redirect, url_for, flash
from extensions import db
from . import users_bp
from .models import User
from .forms import UserForm
from sqlalchemy.exc import IntegrityError


@users_bp.route('/user')
def user_list():
    """List all users with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get search query
    search = request.args.get('search', '', type=str)
    
    # Base query
    query = User.query
    
    # Apply search filter
    if search:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{search}%'),
                User.full_name.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )
    
    # Paginate
    users = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('user/user.html', data=users, search=search)


@users_bp.route('/user/add', methods=['GET', 'POST'])
def user_add():
    """Add a new user"""
    form = UserForm()
    
    if request.method == 'POST':
        username = request.form['username']
        fullname = request.form['fullname']
        email = request.form['email']
        user_type = request.form['user_type']
        role_id = request.form.get('role_id')
        user_status = "user_status" in request.form
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('This email already exists! Please use a different email.', 'danger')
            from roles.models import Role
            roles = Role.query.all()
            return render_template('user/user_add.html', roles=roles)
        
        # Check if username already exists
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('This username already exists! Please choose a different username.', 'danger')
            from roles.models import Role
            roles = Role.query.all()
            return render_template('user/user_add.html', roles=roles)
        
        try:
            data = User(
                username=username,
                full_name=fullname,
                email=email,
                user_type=user_type,
                is_active=user_status,
                role_id=role_id if role_id else None
            )
            data.save()
            flash('User created successfully!', 'success')
            return redirect(url_for('users.user_list'))
        except IntegrityError:
            db.session.rollback()
            flash('Error: User with this email or username already exists!', 'danger')
            from roles.models import Role
            roles = Role.query.all()
            return render_template('user/user_add.html', roles=roles)
    
    # Get all roles for dropdown
    from roles.models import Role
    roles = Role.query.all()
    return render_template('user/user_add.html', roles=roles)


@users_bp.route('/user/edit/<user_id>', methods=['GET', 'POST'])
def user_edit(user_id):
    """Edit an existing user"""
    data = User.query.get(user_id)
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        
        # Check if email already exists (excluding current user)
        existing_email = User.query.filter(User.email == email, User.id != user_id).first()
        if existing_email:
            flash('This email already exists! Please use a different email.', 'danger')
            from roles.models import Role
            roles = Role.query.all()
            return render_template('user/user_edit.html', data=data, roles=roles)
        
        # Check if username already exists (excluding current user)
        existing_username = User.query.filter(User.username == username, User.id != user_id).first()
        if existing_username:
            flash('This username already exists! Please choose a different username.', 'danger')
            from roles.models import Role
            roles = Role.query.all()
            return render_template('user/user_edit.html', data=data, roles=roles)
        
        try:
            data.username = username
            data.full_name = request.form['fullname']
            data.email = email
            data.user_type = request.form['user_type']
            data.role_id = request.form.get('role_id') or None
            data.is_active = "user_status" in request.form
            data.save()
            flash('User updated successfully!', 'success')
            return redirect(url_for('users.user_list'))
        except IntegrityError:
            db.session.rollback()
            flash('Error: User with this email or username already exists!', 'danger')
            from roles.models import Role
            roles = Role.query.all()
            return render_template('user/user_edit.html', data=data, roles=roles)
    
    # Get all roles for dropdown
    from roles.models import Role
    roles = Role.query.all()
    return render_template('user/user_edit.html', data=data, roles=roles)


@users_bp.route('/user/delete/<user_id>', methods=['GET', 'POST'])
def user_delete(user_id):
    """Delete a user"""
    data = User.query.get(user_id)
    
    if request.method == 'POST':
        data.delete()
        flash('User deleted successfully!', 'success')
        return redirect(url_for('users.user_list'))
    
    return render_template('user/user_delete.html', data=data)
