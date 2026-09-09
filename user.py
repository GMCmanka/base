"""
Flask User Management - Raw SQL Version
Uses raw SQL queries with SQLAlchemy sessions (no ORM models)
Both versions render the SAME UI with the same templates
"""

from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:aothecode@127.0.0.1:5433/admin'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'your-secret-key-here'

db = SQLAlchemy(app)

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please login to access this page.'

# Blueprints (same names as ORM version for template compatibility)
users_bp = Blueprint('users', __name__)
roles_bp = Blueprint('roles', __name__, url_prefix='/role')


# ==================== WRAPPER CLASSES ====================

class UserRole:
    """Wraps role data to match ORM interface"""
    def __init__(self, id, name):
        self.id = id
        self.name = name


class UserData:
    """Wraps user data to match ORM interface"""
    def __init__(self, user_row, role_name=None, role_id=None):
        self.id = user_row[0]
        self.username = user_row[1]
        self.full_name = user_row[2]
        self.email = user_row[3]
        self.user_type = user_row[4]
        self.is_active = user_row[5]
        self.role_id = user_row[6]
        self.password_hash = user_row[7]
        self.role = UserRole(role_id, role_name) if role_id else None


class UserLogin:
    """Simple User class for Flask-Login"""
    def __init__(self, user_row):
        self.id = user_row[0]
        self.username = user_row[1]
        self.full_name = user_row[2]
        self.email = user_row[3]
        self.user_type = user_row[4]
        self.is_active = user_row[5]
        self.role_id = user_row[6]
        self.password_hash = user_row[7]
        self.role = None

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.is_active

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Pagination:
    """Wraps pagination data to match SQLAlchemy Pagination interface"""
    def __init__(self, items, total, page, per_page):
        self.items = items
        self.total = total
        self.page = page
        self.per_page = per_page
        self.pages = (total + per_page - 1) // per_page
        self.has_prev = page > 1
        self.has_next = page < self.pages
        self.prev_num = page - 1
        self.next_num = page + 1

    def iter_pages(self, left_edge=1, right_edge=1, left_current=1, right_current=1):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current + 1) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


@login_manager.user_loader
def load_user(user_id):
    result = db.session.execute(
        'SELECT * FROM "user" WHERE id = :id', {'id': user_id}
    ).fetchone()
    if result:
        user = UserLogin(result)
        if user.role_id:
            role_result = db.session.execute(
                'SELECT name FROM role WHERE id = :id', {'id': user.role_id}
            ).fetchone()
            if role_result:
                user.role = UserRole(user.role_id, role_result[0])
        return user
    return None


# ==================== HELPER FUNCTIONS ====================

def get_all_roles():
    result = db.session.execute('SELECT * FROM role ORDER BY id').fetchall()
    return [{'id': r[0], 'name': r[1]} for r in result]


def get_role_by_id(role_id):
    result = db.session.execute('SELECT * FROM role WHERE id = :id', {'id': role_id}).fetchone()
    if result:
        return {'id': result[0], 'name': result[1]}
    return None


def get_users_paginated(page, per_page, search=''):
    offset = (page - 1) * per_page
    
    if search:
        query = '''
            SELECT u.*, r.name as role_name, r.id as role_id_ref
            FROM "user" u
            LEFT JOIN role r ON u.role_id = r.id
            WHERE u.username ILIKE :search
               OR u.full_name ILIKE :search
               OR u.email ILIKE :search
            ORDER BY u.id
            LIMIT :limit OFFSET :offset
        '''
        count_query = '''
            SELECT COUNT(*) FROM "user"
            WHERE username ILIKE :search
               OR full_name ILIKE :search
               OR email ILIKE :search
        '''
        users = db.session.execute(query, {'search': f'%{search}%', 'limit': per_page, 'offset': offset}).fetchall()
        total = db.session.execute(count_query, {'search': f'%{search}%'}).fetchone()[0]
    else:
        query = '''
            SELECT u.*, r.name as role_name, r.id as role_id_ref
            FROM "user" u
            LEFT JOIN role r ON u.role_id = r.id
            ORDER BY u.id
            LIMIT :limit OFFSET :offset
        '''
        users = db.session.execute(query, {'limit': per_page, 'offset': offset}).fetchall()
        total = db.session.execute('SELECT COUNT(*) FROM "user"').fetchone()[0]
    
    users_list = []
    for u in users:
        role_name = u[8] if len(u) > 8 else None
        role_id_ref = u[9] if len(u) > 9 else u[6]
        users_list.append(UserData(u, role_name=role_name, role_id=role_id_ref))
    
    return Pagination(users_list, total, page, per_page)


def get_roles_paginated(page, per_page, search=''):
    offset = (page - 1) * per_page
    
    if search:
        query = '''
            SELECT r.*, COUNT(u.id) as user_count
            FROM role r
            LEFT JOIN "user" u ON r.id = u.role_id
            WHERE r.name ILIKE :search
            GROUP BY r.id
            ORDER BY r.id
            LIMIT :limit OFFSET :offset
        '''
        count_query = 'SELECT COUNT(*) FROM role WHERE name ILIKE :search'
        roles = db.session.execute(query, {'search': f'%{search}%', 'limit': per_page, 'offset': offset}).fetchall()
        total = db.session.execute(count_query, {'search': f'%{search}%'}).fetchone()[0]
    else:
        query = '''
            SELECT r.*, COUNT(u.id) as user_count
            FROM role r
            LEFT JOIN "user" u ON r.id = u.role_id
            GROUP BY r.id
            ORDER BY r.id
            LIMIT :limit OFFSET :offset
        '''
        roles = db.session.execute(query, {'limit': per_page, 'offset': offset}).fetchall()
        total = db.session.execute('SELECT COUNT(*) FROM role').fetchone()[0]
    
    roles_list = []
    for r in roles:
        roles_list.append({
            'id': r[0], 'name': r[1], 'users_count': r[2]
        })
    
    return Pagination(roles_list, total, page, per_page)


# ==================== AUTH ROUTES ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        result = db.session.execute(
            'SELECT * FROM "user" WHERE username = :username', {'username': username}
        ).fetchone()
        
        if result:
            user = UserLogin(result)
            if user.check_password(password):
                login_user(user, remember=bool(remember))
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
        
        flash('Invalid username or password!', 'danger')
    
    return render_template('auth/login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ==================== DASHBOARD ====================

@app.route('/')
@login_required
def home():
    total_users = db.session.execute('SELECT COUNT(*) FROM "user"').fetchone()[0]
    total_roles = db.session.execute('SELECT COUNT(*) FROM role').fetchone()[0]
    active_users = db.session.execute('SELECT COUNT(*) FROM "user" WHERE is_active = true').fetchone()[0]
    inactive_users = db.session.execute('SELECT COUNT(*) FROM "user" WHERE is_active = false').fetchone()[0]
    
    users_by_role = db.session.execute('''
        SELECT r.name, COUNT(u.id)
        FROM role r
        LEFT JOIN "user" u ON r.id = u.role_id
        GROUP BY r.name
    ''').fetchall()
    
    recent_users_result = db.session.execute('''
        SELECT u.id, u.username, u.full_name, u.email, u.is_active, r.name
        FROM "user" u
        LEFT JOIN role r ON u.role_id = r.id
        ORDER BY u.id DESC
        LIMIT 5
    ''').fetchall()
    
    recent_users = []
    for u in recent_users_result:
        obj = type('User', (), {
            'id': u[0], 'username': u[1], 'full_name': u[2],
            'email': u[3], 'is_active': u[4],
            'role': type('Role', (), {'name': u[5]})() if u[5] else None
        })()
        recent_users.append(obj)
    
    return render_template('dashboard/index.html',
        total_users=total_users,
        total_roles=total_roles,
        active_users=active_users,
        inactive_users=inactive_users,
        users_by_role=users_by_role,
        recent_users=recent_users
    )


# ==================== USER ROUTES (Blueprint) ====================

@users_bp.route('/')
@login_required
def user_list():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    users = get_users_paginated(page, 10, search)
    return render_template('user/user.html', data=users, search=search)


@users_bp.route('/add', methods=['GET', 'POST'])
@login_required
def user_add():
    if request.method == 'POST':
        username = request.form['username']
        fullname = request.form['fullname']
        email = request.form['email']
        user_type = request.form['user_type']
        role_id = request.form.get('role_id')
        user_status = "user_status" in request.form
        password = request.form.get('password', 'password123')
        
        existing = db.session.execute(
            'SELECT id FROM "user" WHERE email = :email', {'email': email}
        ).fetchone()
        if existing:
            flash('This email already exists!', 'danger')
            return redirect(url_for('users.user_add'))
        
        existing = db.session.execute(
            'SELECT id FROM "user" WHERE username = :username', {'username': username}
        ).fetchone()
        if existing:
            flash('This username already exists!', 'danger')
            return redirect(url_for('users.user_add'))
        
        password_hash = generate_password_hash(password)
        
        db.session.execute('''
            INSERT INTO "user" (username, full_name, email, user_type, is_active, role_id, password_hash)
            VALUES (:username, :fullname, :email, :user_type, :is_active, :role_id, :password_hash)
        ''', {
            'username': username, 'fullname': fullname, 'email': email,
            'user_type': user_type, 'is_active': user_status,
            'role_id': role_id if role_id else None, 'password_hash': password_hash
        })
        db.session.commit()
        
        flash('User created successfully!', 'success')
        return redirect(url_for('users.user_list'))
    
    roles = get_all_roles()
    return render_template('user/user_add.html', roles=roles)


@users_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_edit(user_id):
    result = db.session.execute(
        'SELECT * FROM "user" WHERE id = :id', {'id': user_id}
    ).fetchone()
    
    if not result:
        flash('User not found!', 'danger')
        return redirect(url_for('users.user_list'))
    
    role_name = None
    if result[6]:
        role_result = db.session.execute(
            'SELECT name FROM role WHERE id = :id', {'id': result[6]}
        ).fetchone()
        if role_result:
            role_name = role_result[0]
    
    user = UserData(result, role_name=role_name, role_id=result[6])
    
    if request.method == 'POST':
        username = request.form['username']
        fullname = request.form['fullname']
        email = request.form['email']
        user_type = request.form['user_type']
        role_id = request.form.get('role_id')
        user_status = "user_status" in request.form
        
        db.session.execute('''
            UPDATE "user"
            SET username = :username, full_name = :fullname, email = :email,
                user_type = :user_type, role_id = :role_id, is_active = :is_active
            WHERE id = :id
        ''', {
            'username': username, 'fullname': fullname, 'email': email,
            'user_type': user_type, 'role_id': role_id if role_id else None,
            'is_active': user_status, 'id': user_id
        })
        db.session.commit()
        
        flash('User updated successfully!', 'success')
        return redirect(url_for('users.user_list'))
    
    roles = get_all_roles()
    return render_template('user/user_edit.html', data=user, roles=roles)


@users_bp.route('/delete/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_delete(user_id):
    if request.method == 'POST':
        db.session.execute('DELETE FROM "user" WHERE id = :id', {'id': user_id})
        db.session.commit()
        flash('User deleted successfully!', 'success')
        return redirect(url_for('users.user_list'))
    
    result = db.session.execute(
        'SELECT * FROM "user" WHERE id = :id', {'id': user_id}
    ).fetchone()
    
    user = UserData(result)
    return render_template('user/user_delete.html', data=user)


# ==================== ROLE ROUTES (Blueprint) ====================

@roles_bp.route('/')
@login_required
def role_list():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    roles = get_roles_paginated(page, 10, search)
    return render_template('roles/role.html', roles=roles, search=search)


@roles_bp.route('/add', methods=['GET', 'POST'])
@login_required
def role_add():
    if request.method == 'POST':
        name = request.form['name']
        
        existing = db.session.execute(
            'SELECT id FROM role WHERE name = :name', {'name': name}
        ).fetchone()
        if existing:
            flash('Role already exists!', 'danger')
            return redirect(url_for('roles.role_add'))
        
        db.session.execute('INSERT INTO role (name) VALUES (:name)', {'name': name})
        db.session.commit()
        
        flash('Role created successfully!', 'success')
        return redirect(url_for('roles.role_list'))
    
    return render_template('roles/role_add.html')


@roles_bp.route('/edit/<int:role_id>', methods=['GET', 'POST'])
@login_required
def role_edit(role_id):
    role = get_role_by_id(role_id)
    if not role:
        flash('Role not found!', 'danger')
        return redirect(url_for('roles.role_list'))
    
    if request.method == 'POST':
        name = request.form['name']
        db.session.execute('UPDATE role SET name = :name WHERE id = :id', {'name': name, 'id': role_id})
        db.session.commit()
        
        flash('Role updated successfully!', 'success')
        return redirect(url_for('roles.role_list'))
    
    return render_template('roles/role_edit.html', role=role)


@roles_bp.route('/delete/<int:role_id>', methods=['GET', 'POST'])
@login_required
def role_delete(role_id):
    if request.method == 'POST':
        db.session.execute('DELETE FROM role WHERE id = :id', {'id': role_id})
        db.session.commit()
        flash('Role deleted successfully!', 'success')
        return redirect(url_for('roles.role_list'))
    
    role = get_role_by_id(role_id)
    return render_template('roles/role_delete.html', role=role)


# ==================== REGISTER BLUEPRINTS ====================

app.register_blueprint(users_bp)
app.register_blueprint(roles_bp)


# ==================== CONTEXT PROCESSOR ====================

@app.context_processor
def inject_globals():
    if current_user.is_authenticated:
        total_users = db.session.execute('SELECT COUNT(*) FROM "user"').fetchone()[0]
        total_roles = db.session.execute('SELECT COUNT(*) FROM role').fetchone()[0]
        active_users = db.session.execute('SELECT COUNT(*) FROM "user" WHERE is_active = true').fetchone()[0]
        inactive_users = db.session.execute('SELECT COUNT(*) FROM "user" WHERE is_active = false').fetchone()[0]
        recent_users_result = db.session.execute('''
            SELECT u.id, u.username, u.full_name, u.email, u.is_active, r.name
            FROM "user" u LEFT JOIN role r ON u.role_id = r.id
            ORDER BY u.id DESC LIMIT 5
        ''').fetchall()
        
        recent_users = []
        for u in recent_users_result:
            obj = type('User', (), {
                'id': u[0], 'full_name': u[2], 'is_active': u[4]
            })()
            recent_users.append(obj)
        
        return dict(
            total_users=total_users,
            total_roles=total_roles,
            active_users=active_users,
            inactive_users=inactive_users,
            recent_users=recent_users
        )
    return dict(total_users=0, total_roles=0, active_users=0, inactive_users=0, recent_users=[])


# ==================== RUN APP ====================

if __name__ == '__main__':
    app.run(debug=True, port=5001)
