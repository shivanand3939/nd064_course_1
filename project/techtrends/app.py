import sqlite3, json, logging, time
import datetime as dt
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import sys

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global number_of_connections
    number_of_connections += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test'

# Define the main route of the web application
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    frmt_date = dt.datetime.utcfromtimestamp(time.time()).strftime("%Y/%m/%d %H:%M")
    if post is None:
      app.logger.error(frmt_date + '  Post is not found')
      return render_template('404.html'), 404
    else:
      app.logger.debug(frmt_date + ' Article ' + post[2] + ' retrieved')
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    frmt_date = dt.datetime.utcfromtimestamp(time.time()).strftime("%Y/%m/%d %H:%M")
    app.logger.debug(frmt_date + '  About Us')
    return render_template('about.html')

# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        frmt_date = dt.datetime.utcfromtimestamp(time.time()).strftime("%Y/%m/%d %H:%M")
        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.debug(frmt_date + ' ' + title + ' is created')
            return redirect(url_for('index'))


    return render_template('create.html')


# Healthcheck endpoint
@app.route('/healthz')
def healthz():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )

    return response

@app.errorhandler(404)
def page_not_found(e):
    #snip
    frmt_date = dt.datetime.utcfromtimestamp(time.time()).strftime("%Y/%m/%d %H:%M")
    app.logger.error(frmt_date + '  Invalid URL')
    return render_template('404.html'), 404


# Define the About Us page
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    total_connections_sql = ''' SELECT COUNT(*) FROM posts '''
    total_connections = connection.execute(total_connections_sql).fetchall()
    connection.close()

    print(total_connections)
    response = app.response_class(
            response=json.dumps({"db_connection_count":number_of_connections,"post_count":total_connections[0][0]}),
            status=200,
            mimetype='application/json'
    )

    return response

# start the application on port 3111
if __name__ == "__main__":
    logger = logging.getLogger("__name__")
    logging.basicConfig( level=logging.DEBUG)
    h1 = logging.StreamHandler(sys.stdout)
    h1.setLevel(logging.DEBUG)
    h2 = logging.StreamHandler(sys.stderr)
    h2.setLevel(logging.ERROR)

    logger.addHandler(h1)
    logger.addHandler(h2)
    number_of_connections =0
    app.run(host='0.0.0.0', port='3111')
