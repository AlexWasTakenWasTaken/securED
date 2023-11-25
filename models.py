# models.py
from numpy import base_repr
from login import *
from sqlalchemy import func
from flask_login import LoginManager, UserMixin
from datetime import datetime

def init_classes(app, db):
    course_participants = db.Table('course_participants',
                                   db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
                                   db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True))

    class User(UserMixin, db.Model):
        __tablename__ = "users"
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String, nullable=False)
        password = db.Column(db.String, nullable=False)
        email = db.Column(db.String, nullable=False)
        date = db.Column(db.DateTime(timezone=True), server_default = func.now())
        views = db.Column(db.Integer)
        enrolled = db.relationship('Course', secondary=course_participants, lazy='subquery', backref=db.backref('participants', lazy=True))

        login_manager = LoginManager()
        login_manager.init_app(app)

        def __repr__(self):
            return f'<User {self.username}>'

        def __str__(self):
            return f'{self.username}'
        
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.filter_by(id=user_id).first()

    class Assignments(db.Model):
        __tablename__ = "assignments"
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String, nullable=False)
        description = db.Column(db.String, nullable=False)
        weight = db.Column(db.Integer)
        release_date = db.Column(db.DateTime)
        due_date = db.Column(db.DateTime)
        course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

        def __repr__(self):
            return f'<Assignment: {self.title}>'

    class Course(db.Model):
        __tablename__ = "courses"
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String, nullable=False)
        desc = db.Column(db.String, nullable=True)
        class_id = db.Column(db.String)
        members = db.Column(db.Integer)
        created_at = db.Column(db.DateTime(timezone=True), server_default = func.now())
        instructor = db.relationship('User', backref=db.backref('admin_courses', lazy=True))
        instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
        assignments = db.relationship('Assignments', backref='course', lazy=True)

        def __repr__(self):
            return f'<Course: {self.title}>'

    class Upload(db.Model):
        __tablename__ = "uploads"
        id = db.Column(db.Integer, primary_key=True)
        filename = db.Column(db.String, nullable=False)
        filepath = db.Column(db.String, nullable=False)
        upload_date = db.Column(db.DateTime)
        assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

        user = db.relationship('User', backref=db.backref('uploaded_files', lazy=True))
        assignment = db.relationship('Assignments', backref=db.backref('uploaded_files', lazy=True))

        def __repr__(self):
            return f'<Upload: {self.filename}>'

    class Submission(db.Model):
        __tablename__ = "submissions"
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
        timestamp = db.Column(db.DateTime, default=datetime.utcnow)
        user = db.relationship('User', backref=db.backref('submissions'))
        assignment = db.relationship('Assignments', backref=db.backref('submissions'))

    return User, Course, Assignments, Upload, Submission

def get_course(class_id, Course):
    id = int(class_id, 36)
    c = Course.query.filter_by(id=id).first()
    return c

# Course Model
def create_course(title, desc, username, db, Course, User):
    instructor = get_user(username, User)

    if (instructor is None):
        return False, None

    c = Course(title=title, desc=desc, instructor_id=instructor.id)

    db.session.add(c)
    db.session.commit()

    # hashing necessary or not?
    # adler32 dupes: 424/1000 unique hashes
    c.class_id = base_repr(c.id, 36).rjust(6, '0') # pads to length of 6

    db.session.commit()

    return True, c

def user_in_course(user_id, course_id, User, Course):
    id = int(course_id, 36)
    user = User.query.filter_by(id=user_id).first()
    course = Course.query.filter_by(id=id).first()
    if (user is None) or (course is None):
        return False
    return ((user in course.participants) or (user == course.instructor))
    
def courses_by_user(username, User):
    user = User.query.filter_by(username=username).first()
    if (user is not None):
        return (user.enrolled + user.admin_courses)
    return None

def add_user_to_course(user_ids, course_id, db, User, Course):
    course = Course.query.filter_by(id=course_id).first()
    if (course is None):
        return False

    for user_id in user_ids:
        user = User.query.filter_by(id=user_id).first()
        if (user is None):
            return False
        if (user not in course.participants and user != course.instructor):
            user.enrolled.append(course)

    db.session.commit()

    return True

def make_assignment(title, description, release_date, due_date, weight, class_id, db, Assignment, Course):
    c = get_course(class_id, Course)

    if (c is None):
        return False
    
    a = Assignment(title=title, description=description, release_date=release_date, due_date=due_date, weight=weight, course_id=c.id)

    c.assignments.append(a)

    db.session.commit()

    return a

def get_assignments(class_id, Course):
    id = int(class_id, 36)
    course = Course.query.filter_by(id=id).first()
    if (course is None):
        return []
    return course.assignments

def get_assignment(assignment_id, Assignment):
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    return assignment

def create_upload(filename, path, date, assignment_id, user_id, db, Upload):
    upload = Upload(filename=filename, filepath=path, upload_date=date, assignment_id=assignment_id, user_id=user_id)

    db.session.add(upload)
    db.session.commit()

    return upload

def get_file(file_id, Upload):
    f = Upload.query.filter_by(id=file_id).first()
    return f

def create_submission(user_id, assignment_id, db, Submission):
    s = Submission(user_id=user_id, assignment_id=assignment_id, timestamp=datetime.now())
    db.session.add(s)
    db.session.commit()
    return s

def assignment_submitted(user_id, assignment_id, Submission):
    s = Submission.query.filter_by(user_id=user_id, assignment_id=assignment_id).first()
    return (s is not None)

def get_submission(user_id, assignment_id, Submission):
    s = Submission.query.filter_by(user_id=user_id, assignment_id=assignment_id).first()
    return s