from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Member, Attendance, Payment
from datetime import date, timedelta
from app import db
from sqlalchemy import func

bp = Blueprint('dashboard', __name__)

@bp.route('/')
@login_required
def index():
    today = date.today()
    
    # Total Members
    total_members = Member.query.filter_by(user_id=current_user.id).count()
    
    # 1. Today Renewal (sum of payments with type 'Renewal' or 'New Plan' made today)
    today_renewal_count = Payment.query.filter_by(payment_date=today, user_id=current_user.id).count()
    
    # 2. Monthly Collection
    current_month = today.replace(day=1)
    monthly_payments = Payment.query.filter(Payment.payment_date >= current_month, Payment.user_id == current_user.id).all()
    monthly_collection = sum(p.amount for p in monthly_payments)
    
    # 3. Yearly Collection
    current_year = today.replace(month=1, day=1)
    yearly_payments = Payment.query.filter(Payment.payment_date >= current_year, Payment.user_id == current_user.id).all()
    yearly_collection = sum(p.amount for p in yearly_payments)
    
    # 4. Today Collection
    today_payments = Payment.query.filter_by(payment_date=today, user_id=current_user.id).all()
    today_collection = sum(p.amount for p in today_payments)
    
    # 4. Plan Expired
    expired_members = Member.query.filter(Member.plan_expiry_date < today, Member.user_id == current_user.id).count()
    
    # 5. Plan Expiring Soon (within next 7 days)
    next_week = today + timedelta(days=7)
    expiring_soon_members = Member.query.filter(
        Member.plan_expiry_date >= today,
        Member.plan_expiry_date <= next_week,
        Member.user_id == current_user.id
    ).count()
    
    # 6. Member Attendance Today
    attendance_today = Attendance.query.filter_by(date=today, user_id=current_user.id).count()

    return render_template('dashboard.html',
                           total_members=total_members,
                           today_renewal_count=today_renewal_count,
                           monthly_collection=monthly_collection,
                           yearly_collection=yearly_collection,
                           today_collection=today_collection,
                           expired_members=expired_members,
                           expiring_soon_members=expiring_soon_members,
                           attendance_today=attendance_today)
