from flask import render_template, request, redirect, url_for, flash
from extensions import db
from . import roles_bp
from .models import Role
from .forms import RoleForm


@roles_bp.route('/')
def role_list():
    """List all roles with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get search query
    search = request.args.get('search', '', type=str)
    
    # Base query
    query = Role.query
    
    # Apply search filter
    if search:
        query = query.filter(Role.name.ilike(f'%{search}%'))
    
    # Paginate
    roles = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('roles/role.html', roles=roles, search=search)


@roles_bp.route('/add', methods=['GET', 'POST'])
def role_add():
    """Add a new role"""
    form = RoleForm()
    
    if request.method == 'POST':
        name = request.form['name']
        role = Role(name=name)
        role.save()
        flash('Role created successfully!', 'success')
        return redirect(url_for('roles.role_list'))
    
    return render_template('roles/role_add.html')


@roles_bp.route('/edit/<role_id>', methods=['GET', 'POST'])
def role_edit(role_id):
    """Edit an existing role"""
    role = Role.query.get(role_id)
    form = RoleForm(obj=role)
    
    if request.method == 'POST':
        role.name = request.form['name']
        role.save()
        flash('Role updated successfully!', 'success')
        return redirect(url_for('roles.role_list'))
    
    return render_template('roles/role_edit.html', role=role)


@roles_bp.route('/delete/<role_id>', methods=['GET', 'POST'])
def role_delete(role_id):
    """Delete a role"""
    role = Role.query.get(role_id)
    
    if request.method == 'POST':
        role.delete()
        flash('Role deleted successfully!', 'success')
        return redirect(url_for('roles.role_list'))
    
    return render_template('roles/role_delete.html', role=role)
