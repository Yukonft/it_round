from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import nullsfirst
from sqlalchemy.sql.expression import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newflask.db'
db = SQLAlchemy(app)
unlock = False


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.Text)


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/posts')
def posts():
    search_query = request.args.get('q', '').strip()

    if search_query:
        filtered_posts = Post.query.filter(
            (Post.title.ilike(f'%{search_query}%')) |
            (Post.text.ilike(f'%{search_query}%'))
        ).all()
        posts = filtered_posts
    else:
        posts = Post.query.all()

    if unlock:
        return render_template('posts.html',
                               posts=posts,
                               search_query=search_query)
    else:
        return "Для действий на сайте выполните вход!"


@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    post = Post.query.get_or_404(id)
    try:
        db.session.delete(post)
        db.session.commit()
        return redirect('/posts')
    except:
        return "При удалении статьи произошла ошибка!"


@app.route('/create', methods=["POST", "GET"])
def create():
    if unlock:
        if request.method == 'POST':
            title = request.form['title']
            text = request.form["text"]

            post = Post(title=title, text=text)

            try:
                db.session.add(post)
                db.session.commit()
                return redirect('/')
            except:
                return "При добавлении статьи произошла ошибка!"

        else:
            return render_template("create.html")
    else:
        return "Для действий на сайте выполните вход!"



@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/registration', methods=["POST", "GET"])
def registration():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User(email=email, password=password)

        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/')

        except:
            return "При добавлении пользователя произошла ошибка! Возможно пользователь с такой почтой уже есть!"

    else:
        return render_template("registration.html")


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user:
            return "Пользователь не найден"

        if user.password != password:
            return "Неверный пароль"
        global unlock
        unlock = True
        return "Вход выполнен успешно!"

    return render_template("login.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
