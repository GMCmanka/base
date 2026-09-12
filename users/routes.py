import csv
import io
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file, current_app
from flask_login import current_user
from extensions import db
from . import users_bp
from .models import User, ActivityLog
from .forms import UserForm
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from datetime import datetime
from functools import wraps
import os


def log_activity(action, details=None):
    """Log user activity"""
    try:
        log = ActivityLog(
            user_id=current_user.id if current_user.is_authenticated else None,
            action=action,
            details=details,
            ip_address=request.remote_addr
        )
        log.save()
    except Exception:
        pass


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or (current_user.role and current_user.role.name != 'Admin'):
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== USER LIST ====================

@users_bp.route('/user')
def user_list():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search = request.args.get('search', '', type=str)
    
    query = User.query
    
    if search:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{search}%'),
                User.full_name.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )
    
    users = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('user/user.html', data=users, search=search)


# ==================== ADD USER ====================

@users_bp.route('/user/add', methods=['GET', 'POST'])
def user_add():
    form = UserForm()
    
    if request.method == 'POST':
        username = request.form['username']
        fullname = request.form['fullname']
        email = request.form['email']
        user_type = request.form['user_type']
        role_id = request.form.get('role_id')
        user_status = "user_status" in request.form
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('This email already exists!', 'danger')
            from roles.models import Role
            roles = Role.query.all()
            return render_template('user/user_add.html', roles=roles)
        
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('This username already exists!', 'danger')
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
            data.set_password('password123')
            data.save()
            log_activity('USER_CREATED', f'Created user: {username}')
            flash('User created successfully!', 'success')
            return redirect(url_for('users.user_list'))
        except IntegrityError:
            db.session.rollback()
            flash('Error creating user!', 'danger')
    
    from roles.models import Role
    roles = Role.query.all()
    return render_template('user/user_add.html', roles=roles)


# ==================== EDIT USER ====================

@users_bp.route('/user/edit/<user_id>', methods=['GET', 'POST'])
def user_edit(user_id):
    data = User.query.get(user_id)
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        
        existing_email = User.query.filter(User.email == email, User.id != user_id).first()
        if existing_email:
            flash('Email already exists!', 'danger')
            from roles.models import Role
            roles = Role.query.all()
            return render_template('user/user_edit.html', data=data, roles=roles)
        
        existing_username = User.query.filter(User.username == username, User.id != user_id).first()
        if existing_username:
            flash('Username already exists!', 'danger')
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
            log_activity('USER_UPDATED', f'Updated user: {username}')
            flash('User updated successfully!', 'success')
            return redirect(url_for('users.user_list'))
        except IntegrityError:
            db.session.rollback()
            flash('Error updating user!', 'danger')
    
    from roles.models import Role
    roles = Role.query.all()
    return render_template('user/user_edit.html', data=data, roles=roles)


# ==================== DELETE USER ====================

@users_bp.route('/user/delete/<user_id>', methods=['GET', 'POST'])
def user_delete(user_id):
    data = User.query.get(user_id)
    
    if request.method == 'POST':
        username = data.username
        data.delete()
        log_activity('USER_DELETED', f'Deleted user: {username}')
        flash('User deleted successfully!', 'success')
        return redirect(url_for('users.user_list'))
    
    return render_template('user/user_delete.html', data=data)


# ==================== PROFILE PAGE ====================

@users_bp.route('/profile')
def profile():
    return render_template('user/profile.html', user=current_user)


# ==================== UPDATE PROFILE ====================

@users_bp.route('/profile/update', methods=['POST'])
def update_profile():
    try:
        current_user.full_name = request.form.get('full_name', current_user.full_name)
        current_user.email = request.form.get('email', current_user.email)
        current_user.phone = request.form.get('phone', current_user.phone)
        
        if 'avatar' in request.files:
            avatar = request.files['avatar']
            if avatar.filename:
                import uuid
                ext = avatar.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                avatar.save(os.path.join(current_app.root_path, 'static', 'assets', 'img', 'profiles', filename))
                current_user.avatar = filename
        
        db.session.commit()
        log_activity('PROFILE_UPDATED', 'Updated profile')
        flash('Profile updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating profile!', 'danger')
    
    return redirect(url_for('users.profile'))


# ==================== SETTINGS PAGE ====================

@users_bp.route('/settings')
def settings():
    return render_template('user/settings.html', user=current_user)


# ==================== UPDATE SETTINGS ====================

@users_bp.route('/settings/update', methods=['POST'])
def update_settings():
    try:
        dark_mode = request.form.get('dark_mode') == 'on'
        current_user.dark_mode = dark_mode
        db.session.commit()
        log_activity('SETTINGS_UPDATED', 'Updated settings')
        flash('Settings saved successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error saving settings!', 'danger')
    
    return redirect(url_for('users.settings'))


# ==================== CHANGE PASSWORD ====================

@users_bp.route('/change-password', methods=['POST'])
def change_password():
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect!', 'danger')
            return redirect(url_for('users.settings'))
        
        if new_password != confirm_password:
            flash('New passwords do not match!', 'danger')
            return redirect(url_for('users.settings'))
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters!', 'danger')
            return redirect(url_for('users.settings'))
        
        current_user.set_password(new_password)
        db.session.commit()
        log_activity('PASSWORD_CHANGED', 'Changed password')
        flash('Password changed successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error changing password!', 'danger')
    
    return redirect(url_for('users.settings'))


# ==================== ACTIVITY LOG ====================

@users_bp.route('/activity')
def activity_log():
    page = request.args.get('page', 1, type=int)
    logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('user/activity.html', logs=logs)


# ==================== EXPORT CSV ====================

@users_bp.route('/export/csv')
def export_csv():
    users = User.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Username', 'Full Name', 'Email', 'Role', 'Status', 'Created'])
    
    for user in users:
        writer.writerow([
            user.id,
            user.username,
            user.full_name,
            user.email,
            user.role.name if user.role else 'N/A',
            'Active' if user.is_active else 'Inactive',
            user.created_at.strftime('%Y-%m-%d') if user.created_at else 'N/A'
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'users_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )


# ==================== API ENDPOINTS ====================

@users_bp.route('/api/users')
def api_users():
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'full_name': u.full_name,
        'email': u.email,
        'role': u.role.name if u.role else None,
        'is_active': u.is_active
    } for u in users])


@users_bp.route('/api/users/<int:user_id>')
def api_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'email': user.email,
        'role': user.role.name if user.role else None,
        'is_active': user.is_active,
        'phone': user.phone,
        'created_at': user.created_at.isoformat() if user.created_at else None
    })
