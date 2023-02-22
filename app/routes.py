from app import app, db, login_manager, bcrypt
from flask import render_template, session, redirect, url_for, request, jsonify
import functools
from datetime import datetime

from .models import User, Contest, Group, Subject, contest_subject, Stage, Year
from .forms import LoginForm, CreateUserForm, ContestForm, StageForm

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)

def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)
    return secure_function

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.get(form.username.data)
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                session["username"] = form.username.data
                return redirect("/")
    return render_template("user_login.html", form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = CreateUserForm()
    if form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')
        user = User(username=username, password=bcrypt.generate_password_hash(password).decode('utf-8'))
        db.session.add(user)
        db.session.commit()
        return redirect("/")
    return render_template("user_register.html", form=form)

@app.route("/logout", methods=["GET"])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/')
@login_required
def index():
    groups = Group.query.all()
    group = request.args.get('group')
    if group:
        contests = Contest.query.filter_by(group_id=group).all()
    else:
        contests = Contest.query.all()
    form_stage = StageForm()
    return render_template("contest_view.html", title="Список конкурсных мероприятий",
                           contests=contests, form_stage=form_stage, groups=groups)

# Брейкпойнт страницы добавления записей в БД
@app.route("/add_contest", methods=("POST", "GET"))
@login_required
def add_contest():
    form = ContestForm()
    form.group.choices = [(g.id, g.title) for g in Group.query.all()]
    form.year.choices = [(y.id, y.title) for y in Year.query.all()]
    form.subjects.choices = [(s.id, s.name) for s in Subject.query.all()]
    if request.method == "POST":
        if form.validate_on_submit():
            contest = Contest(title=form.title.data,
                              description=form.description.data,
                              link=form.link.data,
                              level=form.level.data,
                              type=form.type.data,
                              grade=form.grade.data,
                              group_id=form.group.data,
                              year_id=form.year.data)
            contest.subjects = [sb for sb in Subject.query.all() if sb.id in form.subjects.data]
            db.session.add(contest)
            db.session.commit()
        return redirect(url_for('index'))
    return render_template("contest_edit.html", title="Добавление конкурсного мероприятия",
                           btn_submit="Создать", form=form)

# Брейкпойнт страницы редактирования записей в БД
@app.route("/edit_contest/<int:contest_id>", methods=("POST", "GET"))
@login_required
def edit_contest(contest_id):
    contest = Contest.query.get(contest_id)
    form = ContestForm(obj=contest)
    form.group.choices = [(g.id, g.title) for g in Group.query.all()]
    form.year.choices = [(y.id, y.title) for y in Year.query.all()]
    form.subjects.choices = [(s.id, s.name) for s in Subject.query.all()]
    if request.method == "POST":
        if form.validate_on_submit():
            contest.title = form.title.data
            contest.description = form.description.data
            contest.link = form.link.data
            contest.type = form.type.data
            contest.level = form.level.data
            contest.grade = form.grade.data
            contest.group_id = form.group.data
            contest.year_id = form.year.data
            contest.subjects = [sb for sb in Subject.query.all() if sb.id in form.subjects.data and sb.id not in contest.subjects]
            db.session.commit()
        return redirect(url_for('index'))
    else:
        form.group.data = contest.group.id
        form.subjects.data = [sb.id for sb in contest.subjects]
        return render_template("contest_edit.html", title="Редактирование конкурсного мероприятия",
                               btn_submit="Сохранить", form=form)

# Брейкпойнт удаления записи из БД
@app.route("/del_contest/<int:contest_id>", methods=["GET"])
@login_required
def del_contest(contest_id):
    contest = Contest.query.filter_by(id=contest_id)
    db.session.query(contest_subject).filter_by(contest_id=contest_id).delete()
    contest.subjects = []
    contest.delete()
    # добавить удаление связанных stage
    db.session.commit()
    return redirect(url_for('index'))


@app.route("/add_stage/<int:contest_id>", methods=("POST", ))
@login_required
def add_stage(contest_id):
    stage = Stage(title=request.form['title'],
                  link=request.form['link'],
                  deadline=datetime.strptime(request.form['deadline'], '%Y-%m-%d'),
                  contest_id=contest_id)
    db.session.add(stage)
    db.session.commit()
    return jsonify("Success")

@app.route("/edit_stage/<int:stage_id>", methods=("POST", ))
@login_required
def edit_stage(stage_id):
    stage = Stage.query.get(stage_id)
    stage.title = request.form['title']
    stage.link = request.form['link']
    stage.deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d')
    db.session.commit()
    return jsonify("Success")

@app.route("/del_stage/<int:stage_id>", methods=("GET", ))
@login_required
def del_stage(stage_id):
    stage = Stage.query.filter_by(id=stage_id)
    stage.delete()
    db.session.commit()
    return redirect(url_for('index'))