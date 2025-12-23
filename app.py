from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:aothecode@127.0.0.1/admin'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
Base = declarative_base()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    user_type = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    def update(self):
        db.session.commit()
        return self


@app.route('/')
def home():
    return render_template('dashboard/index.html')


@app.route('/user')
def user():
    result = User.query.all()
    return render_template('user/user.html', data=result)


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
        data = User(username=username, full_name=fullname, email=email, user_type=user_type, is_active=user_status)
        data.save()
        return redirect(url_for('user'))

    return render_template('user/user_add.html', data=[])


@app.route('/user/edit/<user_id>', methods=['GET', 'POST'])
def user_edit(user_id):
    data = User.query.get(user_id)
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
        data.username = username
        data.full_name = fullname
        data.email = email
        data.user_type = user_type
        data.save()
        return redirect(url_for('user'))
    return render_template('user/user_edit.html', data=data)


@app.route('/user/delete/<user_id>', methods=['GET', 'POST'])
def user_delete(user_id):
    data = User.query.get(user_id)
    if request.method == 'POST':
        data.delete()
        return redirect(url_for('user'))
    return render_template('user/user_delete.html', data=data)


if __name__ == '__main__':
    app.run()
