from functools import wraps

from alayatodo import app
from flask import (
    g,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
	abort,
    session
    )

def login_required(view_function):
    @wraps(view_function)
    def _wrapped(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return view_function(*args, **kwargs)
    return _wrapped

@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l.decode('utf-8') for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    if session.get('logged_in'):
        return redirect('/')
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')

    sql = "SELECT * FROM users WHERE username = ? AND password = ?";
    cur = g.db.execute(sql, (username, password))
    user = cur.fetchone()
    if user:
        session['user'] = dict(user)
        session['logged_in'] = True
        return redirect('/todo')

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>', methods=['GET'])
@login_required
def todo(id):
    user_id = session['user']['id']
    cur = g.db.execute("SELECT * FROM todos WHERE id = ? and user_id = ?", (id, user_id))
    todo = cur.fetchone()
    if not todo:
        abort(404)
    return render_template('todo.html', todo=todo)


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
@login_required
def todos():
    user_id = session['user']['id']
    cur = g.db.execute("SELECT * FROM todos WHERE user_id = ?", (user_id,))
    todos = cur.fetchall()
    return render_template('todos.html', todos=todos)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
@login_required
def todos_POST():
    if not request.form.get('description', ''):
        return redirect('/todo')
    g.db.execute(
        "INSERT INTO todos (user_id, description) VALUES (?, ?)",
        (session['user']['id'], request.form.get('description', ''))
    )
    g.db.commit()
    flash('TODO added successfully')
    return redirect('/todo')


@app.route('/todo/<id>', methods=['POST'])
@login_required
def todo_delete(id):
    user_id = session['user']['id']
    g.db.execute("DELETE FROM todos WHERE id = ? and user_id = ?", (id, user_id))
    g.db.commit()
    flash('TODO deleted successfully')
    return redirect('/todo')
	

@app.route('/todo/complete/<id>', methods=['POST'])
@login_required
def todo_complete(id):
    user_id = session['user']['id']
    g.db.execute("UPDATE todos SET completed = 1 WHERE id = ? and user_id = ?", (id, user_id))
    g.db.commit()
    return redirect(request.referrer)

	
@app.route('/todo/reset/<id>', methods=['POST'])
@login_required
def todo_reset(id):
    user_id = session['user']['id']
    g.db.execute("UPDATE todos SET completed = 0 WHERE id = ? and user_id = ?", (id, user_id))
    g.db.commit()
    return redirect(request.referrer)


@app.route('/todo/<id>/json', methods=['GET'])
@login_required
def todo_json(id):
    user_id = session['user']['id']
    cur = g.db.execute("SELECT * FROM todos WHERE id = ? and user_id = ?", (id, user_id))
    todo = cur.fetchone()
    if not todo:
        abort(404)
    return jsonify(dict(todo))
