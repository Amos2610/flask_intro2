from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required

from werkzeug.security import generate_password_hash, check_password_hash
import os


from datetime import datetime
import pytz


# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
# パスワードを保存するための環境設定
app.config['SECRET_KEY'] = os.urandom(24)
# create the extension
db = SQLAlchemy(app)
# initialize the app with the extension
# db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # nullable=False: 空文字を許可しない
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, 
                            default=datetime.now(pytz.timezone('Asia/Tokyo')))
    
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # nullable=False: 空文字を許可しない
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(12), nullable=False)

@login_manager.user_loader
def login_user(user_id):
    if isinstance(user_id, str) and user_id.isdigit():
        return User.query.get(int(user_id))
    else:
        return None
    # return User.query.get(int(user_id))


# 初期画面の表示機能
@app.route('/', methods=['GET', 'POST'])
@login_required #ログイン状態でのみ有効
def index():
    if request.method == 'GET':
        # データベースからデータを取得
        posts = Post.query.all()
        # テンプレートにデータを渡す
        return render_template('index.html', posts=posts)
    
# 新規登録の機能を実装
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # データベースに保存されているデータを取得して、テンプレートに渡す
    if request.method == 'POST':
        # フォームから送信されたデータを取得
        username = request.form.get('username')
        password = request.form.get('password')

        # パスワードがNoneでないことを確認する
        if password is None:
            return 'パスワードが提供されていません'
        # データベースに保存するデータを作成
        user = User(username=username, password=generate_password_hash(password, method='sha256'))
        # データベースに保存
        db.session.add(user)
        db.session.commit()
        # 保存後はログインページにリダイレクト
        return redirect('/login')
    else:
        # GETの場合はテンプレートを表示
        return render_template('signup.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    # データベースに保存されているデータを取得して、テンプレートに渡す
    if request.method == 'POST':
        # フォームから送信されたデータを取得
        username = request.form.get('username')
        password = request.form.get('password')
        # ユーザーの名前を合致させる
        user = User.query.filter_by(username=username).first()
        if check_password_hash(user.password, password):
            login_user(user)
            # ログイン情報が正しければログインしてトップページにリダイレクト
            return redirect('/')
        else:
            # ユーザーが存在しないか、パスワードが一致しない場合はエラーメッセージを表示
            return "Invalid username or password"
    else:
        # GETの場合はテンプレートを表示
        return render_template('login.html')
    
# ログアウトの機能を実装
@app.route('/logout')
@login_required #ログイン状態でのみ有効
def logout():
    logout_user()
    return redirect('/login')


# 新規登録の機能を実装
@app.route('/create', methods=['GET', 'POST'])
@login_required #ログイン状態でのみ有効
def create():
    # データベースに保存されているデータを取得して、テンプレートに渡す
    if request.method == 'POST':
        # フォームから送信されたデータを取得
        title = request.form.get('title')
        body = request.form.get('body')
        # データベースに保存するデータを作成
        post = Post(title=title, body=body)
        # データベースに保存
        db.session.add(post)
        db.session.commit()
        # 保存後は一覧ページにリダイレクト
        return redirect('/')
    else:
        # GETの場合はテンプレートを表示
        return render_template('create.html')
    
# 編集の機能を実装
@app.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required #ログイン状態でのみ有効
def update(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        # GETの場合はテンプレートを表示
        return render_template('update.html', post=post)
    else: 
        # フォームから送信されたデータを取得
        post.title = request.form.get('title')
        post.body = request.form.get('body')

        db.session.commit()
        # 保存後は一覧ページにリダイレクト
        return redirect('/')
    
# 削除の機能を実装
@app.route('/<int:id>/delete', methods=['GET'])
@login_required #ログイン状態でのみ有効
def delete(id):
    post = Post.query.get(id)

    db.session.delete(post)
    db.session.commit()

    return redirect('/')

    
