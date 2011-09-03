# -*- coding: utf-8 -*-
import sys,os
os.environ['DYLD_LIBRARY_PATH'] = '/usr/local/mysql/lib'
os.environ['LD_LIBRARY_PATH'] = '/usr/local/mysql/lib'
import MySQLdb
from flask import Flask, request, g, redirect, url_for, abort, render_template, flash


DB_HOST = 'localhost'
DB_NAME = 'isucon'
DB_USER = ''
DB_PASSWD = ''
DEBUG = True
SECRET_KEY = 'development key'


app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return MySQLdb.connect(host=app.config['DB_HOST'],db=app.config['DB_NAME'],user=app.config['DB_USER'],passwd=app.config['DB_PASSWD'],charset='utf8')



@app.before_request
def before_request():
    g.db = connect_db()
    cur = g.db.cursor()
    cur.execute('SELECT a.id, a.title FROM comment c LEFT JOIN article a ON c.article = a.id GROUP BY a.id ORDER BY MAX(c.created_at) DESC LIMIT 10')
    g.sidebaritems = [dict(id=row[0], title=row[1]) for row in cur.fetchall()]


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/')
def index():
    cur = g.db.cursor()
    cur.execute('SELECT id,title,body,created_at FROM article ORDER BY id DESC LIMIT 10')
    articles = [dict(id=row[0], title=row[1], body=row[2], created_at=row[3]) for row in cur.fetchall()]
    return render_template('index.html', articles=articles, sidebaritems=g.sidebaritems)


@app.route('/post', methods=['GET'])
def get_post():
    return render_template('post.html')


@app.route('/post', methods=['POST'])
def post_post():
    cur = g.db.cursor()
    cur.execute('INSERT INTO article (title, body) VALUES (%s, %s)',
                (request.form['title'], request.form['body']))
    g.db.commit();
    return redirect(url_for('index'))


@app.route('/article/<article_id>', methods=['GET'])
def show_article(article_id):
    cur = g.db.cursor()
    cur.execute('SELECT id,title,body,created_at FROM article WHERE id = %s',
                (article_id))
    article = [dict(id=row[0], title=row[1], body=row[2], created_at=row[3]) for row in cur.fetchall()]
    if len(article) == 1:
        article = article[0]
    else:
        article = null
    if not article:
        abort(404)

    cur.execute('SELECT name,body,created_at FROM comment WHERE article=%s ORDER BY id',
                (article_id))

    comments = [dict(name=row[0], body=row[1], created_at=row[2]) for row in cur.fetchall()]
    g.db.commit();
    return render_template('article.html', article=article, comments=comments, sidebaritems=g.sidebaritems)


@app.route('/comment/<article_id>', methods=['POST'])
def add_comment(article_id):
    cur = g.db.cursor()
    cur.execute('INSERT INTO comment SET article=%s, name=%s, body=%s',
                (article_id, request.form['name'], request.form['body']))
    g.db.commit();
    return redirect(url_for('show_article', article_id=article_id))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
