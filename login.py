import hashlib
from sqlalchemy import func
from flask_login import login_user, logout_user, current_user

def user_login(username, password, User):
    # hashes the given plain text password and checks if credentials match
    hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()
    search = User.query.filter_by(username=username, password=hashed).first()
    if (search is not None):
        login_user(search)
    return (search is not None)

def create_user(username, password, email, db, User):
    exists = (User.query.filter_by(email=email).first() is not None) or (User.query.filter_by(username=username).first() is not None)

    # checks if the user already exists, denies creation if true.
    if (exists):
        return False
    
    hashed = hashlib.sha256(password.encode('utf-8')).hexdigest() # hashes passwords
    user = User(username=username, password=hashed, email=email, views=0) # creates users
    login_user(user)

    db.session.add(user) # add the user to the database.
    db.session.commit() # write database to file.

    return True

def user_logout():
    logout_user()

def get_user(username, User):
    search = User.query.filter_by(username=username).first()
    return search

def user_exists(username, User):
    return (get_user(username, User) is not None)

def current():
    return current_user