from functools import wraps
from alayatodo.pagination import Pagination

from alayatodo import app, db
from alayatodo.models import User, Todo
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

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['user'] = user.to_dict()
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
    todo = Todo.query.filter_by(id=id, user_id=session['user']['id']).first()

    if not todo:
        abort(404)
    return render_template('todo.html', todo=todo)


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
@login_required
def todos():
    per_page = request.args.get('per_page', 5, int)
    page = request.args.get('page', 1, int)
	
    user_id = session['user']['id']
    todos = User.query.get(user_id).todos
    pagination = Pagination(page, per_page, todos.count())
	
    if page > pagination.pages and page > 1:
        return redirect('/todo')
	   
    todos = todos.limit(per_page).offset(per_page * (page-1)).all()
    return render_template('todos.html', todos=todos, pagination=pagination)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
@login_required
def todos_POST():
    if not request.form.get('description', ''):
        return redirect('/todo')
	
    description = request.form.get('description', '')
    todo = Todo(user_id=session['user']['id'], description=description, completed=0)
	
    db.session.add(todo)
    db.session.commit()
	
    flash('TODO added successfully')
    return redirect('/todo')


@app.route('/todo/<id>', methods=['POST'])
@login_required
def todo_delete(id):
    todo = Todo.query.filter_by(id=id, user_id=session['user']['id']).first()
	
    if todo:
        db.session.delete(todo)
        db.session.commit()
        flash('TODO deleted successfully')
    
    return redirect('/todo')
	

@app.route('/todo/complete/<id>', methods=['POST'])
@login_required
def todo_complete(id):
    todo = Todo.query.filter_by(id=id, user_id=session['user']['id']).first()
	
    if todo:
        todo.completed = 1
        db.session.commit()

    return redirect(request.referrer)

	
@app.route('/todo/reset/<id>', methods=['POST'])
@login_required
def todo_reset(id):
    todo = Todo.query.filter_by(id=id, user_id=session['user']['id']).first()
	
    if todo:
        todo.completed = 0
        db.session.commit()

    return redirect(request.referrer)


@app.route('/todo/<id>/json', methods=['GET'])
@login_required
def todo_json(id):
    todo = Todo.query.filter_by(id=id, user_id=session['user']['id']).first()

    if not todo:
        return jsonify({'Error': '404', 'Message': 'Todo not found'})
    return jsonify(todo.to_dict())
