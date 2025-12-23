from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:aothecode@127.0.0.1/admin'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# initialize the app with Flask-SQLAlchemy
db.init_app(app)


@app.route('/')
def home():
    return render_template('dashboard/index.html')


@app.route('/user')
def user():
    result = db.session.execute(text('SELECT id, username, full_name, email, user_type, is_active FROM public."user";'))
    data = []
    for r in result:
        row = {
            'id': r[0],
            'username': r[1],
            'full_name': r[2],
            'email': r[3],
            'user_type': r[4],
            'is_active': r[5],
        }
        data.append(row)
    return render_template('user/user.html', data=data)


@app.route('/user/add', methods=['GET', 'POST'])
def user_add():
    if request.method == 'POST':
        print("username: ", request.form['username'])
        print("fullname: ", request.form['fullname'])
        print("email: ", request.form['email'])
        print("user_type: ", request.form['user_type'])
        print("form: ", request.form)
        user_status = "user_status" in request.form
        print("user_status: ", user_status)
        username = request.form['username']
        fullname = request.form['fullname']
        email = request.form['email']
        user_type = request.form['user_type']

        result = db.session.execute(text(
            f"""INSERT INTO "user" (username, full_name, email, user_type, is_active) VALUES ('{username}','{fullname}', '{email}', '{user_type}', {user_status} )"""))
        db.session.commit()
        print("success", result)
        return redirect(url_for('user'))

    return render_template('user/user_add.html', data=[])


@app.route('/user/edit/<user_id>', methods=['GET', 'POST'])
def user_edit(user_id):
    result = db.session.execute(
        text(f'SELECT id, username, full_name, email, user_type, is_active FROM public."user" WHERE id = {user_id}'))
    data = None
    for r in result:
        data = {
            'id': r[0],
            'username': r[1],
            'full_name': r[2],
            'email': r[3],
            'user_type': r[4],
            'is_active': r[5],
        }
    if request.method == 'POST':
        print("username: ", request.form['username'])
        print("fullname: ", request.form['fullname'])
        print("email: ", request.form['email'])
        print("user_type: ", request.form['user_type'])
        print("form: ", request.form)
        user_status = "user_status" in request.form
        print("user_status: ", user_status)
        username = request.form['username']
        fullname = request.form['fullname']
        email = request.form['email']
        user_type = request.form['user_type']

        result = db.session.execute(text(
            f"""UPDATE  "user" SET username ='{username}', full_name='{fullname}', email='{email}', user_type= '{user_type}', is_active={user_status} WHERE id={user_id}"""))
        db.session.commit()
        print("success", result)
        return redirect(url_for('user'))
    return render_template('user/user_edit.html', data=data)


@app.route('/user/delete/<user_id>', methods=['GET', 'POST'])
def user_delete(user_id):
    result = db.session.execute(
        text(f'SELECT id, username, full_name, email, user_type, is_active FROM public."user" WHERE id = {user_id}'))
    data = None
    for r in result:
        data = {
            'id': r[0],
            'username': r[1],
            'full_name': r[2],
            'email': r[3],
            'user_type': r[4],
            'is_active': r[5],
        }
    if request.method == 'POST':
        result = db.session.execute(text(f"""DELETE FROM  "user" WHERE id={user_id}"""))
        db.session.commit()
        print("success", result)
        return redirect(url_for('user'))
    return render_template('user/user_delete.html', data=data)


if __name__ == '__main__':
    app.run()
