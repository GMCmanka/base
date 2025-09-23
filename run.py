#!/usr/bin/env python3
from app import create_app, db
from app.models import Role, Permission

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # Default roles
        default_roles = ["Admin", "Manager", "Normal"]
        for r in default_roles:
            if not Role.query.filter_by(name=r).first():
                Role(name=r, description=f"{r} role").save()

        # Default permissions
        default_permissions = [
            ("view_users", "Can view user list"),
            ("edit_users", "Can edit users"),
            ("delete_users", "Can delete users"),
            ("manage_roles", "Can manage roles"),
        ]
        for name, desc in default_permissions:
            if not Permission.query.filter_by(name=name).first():
                Permission(name=name, description=desc).save()

    app.run(debug=True)
