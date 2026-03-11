from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login
from datetime import datetime, date, timedelta

class User(UserMixin, db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Relationships for User Data Isolation
    plans = db.relationship('Plan', backref='owner', lazy='dynamic')
    members = db.relationship('Member', backref='owner', lazy='dynamic')
    attendances = db.relationship('Attendance', backref='owner', lazy='dynamic')
    payments = db.relationship('Payment', backref='owner', lazy='dynamic')
    expenses = db.relationship('Expense', backref='owner', lazy='dynamic')
    enquiries = db.relationship('Enquiry', backref='owner', lazy='dynamic')
    visitors = db.relationship('Visitor', backref='owner', lazy='dynamic')
    reminders = db.relationship('Reminder', backref='owner', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Plan(db.Model):
    __tablename__ = 'plan'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    members = db.relationship('Member', backref='plan', lazy=True)

class Member(db.Model):
    __tablename__ = 'member'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(120))
    join_date = db.Column(db.Date, default=date.today)
    current_plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'))
    plan_expiry_date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    
    attendances = db.relationship('Attendance', backref='member', lazy='dynamic')
    payments = db.relationship('Payment', backref='member', lazy='dynamic')
    reminders = db.relationship('Reminder', backref='member', lazy='dynamic', order_by='desc(Reminder.date_sent)')

    @property
    def status(self):
        if not self.plan_expiry_date:
            return "No Plan"
        today = date.today()
        if self.plan_expiry_date < today:
            return "Plan Expired"
        elif today <= self.plan_expiry_date <= today + timedelta(days=7):
            return "Plan Expiring Soon"
        return "Active"

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    date = db.Column(db.Date, default=date.today, nullable=False)
    entry_time = db.Column(db.Time, default=lambda: datetime.now().time(), nullable=False)
    exit_time = db.Column(db.Time, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('staff.id'))

class Payment(db.Model):
    __tablename__ = 'payment'
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.Date, default=date.today, nullable=False)
    type = db.Column(db.String(64), nullable=False) # e.g., 'New Plan', 'Upgrade'
    user_id = db.Column(db.Integer, db.ForeignKey('staff.id'))

class Expense(db.Model):
    __tablename__ = 'expense'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, default=date.today, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('staff.id'))

class Enquiry(db.Model):
    __tablename__ = 'enquiry'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(32), nullable=False)
    notes = db.Column(db.Text)
    enquiry_date = db.Column(db.Date, default=date.today, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('staff.id'))

class Visitor(db.Model):
    __tablename__ = 'visitor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(32), nullable=False)
    visit_date = db.Column(db.Date, default=date.today, nullable=False)
    entry_time = db.Column(db.Time, default=lambda: datetime.now().time(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('staff.id'))

class Reminder(db.Model):
    __tablename__ = 'reminder'
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    date_sent = db.Column(db.Date, default=date.today, nullable=False)
    type = db.Column(db.String(64), nullable=False) # e.g., 'Expiring Soon', 'Expired'
    user_id = db.Column(db.Integer, db.ForeignKey('staff.id'))

