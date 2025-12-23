## Intern Task List (Beginner Friendly)

This file explains what to do and how to approach each task. Follow the steps in order.

### 0) Quick Start (Once)

1. Clone the repo.
2. Create a virtual environment and activate it.
3. Install Python packages:
   - `flask`
   - `flask_sqlalchemy`
   - `psycopg2-binary`
   - `flask-wtf`
4. Create a PostgreSQL database named `admin`.
5. Update the DB connection string if your user/password/host is different.
6. Apply `database.sql` to the database.
7. Run one app:
   - ORM version: `python app.py`
   - Raw SQL version: `python user.py`

### 1) Add Bootstrap Modals, SweetAlert, WTForms, Jinja2, jQuery

Goal: Learn common UI tooling and template patterns.

References:
- Bootstrap Modals: https://getbootstrap.com/docs/4.6/components/modal/
- SweetAlert2: https://sweetalert2.github.io/
- Flask-WTF: https://flask-wtf.readthedocs.io/en/stable/
- Jinja2 Templates: https://jinja.palletsprojects.com/en/3.1.x/templates/
- jQuery: https://api.jquery.com/

Steps:
1. Inspect templates under `templates/` to see current forms and tables.
2. Add a Bootstrap modal for delete confirmation (or edit) in the User view.
3. Replace default browser confirm() with SweetAlert:
   - Use SweetAlert on delete buttons.
4. Add Flask-WTForms:
   - Create a form class for User.
   - Use the form in create/update routes.
   - Render the form fields in Jinja2 templates.
5. Ensure jQuery is included and used where needed for modals and alerts.

Deliverable:
- User create/edit pages use WTForms and SweetAlert for delete.

### 2) Create Role Entity (CRUD) + Relate to User

Goal: Build a new feature end-to-end and connect it with User.

References:
- SQLAlchemy ORM: https://docs.sqlalchemy.org/en/20/orm/
- Flask-SQLAlchemy: https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/
- PostgreSQL Docs: https://www.postgresql.org/docs/

Steps:
1. Create a new `Role` model (or SQL table if using raw SQL).
2. Add a foreign key from `User` to `Role`.
3. Create role routes:
   - List roles
   - Add role
   - Edit role
   - Delete role
4. Build templates for role CRUD (list, add, edit, delete).
5. Update User create/edit:
   - Replace user_type text input with a role dropdown.
   - Load roles from DB and show them in the select.

Deliverable:
- Roles can be created and assigned to users.

### 3) Pagination + Lazy Loading (DataTables + Select2)

Goal: Learn pagination and async loading on big data.

References:
- DataTables: https://datatables.net/
- DataTables Server-side: https://datatables.net/manual/server-side
- Select2: https://select2.org/
- Select2 AJAX: https://select2.org/data-sources/ajax

Steps:
1. Add DataTables to Users list and Roles list.
2. Start with client-side DataTables on small data.
3. Then add server-side pagination (lazy load):
   - Create an endpoint that returns JSON data for DataTables.
   - Use page number / limit to return chunks.
4. Replace the Role dropdown on user forms with Select2:
   - Load roles via AJAX.
   - Support searching and pagination in Select2.

Deliverable:
- Users and Roles list pages are paginated.
- Role select is async with Select2.

### 4) Blueprints + Separate Modules

Goal: Organize code into clean modules.

References:
- Flask Blueprints: https://flask.palletsprojects.com/en/3.0.x/blueprints/
- Flask App Factories (optional): https://flask.palletsprojects.com/en/3.0.x/patterns/appfactories/

Steps:
1. Create a folder structure like:
   - `users/` (blueprint)
   - `roles/` (blueprint)
2. Inside each feature folder, create:
   - `models.py`
   - `forms.py`
   - `views.py` (routes)
3. Register blueprints in the main app file.
4. Update imports and templates to match the new routes.

Deliverable:
- User and Role logic separated into modules and blueprints.

### 5) Forms, SweetAlert, and Filters

Goal: Polish UX and handle updates cleanly.

References:
- Flask-WTF: https://flask-wtf.readthedocs.io/en/stable/
- SweetAlert2: https://sweetalert2.github.io/
- DataTables Searching: https://datatables.net/examples/api/regex.html

Steps:
1. Create WTForms for edit/update for both User and Role.
2. Use SweetAlert for delete confirmation (User and Role).
3. Add filter/search inputs above list tables:
   - For Users: filter by username, email, role, active status.
   - For Roles: filter by role name.
4. Connect filters to the backend or DataTables search.

Deliverable:
- Edit forms exist for both entities.
- Filters work and delete is confirmed with SweetAlert.

## What You Should Learn

- Flask app structure and blueprints
- SQLAlchemy ORM basics
- Jinja2 templating
- Flask-WTForms
- DataTables pagination and filtering
- Select2 lazy loading
- Bootstrap modals
- SweetAlert confirmations
- jQuery for UI behavior
