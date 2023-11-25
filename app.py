# app.py
import os
from flask import (Flask, request, url_for, render_template, redirect, flash , session, send_from_directory)
from flask_login import (AnonymousUserMixin, login_required, current_user)
from flask_sqlalchemy import (SQLAlchemy)
from datetime import datetime
from login import *
from models import *
from fernet import *
from ai import *

# Initializes some global variables
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "db.db") # specifies the path of the db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # disable tracking (uses less memory)
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, "uploads\\") # uploads folder
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB
db = SQLAlchemy(app)
# Gets the models used for the Apps.
User, Course, Assignment, Upload, Submission = init_classes(app, db)

# Uses a context processor to allow information, such as the current username, to be accessed from any template
@app.context_processor
def data():
    logged = not isinstance(current(), AnonymousUserMixin)
    data = {'status': logged, 'username': (current().username if logged else "")}
    return dict(data=data)

# Renders the course.html template
@app.route("/")
def index():
    logged = not isinstance(current(), AnonymousUserMixin)
    courses = (courses_by_user(current().username, User) if logged else [])
    return render_template("courses.html", courses=courses, user=(current().username if logged else ""))

# Provides a list of users and the dates they've signed up.
@app.route("/users")
def list_users():
    l = []
    users = User.query.all()
    for user in users:
        l.append(user)
    return render_template("users.html", users=l)

# Allows the user to enroll into a course.
@app.route("/enroll/", methods=['POST'])
@login_required
def enroll_course():
    id = int(request.form['id'], 36)
    status = add_user_to_course([current().id], id, db, User, Course)
    return redirect(url_for('index'))

# Allows a user to delete the course that they own.
@app.route('/delete_course/<int:course_id>', methods=['POST'])
@login_required
def delete_course(course_id):
    course = Course.query.get(course_id)
    if (course is not None and course.instructor == current()):
        db.session.delete(course)
        db.session.commit()
    return redirect(url_for('index'))

# Get feedback for text files from the GPT-4 model!
@app.route('/course-<string:class_id>/assignment-<string:assignment_id>/get_feedback/<int:file_id>', methods=['POST'])
@login_required
def get_feedback(class_id, assignment_id, file_id):
    f = get_file(file_id, Upload)
    if (f is not None and f.user_id == current().id):
        s = ""
        path = f'{f.filepath}\\{f.filename}'
        decrypt(key, path, f.filename)
        f = open(f.filename, 'r')
        lines = f.readlines()

        for l in lines:
            s += (l + "\n")

        feedback = openai_feedback(s)
    return render_template("feedback.html", feedback=feedback, title="Feedback")


@app.route('/course-<string:class_id>/assignment-<string:assignment_id>/feedback/<int:file_id>', methods=['POST'])
@login_required
def ai_detection(class_id, assignment_id, file_id):
    f = get_file(file_id, Upload)
    if (f is not None and f.user_id == current().id):
        s = ""
        path = f'{f.filepath}\\{f.filename}'
        decrypt(key, path, f.filename)
        f = open(f.filename, 'r')
        lines = f.readlines()

        for l in lines:
            s += (l + "\n")

        detection = openai_detection(s)
    return render_template("feedback.html", feedback=detection, title="AI Detection")
 

# Delete an upload to an assignment.
@app.route('/course-<string:class_id>/assignment-<string:assignment_id>/delete_upload/<int:file_id>', methods=['POST'])
@login_required
def delete_upload(class_id, assignment_id, file_id):
    f = get_file(file_id, Upload)
    if (f is not None and f.user_id == current().id):
        db.session.delete(f)
        db.session.commit()
    return redirect(f'/course-{class_id}/assignment-{assignment_id}') 

# Let's the user create a course.
@app.route("/create", methods=['GET', 'POST'])
@login_required
def create():
    if (request.method == 'POST'):
        user = current()
        F = request.form
        T, D = F['title'], F['desc']
        success, course = create_course(T, D, user.username, db, Course, User)
        if (success):
            return redirect(url_for('index'))

    return render_template("course_creation.html")

# Simple little page that shows how many people have visited their page.
@app.route("/user/<page>")
def home(page):
    user = get_user(page, User)
    if (user is not None):
        user.views += 1
        db.session.commit()
    return render_template("user_page.html", user=user)

# Allows a new user to signup
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if (request.method == 'POST'):
        F = request.form
        U, E, P = F['username'], F['email'], F['password']
        success = create_user(U, P, E, db, User)

        if (success):
            return redirect(url_for('login'))
        else:
            render_template('signup.html', message="Account with username or email already exists!")

    return render_template("signup.html")

# Allows a user to login.
@app.route('/login', methods=['GET', 'POST'])
def login():
    if (request.method == 'POST'):
        F = request.form
        U, P = F['username'], F['password']
        success = user_login(U, P, User)
        if (success):
            session['username'] = U
            session['logged'] = True
            return redirect(url_for('index'))
    return render_template('login.html')

# Logs a user out.
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('index'))

# Allows a user to view the assignments within a course.
@app.route("/course-<string:class_id>")
@login_required
def visit_course(class_id):
    authorized = user_in_course(current().id, class_id, User, Course)
    return render_template("course.html", course=get_course(class_id, Course), authorized=authorized, user=current())

# Allows the user to view a specific assignment.
@app.route("/course-<string:class_id>/assignment-<string:assignment_id>")
@login_required
def view_assignment(class_id, assignment_id):
    c = get_course(class_id, Course)
    a = get_assignment(assignment_id, Assignment)
    return render_template('assignment.html', user=current(), course=c, assignment=a, files=current().uploaded_files, submitted=assignment_submitted(current().id, assignment_id=assignment_id, Submission=Submission))

# Allows the admin to create an assignment
@app.route("/course-<string:class_id>/create_assignment/", methods=['POST'])
@login_required
def create_assignment(class_id):
    F = request.form

    title, desc, weight, start_str, end_str = F['title'], F['description'], F['weight'], F['start'], F['end']

    if (weight == ''):
        weight = 0

    # datetime.strptime("YYYY-MM-DD", "%Y-%m-%d")
    start_time = datetime.strptime(start_str, "%Y-%m-%d")
    end_time = datetime.strptime(end_str, "%Y-%m-%d")

    make_assignment(title, desc, start_time, end_time, weight, class_id, db, Assignment, Course)

    return redirect(f'/course-{class_id}')

# Allows the admin to delete an assignment.
@app.route("/course-<string:class_id>/delete_assignment/<string:assignment_id>", methods=['POST'])
@login_required
def delete_assignment(class_id, assignment_id):
    c = get_course(class_id, Course)
    a = get_assignment(assignment_id, Assignment)
    if (c is not None and c.instructor == current()):
        db.session.delete(a)
        db.session.commit()
    return redirect(f'/course-{class_id}')

# Allows the user to upload content to a assignment.
@app.route("/course-<string:class_id>/assignment-<string:assignment_id>/upload", methods=['GET', 'POST'])
@login_required
def upload(class_id, assignment_id):
    if (request.method == 'POST'):
        file = request.files['file']
        if (file is not None):
            path = os.path.join(app.config['UPLOAD_FOLDER'], f'{class_id}\\{assignment_id}\\{current().username}')
            os.makedirs(path, exist_ok=True)
            filename = f'{path}\\{file.filename}'
            file.save("tmp")
            encrypt(key, "tmp", filename)
            os.remove("tmp")
            create_upload(filename=file.filename, path=path, date=datetime.now(), assignment_id=assignment_id, user_id=current().id, db=db, Upload=Upload)
    print(current().uploaded_files)
    return redirect(f'/course-{class_id}/assignment-{assignment_id}')

@app.route("/course-<string:class_id>/assignment-<string:assignment_id>/submit", methods=['POST'])
@login_required
def submit_assignment(class_id, assignment_id):
    user_id = current().id
    s = create_submission(user_id=user_id, assignment_id=assignment_id, db=db, Submission=Submission)
    return redirect(f'/course-{class_id}/assignment-{assignment_id}')

@app.route("/course-<string:class_id>/assignment-<string:assignment_id>/unsubmit", methods=['POST'])
@login_required
def unsubmit_assignment(class_id, assignment_id):
    user_id = current().id
    s = get_submission(user_id=user_id, assignment_id=assignment_id, Submission=Submission)
    if (s is not None):
        print(s)
        db.session.delete(s)
        db.session.commit()
    return redirect(f'/course-{class_id}/assignment-{assignment_id}')


@app.route("/download/<int:file_id>")
@login_required
def download_file(file_id):
    f = get_file(file_id, Upload)
    if (f is not None and f.user_id == current().id):
        path = f'{f.filepath}\\{f.filename}'
        decrypt(key, path, f.filename)
        return send_from_directory(basedir, f.filename, as_attachment=True)
    return ""

if (__name__ == "__main__"):
    key = load_key("key.tmp")
    with app.app_context():
        db.create_all()
        app.run(debug=True)