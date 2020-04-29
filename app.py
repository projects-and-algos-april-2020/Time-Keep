from flask import Flask, render_template, redirect, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
import datetime, re
from datetime import date, timedelta




app = Flask(__name__)
DJANGO_NOTIFICATIONS_CONFIG = {
'USE_JSONFIELD': True
}
app.secret_key = "Totally Secrete"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timekeep.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
today = datetime.datetime.now()
wk_end = "4/25/20"


time_stamp = db.Table('stamp',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='cascade'), primary_key=True), 
    db.Column('timecard_id', db.Integer, db.ForeignKey('timecard.id', ondelete='cascade'), primary_key=True))

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(45))
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    employee = db.relationship("User", back_populates="group", cascade="all, delete, delete-orphan")
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    email = db.Column(db.String(45))
    status = db.Column(db.String(45))
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    time_card = db.relationship('Timecard', secondary=time_stamp, passive_deletes=True)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"), nullable=False)
    group = db.relationship('Group', foreign_keys=[group_id])

class Timecard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(45))
    week_end = db.Column(db.String(45))
    day = db.Column(db.String(45))
    reason = db.Column(db.String(45))
    duration = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    employee = db.relationship('User', secondary=time_stamp, passive_deletes=True)

@app.route('/')
def index():
    return render_template("index.html")

# Add
@app.route('/add_group', methods=['POST'])
def add_group():
    print(request.form['gname'])
    
    is_valid = True
    # Group Name
    if len(request.form['gname']) < 1:
    	is_valid = False
    	flash("Please enter a group name")
    elif str.isnumeric(request.form['gname']):
    	is_valid = False
    	flash("Please enter a group name with letters only")
    # Email
    if len(request.form['email']) < 1:
        is_valid = False
        flash("Please enter an email address")
    elif not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Please enter a valid email address")
    else:
        user = Group.query.filter_by(email = request.form['email']).all()
        if user:
            is_valid = False
            flash('Email aready in use')
    
    # Password
    if len(request.form['pword']) < 8:
    	is_valid = False
    	flash("Password should be at least 8 characters")
    elif request.form['passconf'] != request.form['pword']:
        is_valid = False
        flash("Passwords do not match")
    
    if is_valid:
        pw_hash = bcrypt.generate_password_hash(request.form['pword'])
        new_group = Group(name= request.form['gname'], email= request.form['email'], password=pw_hash)
        db.session.add(new_group)
        db.session.commit()
        session['group_id'] = new_group.id
        return redirect ('/group_portal')
    return redirect('/')
@app.route('/add_user', methods=['POST'])
def add_user():
    print(request.form['fname'])
    
    is_valid = True
    # First Name
    if len(request.form['fname']) < 1:
    	is_valid = False
    	flash("Please enter a first name")
    elif not str.isalpha(request.form['fname']):
    	is_valid = False
    	flash("Please enter a first name with letters only")
    # Last Name
    if len(request.form['lname']) < 1:
    	is_valid = False
    	flash("Please enter a last name")
    elif not str.isalpha(request.form['lname']):
    	is_valid = False
    	flash("Please enter a last name with letters only")
    # Email
    if len(request.form['email']) < 1:
    	is_valid = False
    	flash("Please enter an Email")
    elif not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Please enter a valid email address")
    else:
        user = User.query.filter_by(email = request.form['email']).all()
        if user:
            is_valid = False
            flash('Email aready in use')
    # Password
    if len(request.form['pword']) < 8:
    	is_valid = False
    	flash("Password should be at least 8 characters")
    if request.form['passconf'] != request.form['pword']:
        is_valid = False
        flash("Passwords do not match")
    
    if is_valid:
        pw_hash = bcrypt.generate_password_hash(request.form['pword'])
        new_user = User(first_name= request.form['fname'], last_name=request.form['lname'], email= request.form['email'], status= request.form['status'], password=pw_hash, group_id= session['group_id'])
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
    return redirect('/group_portal')

# User Login
@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/user_login', methods=["POST"])
def user_login():
    print(request.form['usr_email'])
    
    is_valid = True
    if len(request.form['usr_email']) < 1:
        is_valid = False
        flash("Email and/or Password not found")
    elif not EMAIL_REGEX.match(request.form['usr_email']):
        is_valid = False
        flash("Email and/or Password not found")
    else:
        user = User.query.filter_by(email = request.form['usr_email']).all()
        if not user:
            is_valid = False
            flash('Email and/or Password not found')

    if len(request.form['pword']) < 8:
    	is_valid = False
    	flash("Email and/or Password not found")
    if is_valid:
        user = User.query.filter_by(email=request.form['usr_email']).first()

        if user:
            if bcrypt.check_password_hash(user.password, request.form['pword']):
                session['user_id'] = user.id
                return redirect('/user_portal')
            else:
                flash("Email and/or Password not found")
        else:
            flash("Email and/or Password not found")
    return redirect('/login')
@app.route('/group_login', methods=["POST"])
def group_login():
    print(request.form['grp_email'])
    is_valid = True

    # Email
    if len(request.form['grp_email']) < 1:
        is_valid = False
        flash("Email and/or Password not found")
    elif not EMAIL_REGEX.match(request.form['grp_email']):
        is_valid = False
        flash("Email and/or Password not found")
    else:
        user = Group.query.filter_by(email = request.form['grp_email']).all()
        if not user:
            is_valid = False
            flash('Email and/or Password not found')
    # Password
    if len(request.form['pword']) < 8:
    	is_valid = False
    	flash("Email and/or Password not found")
    if is_valid:
        print(is_valid)
        user = Group.query.filter_by(email=request.form['grp_email']).first()
        
        if user:
            if bcrypt.check_password_hash(user.password, request.form['pword']):
                session['group_id'] = user.id
                return redirect('/group_portal')
            else:
                flash("Email and/or Password not found")
        else:
            flash("Email and/or Password not found")
    print(is_valid)
    return redirect('/login')

# Logout
@app.route('/logout')
def logout():
    session.pop('user_id')
    session.pop('group_id')
    return redirect('/')

# Portals
@app.route('/portal')
def portal():
    users = User.query.all()
    groups = Group.query.all()
    timecards = Timecard.query.all()
    return render_template("portal.html", users = users, groups=groups, timecards=timecards)
@app.route('/user_portal')
def user_portal():
    if 'user_id' not in session:
        flash("Please Login")
        return redirect('/')
    elif session['user_id'] < 1:
        flash("Please Login")
        return redirect('/')
    this_user = User.query.get(session['user_id'])
    return render_template("user_portal.html", user = this_user, date=today)
@app.route('/group_portal')
def group_portal():
    if 'group_id' not in session:
        return redirect('/')
    elif session['group_id'] < 1:
        flash("Please Login")
        return redirect('/')
    this_group = Group.query.get(session['group_id'])
    
    return render_template("group_portal.html", group = this_group, date=today)

# Timeclock
@app.route('/time_clock')
def time_clock():
    if 'user_id' not in session:
        flash("Please Login")
        return redirect('/')
    elif session['user_id'] < 1:
        flash("Please Login")
        return redirect('/')
    this_user = User.query.get(session['user_id'])
    return render_template("time_clock.html", date = today, user = this_user)
@app.route('/start_time', methods=['POST'])
def start_time():
    if 'user_id' not in session:
        flash("Please Login")
        return redirect('/')
    elif session['user_id'] < 1:
        flash("Please Login")
        return redirect('/')
    print(session['user_id'])
    print(request.form['tname'])
    is_valid = True
    # Task Name
    if len(request.form['tname']) < 1:
    	is_valid = False
    	flash("Please enter a task name")
    # Weekend
    print(request.form['wkend'])
    if not request.form['wkend']:
    	is_valid = False
    	flash("Please enter a week ending date")
    print(request.form['strt'])
    if is_valid:
        new_record = Timecard(task_name=request.form['tname'], week_end= request.form['wkend'], day=today.strftime('%A'), reason=request.form['strt'])
        this_user = User.query.get(session['user_id'])
        this_user.time_card.append(new_record)
        db.session.commit()
        print('You have started your day')
    return redirect("/time_clock")
@app.route('/stop_time', methods=['POST'])
def stop_time():
    if 'user_id' not in session:
        flash("Please Login")
        return redirect('/')
    elif session['user_id'] < 1:
        flash("Please Login")
        return redirect('/')
    print(request.form['tname'])
    is_valid = True
    # Task Name
    if len(request.form['tname']) < 1:
    	is_valid = False
    	flash("Please enter a task name")
    # Weekend
    print(request.form['wkend'])
    if not request.form['wkend']:
    	is_valid = False
    	flash("Please enter a week ending date")
    print(request.form['stp'])
    if is_valid:
        new_record = Timecard(task_name=request.form['tname'], week_end= request.form['wkend'], day=today.strftime('%A'), reason=request.form['stp'])
        this_user = User.query.get(session['user_id'])
        this_user.time_card.append(new_record)
        db.session.commit()
        print('Your time has been submited')
    return redirect("/user_portal")


@app.route('/sick_time', methods=['POST'])
def sick_time():
    if 'user_id' not in session:
        flash("Please Login")
        return redirect('/')
    elif session['user_id'] < 1:
        flash("Please Login")
        return redirect('/')
    
    new_record = Timecard(task_name="sick_time", week_end= wk_end, day=today.strftime('%A'), reason="sick_time")
    this_user = User.query.get(session['user_id'])
    this_user.time_card.append(new_record)
    db.session.commit()
    print('You have started your day')
    flash('You have successfully used 8 Hours of Sick Time')
    return redirect("user_portal")

# Delete/Deactivate
@app.route('/user_delete/<user_id>')
def user_delete(user_id):
    user_instance_to_delete = User.query.get(user_id)
    db.session.delete(user_instance_to_delete)
    db.session.commit()
    session.pop('user_id')
    return redirect('/')
@app.route('/group_delete/<user_id>')
def group_delete(user_id):
    group_instance_to_delete = Group.query.get(user_id)
    db.session.delete(group_instance_to_delete)
    db.session.commit()
    session.pop('group_id')
    return redirect('/portal')
@app.route('/time_delete/<record_id>')
def time_delete(record_id):
    time_instance_to_delete = Timecard.query.get(record_id)
    db.session.delete(time_instance_to_delete)
    db.session.commit()
    # session.pop('user_id')
    return redirect('/portal')

if __name__=="__main__":
    app.run(debug=True)