from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz


# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
# create the extension
db = SQLAlchemy(app)
# initialize the app with the extension
# db.init_app(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # nullable=False: 空文字を許可しない
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, 
                            default=datetime.now(pytz.timezone('Asia/Tokyo')))


# 初期画面の表示機能
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # データベースからデータを取得
        posts = Post.query.all()
        # テンプレートにデータを渡す
        return render_template('index.html', posts=posts)

# 新規登録の機能を実装
@app.route('/create', methods=['GET', 'POST'])
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
def delete(id):
    post = Post.query.get(id)

    db.session.delete(post)
    db.session.commit()

    return redirect('/')

    
