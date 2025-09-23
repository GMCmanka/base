# app/routes/role.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy.exc import IntegrityError
from app.models import Role, Permission, db

role_bp = Blueprint('role', __name__, template_folder='../templates/role')

@role_bp.route('/')
def role_list():
    page = request.args.get('page', 1, type=int)
    roles = Role.query.order_by(Role.id.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('role/role.html', roles=roles)

@role_bp.route('/add', methods=['GET', 'POST'])
def role_add():
    permissions = Permission.query.order_by(Permission.name).all()
    if request.method == 'POST':
        # Use .get to avoid KeyError when form field missing
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        selected_perms = request.form.getlist('permissions')

        # Basic validation
        if not name:
            flash("Fadlan gali magaca Role-ka", "danger")
            return redirect(url_for('role.role_add'))

        # Prevent duplicate
        if Role.query.filter_by(name=name).first():
            flash("Magaca Role-ka wuu jiraa horay", "danger")
            return redirect(url_for('role.role_add'))

        role = Role(name=name, description=description)

        for pid in selected_perms:
            try:
                perm = Permission.query.get(int(pid))
            except (ValueError, TypeError):
                perm = None
            if perm:
                role.permissions.append(perm)

        try:
            db.session.add(role)
            db.session.commit()
            flash("✅ Role added successfully", "success")
            return redirect(url_for('role.role_list'))
        except IntegrityError:
            db.session.rollback()
            flash("❌ Error: Role name already exists or DB error", "danger")
            return redirect(url_for('role.role_add'))

    return render_template('role/role_add.html', permissions=permissions)

@role_bp.route('/edit/<int:role_id>', methods=['GET', 'POST'])
def role_edit(role_id):
    role = Role.query.get_or_404(role_id)
    permissions = Permission.query.order_by(Permission.name).all()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        selected_perms = request.form.getlist('permissions')

        if not name:
            flash("Fadlan gali magaca Role-ka", "danger")
            return redirect(url_for('role.role_edit', role_id=role.id))

        # Check uniqueness (exclude current role)
        existing = Role.query.filter(Role.name==name, Role.id != role.id).first()
        if existing:
            flash("Magaca Role-ka waxaa isticmaala role kale", "danger")
            return redirect(url_for('role.role_edit', role_id=role.id))

        role.name = name
        role.description = description

        # reset permissions
        role.permissions = []
        for pid in selected_perms:
            try:
                perm = Permission.query.get(int(pid))
            except (ValueError, TypeError):
                perm = None
            if perm:
                role.permissions.append(perm)

        try:
            db.session.commit()
            flash("✅ Role updated successfully", "success")
            return redirect(url_for('role.role_list'))
        except IntegrityError:
            db.session.rollback()
            flash("❌ Error saving role (duplicate or DB error)", "danger")
            return redirect(url_for('role.role_edit', role_id=role.id))

    return render_template('role/role_edit.html', role=role, permissions=permissions)

@role_bp.route('/delete/<int:role_id>', methods=['POST'])
def role_delete(role_id):
    role = Role.query.get_or_404(role_id)
    try:
        db.session.delete(role)
        db.session.commit()
        flash("✅ Role deleted successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error deleting role: {str(e)}", "danger")
    return redirect(url_for('role.role_list'))
