from app import db

contest_subject = db.Table('contest_subject',
                           db.Column('contest_id', db.Integer, db.ForeignKey('contest.id')),
                           db.Column('subject_id', db.Integer, db.ForeignKey('subject.id')))

contest_users = db.Table('contest_users',
                           db.Column('contest_id', db.Integer, db.ForeignKey('contest.id')),
                           db.Column('users_id', db.Integer, db.ForeignKey('user_tg.id')))

class User(db.Model):
    __tablename__ = 'user'
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)
    last_name = db.Column(db.String(64))
    first_name = db.Column(db.String(64))
    authenticated = db.Column(db.Boolean, default=False)
    def get_id(self):
        return self.username
    def is_authenticated(self):
        return self.authenticated

class UserTg(db.Model):
    __tablename__ = 'user_tg'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64))
    username = db.Column(db.String(64))
    grade = db.Column(db.Integer)
    contests = db.relationship('Contest', secondary=contest_users, backref='user')

class Contest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    description = db.Column(db.Text)
    link = db.Column(db.String(128))
    level = db.Column(db.String(1))
    type = db.Column(db.String(32))
    grade = db.Column(db.String(12))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    year_id = db.Column(db.Integer, db.ForeignKey('year.id'))
    stages = db.relationship('Stage', backref='contest', order_by="Stage.deadline")
    subjects = db.relationship('Subject', secondary=contest_subject, backref='contest')

class Stage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    link = db.Column(db.String(128))
    deadline = db.Column(db.Date)
    contest_id = db.Column(db.Integer, db.ForeignKey('contest.id'))

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    code = db.Column(db.String(64))
    contests = db.relationship('Contest', backref='group')

class Year(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32))
    date_start = db.Column(db.Date)
    date_end = db.Column(db.Date)
    contests = db.relationship('Contest', backref='year')

