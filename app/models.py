# ======================================================
# models.py
# ======================================================
from datetime import datetime
from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

# ======================================================
# Association Tables
# ======================================================
user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id"), primary_key=True),
)

role_permissions = db.Table(
    "role_permissions",
    db.Column("role_id", db.Integer, db.ForeignKey("role.id"), primary_key=True),
    db.Column("permission_id", db.Integer, db.ForeignKey("permission.id"), primary_key=True),
)

# ======================================================
# User Model
# ======================================================
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(20), default="Normal")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    roles = db.relationship(
        "Role", secondary=user_roles, backref=db.backref("users", lazy="dynamic")
    )

    def set_password(self, password: str):
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def has_permission(self, permission_name: str) -> bool:
        """Check if user has permission via roles"""
        return any(
            perm.name == permission_name
            for role in self.roles
            for perm in role.permissions
        )

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self


# ======================================================
# Role Model
# ======================================================
class Role(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    permissions = db.relationship(
        "Permission",
        secondary=role_permissions,
        backref=db.backref("roles", lazy="dynamic"),
    )

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self


# ======================================================
# Permission Model
# ======================================================
class Permission(db.Model):
    __tablename__ = "permission"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self
