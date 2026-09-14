import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from extensions import db


def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration - use Render DATABASE_URL if available, else local
    database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:aothecode@127.0.0.1:5433/admin')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Initialize SQLAlchemy with app
    db.init_app(app)
    
    # Create tables and admin user on first run
    with app.app_context():
        from users.models import User
        from roles.models import Role
        db.create_all()
        if not Role.query.filter_by(name='Admin').first():
            admin_role = Role(name='Admin')
            db.session.add(admin_role)
            db.session.commit()
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                full_name='System Admin',
                email='admin@system.com',
                role_id=admin_role.id,
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please login to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        from users.models import User
        return User.query.get(int(user_id))
    
    # Make data available to ALL templates (including header)
    @app.context_processor
    def inject_globals():
        from users.models import User
        from roles.models import Role
        
        if current_user.is_authenticated:
            total_users = User.query.count()
            total_roles = Role.query.count()
            active_users = User.query.filter_by(is_active=True).count()
            inactive_users = User.query.filter_by(is_active=False).count()
            recent_users = User.query.order_by(User.id.desc()).limit(5).all()
            users_by_role = db.session.query(
                Role.name, 
                db.func.count(User.id)
            ).join(User, Role.id == User.role_id).group_by(Role.name).all()
            
            return dict(
                total_users=total_users,
                total_roles=total_roles,
                active_users=active_users,
                inactive_users=inactive_users,
                recent_users=recent_users,
                users_by_role=users_by_role
            )
        return dict(
            total_users=0,
            total_roles=0,
            active_users=0,
            inactive_users=0,
            recent_users=[],
            users_by_role=[]
        )
    
    # Import and register blueprints
    from users import users_bp
    from roles import roles_bp
    
    app.register_blueprint(users_bp)
    app.register_blueprint(roles_bp)
    
    # ==================== AUTH ROUTES ====================
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            remember = request.form.get('remember', False)
            
            from users.models import User
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user, remember=bool(remember))
                flash('Login successful!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('home'))
            else:
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
        from users.models import User
        from roles.models import Role
        
        # Get real counts from database
        total_users = User.query.count()
        total_roles = Role.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        inactive_users = User.query.filter_by(is_active=False).count()
        
        # Get users by role
        users_by_role = db.session.query(
            Role.name, 
            db.func.count(User.id)
        ).join(User, Role.id == User.role_id).group_by(Role.name).all()
        
        # Get recent 5 users
        recent_users = User.query.order_by(User.id.desc()).limit(5).all()
        
        return render_template('dashboard/index.html',
            total_users=total_users,
            total_roles=total_roles,
            active_users=active_users,
            inactive_users=inactive_users,
            users_by_role=users_by_role,
            recent_users=recent_users
        )
    
    return app


# Run the app
if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
