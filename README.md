# Flask User Management Learning Project

This project is a learning sandbox for Flask. It includes two equivalent user-management
implementations:

- `app.py` uses SQLAlchemy ORM models.
- `user.py` uses raw SQL queries with SQLAlchemy sessions.

Both versions render the same UI and share the same templates and static assets. The goal is
to help an intern set up the project, run it, and complete a set of feature tasks covering
Flask, SQLAlchemy ORM, Jinja2, WTForms, Bootstrap modals, SweetAlert, DataTables, and Select2.

## Project Structure

- `app.py` - ORM-based Flask app.
- `user.py` - Raw SQL-based Flask app.
- `templates/` - Jinja2 HTML templates for users, roles, and layouts.
- `static/` - CSS/JS assets (Bootstrap, DataTables, Select2, SweetAlert, jQuery).
- `database.sql` - Seed schema or starter SQL.

## Setup and Run

1. Clone the repo.
2. Create and activate a virtual environment.
3. Install dependencies:
   - `flask`
   - `flask_sqlalchemy`
   - `psycopg2-binary`
4. Create a PostgreSQL database named `admin` and update the connection string if needed:
   - `postgresql://postgres:aothecode@127.0.0.1/admin`
5. Apply `database.sql` to your database.
6. Run one of the apps:
   - ORM version: `python app.py`
   - Raw SQL version: `python user.py`

## Intern Task List

### 1) Bootstrap and Project Modularization

- Set up Bootstrap modals, SweetAlert confirmations, and jQuery where needed.
- Introduce Flask blueprints for modularization.
- Add Flask-WTForms and use Jinja2 for templating.

### 2) Roles Feature (CRUD)

- Create a Role entity with list/create/update/delete.
- Link Users to Roles (relationship).
- On user creation, allow selecting a Role from the existing list.

### 3) Pagination and Lazy Loading

- Add pagination for both Users and Roles using DataTables (server-side or lazy load).
- Use Select2 for role selection with lazy loading on the user creation form.

### 4) Blueprints and Separation of Concerns

- Split the project into modules:
  - `users/` and `roles/` blueprints.
  - Separate files for models, forms, and routes (views).

### 5) UX Improvements and Filters

- Add edit/update forms (models or WTForms) for both entities.
- Use SweetAlert for delete confirmations.
- Add filter inputs above each list (Users and Roles).

## Learning Outcomes

After completing the tasks, the intern should be comfortable with:

- Flask app structure and blueprints
- SQLAlchemy ORM fundamentals
- Jinja2 templating
- Flask-WTForms
- DataTables pagination and filtering
- Select2 lazy loading
- Bootstrap modals
- SweetAlert confirmations
- jQuery integration
