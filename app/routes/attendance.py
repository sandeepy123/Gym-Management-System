from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Member, Attendance
from app import db
from datetime import date, datetime

bp = Blueprint('attendance', __name__)

@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    today = date.today()
    if request.method == 'POST':
        member_id = request.form.get('member_id')
        action = request.form.get('action')
        member = Member.query.filter_by(id=member_id, user_id=current_user.id).first()
        
        if not member:
            flash('Member not found.', 'error')
        else:
            existing = Attendance.query.filter_by(member_id=member_id, date=today, user_id=current_user.id).first()
            if action == 'checkin':
                if existing:
                    flash(f'{member.full_name} is already checked in for today.', 'warning')
                else:
                    att = Attendance(member_id=member_id, date=today, entry_time=datetime.now().time(), user_id=current_user.id)
                    db.session.add(att)
                    db.session.commit()
                    flash(f'Check-in logged for {member.full_name}.', 'success')
            elif action == 'checkout':
                if not existing:
                    flash(f'Cannot check out {member.full_name} because they have not checked in today.', 'error')
                elif existing.exit_time is not None:
                    flash(f'{member.full_name} has already completely checked out today.', 'warning')
                else:
                    existing.exit_time = datetime.now().time()
                    db.session.commit()
                    flash(f'Checkout logged for {member.full_name}.', 'success')
                
        return redirect(url_for('attendance.index'))
        
    # Get today's attendance logs
    today_logs = Attendance.query.filter_by(date=today, user_id=current_user.id).all()
    # For a small gym, passing all members for a dropdown might be okay. 
    # For large gyms, we would use AJAX search. Here we use a dropdown for simplicity.
    all_members = Member.query.filter_by(user_id=current_user.id).all()
    
    return render_template('attendance/mark.html', logs=today_logs, members=all_members, today=today)
