from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy.exc import IntegrityError
from app.models import User, Role, db

user_bp = Blueprint('user', __name__, template_folder='../templates/user')


# ======================================================
# User List (Paginated)
# ======================================================
@user_bp.route('/')
def user_list():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    users = User.query.order_by(User.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('user/user.html', data=users)


# ======================================================
# Add User
# ======================================================
@user_bp.route('/add', methods=['GET','POST'])
def user_add():
    roles = Role.query.all()
    if request.method == 'POST':
        username = request.form['username'].strip()
        full_name = request.form['fullname'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        user_type = request.form['user_type']
        is_active = 'user_status' in request.form
        selected_roles = request.form.getlist('roles')

        # Prevent duplicate
        if User.query.filter_by(email=email).first():
            flash("Email-kan horey ayuu u diiwaangashan yahay", "danger")
            return redirect(url_for('user.user_add'))

        if User.query.filter_by(username=username).first():
            flash("Username-kan horey ayuu u diiwaangashan yahay", "danger")
            return redirect(url_for('user.user_add'))

        u = User(username=username, full_name=full_name, email=email,
                 user_type=user_type, is_active=is_active)
        u.set_password(password)

        # Add roles
        for role_id in selected_roles:
            role = Role.query.get(int(role_id))
            if role:
                u.roles.append(role)

        try:
            u.save()
            flash("User added successfully", "success")
            return redirect(url_for('user.user_list'))
        except IntegrityError:
            db.session.rollback()
            flash("Email ama Username duplicate ah", "danger")
            return redirect(url_for('user.user_add'))

    return render_template('user/user_add.html', roles=roles)
# ======================================================
# Edit User
# ======================================================
@user_bp.route('/edit/<int:user_id>', methods=['GET','POST'])
def user_edit(user_id):
    user = User.query.get_or_404(user_id)
    roles = Role.query.all()
    if request.method == 'POST':
        new_username = request.form['username'].strip()
        new_email = request.form['email'].strip().lower()
        full_name = request.form['fullname'].strip()
        user_type = request.form['user_type']
        is_active = 'user_status' in request.form
        selected_roles = request.form.getlist('roles')

        # Prevent duplicates excluding current user
        if User.query.filter(User.email==new_email, User.id != user.id).first():
            flash("Email-kan waxaa isticmaala user kale", "danger")
            return redirect(url_for('user.user_edit', user_id=user.id))

        if User.query.filter(User.username==new_username, User.id != user.id).first():
            flash("Username-kan waxaa isticmaala user kale", "danger")
            return redirect(url_for('user.user_edit', user_id=user.id))

        # Update user
        user.username = new_username
        user.full_name = full_name
        user.email = new_email
        user.user_type = user_type
        user.is_active = is_active

        # Update roles
        user.roles = []
        for role_id in selected_roles:
            role = Role.query.get(int(role_id))
            if role:
                user.roles.append(role)

        try:
            db.session.commit()
            flash("User updated successfully", "success")
            return redirect(url_for('user.user_list'))
        except IntegrityError:
            db.session.rollback()
            flash("Error: Email ama Username duplicate ah", "danger")
            return redirect(url_for('user.user_edit', user_id=user.id))

    return render_template('user/user_edit.html', data=user, roles=roles)


# ======================================================
# Delete User
# ======================================================
@user_bp.route('/delete/<int:user_id>', methods=['POST'])
def user_delete(user_id):
    user = User.query.get_or_404(user_id)
    user.delete()
    flash("User deleted successfully", "success")
    return redirect(url_for('user.user_list'))
# ======================================================
# End of user.py
# ======================================================