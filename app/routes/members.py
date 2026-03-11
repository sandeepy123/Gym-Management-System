from flask import Blueprint, render_template, request, redirect, url_for, flash, render_template_string
from flask_login import login_required, current_user
from app.models import Member, Plan, Payment, Reminder, Attendance
from app import db
from datetime import date, timedelta
import urllib.parse

bp = Blueprint('members', __name__)

@bp.route('/')
@login_required
def list_members():
    filter_type = request.args.get('filter')
    if filter_type == 'expiring_soon':
        today = date.today()
        next_week = today + timedelta(days=7)
        members = Member.query.filter(
            Member.user_id == current_user.id,
            Member.plan_expiry_date >= today,
            Member.plan_expiry_date <= next_week
        ).all()
    else:
        members = Member.query.filter_by(user_id=current_user.id).all()
        
    plans = Plan.query.filter_by(user_id=current_user.id).all()
    return render_template('members/list.html', members=members, plans=plans)

@bp.route('/plans/')
@login_required
def list_plans():
    plans = Plan.query.filter_by(user_id=current_user.id).all()
    return render_template('members/plans_list.html', plans=plans)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_member():
    plans = Plan.query.filter_by(user_id=current_user.id).all()
    if request.method == 'POST':
        full_name = request.form['full_name']
        phone = request.form['phone']
        email = request.form['email']
        plan_id = request.form['plan_id']
        
        selected_plan = Plan.query.filter_by(id=plan_id, user_id=current_user.id).first()
        if not selected_plan:
            flash('Invalid plan selected.', 'error')
            return redirect(url_for('members.add_member'))
            
        join_date = date.today()
        expiry_date = join_date + timedelta(days=selected_plan.duration_days)
        
        member = Member(
            full_name=full_name,
            phone=phone,
            email=email,
            join_date=join_date,
            current_plan_id=plan_id,
            plan_expiry_date=expiry_date,
            user_id=current_user.id
        )
        db.session.add(member)
        db.session.flush() # get member ID
        
        # Log payment
        payment = Payment(
            member_id=member.id,
            amount=selected_plan.price,
            payment_date=join_date,
            type='New Plan',
            user_id=current_user.id
        )
        db.session.add(payment)
        db.session.commit()
        
        flash('Member added successfully!', 'success')
        return redirect(url_for('members.list_members'))
        
    return render_template('members/add.html', plans=plans)

@bp.route('/<int:id>/update_plan', methods=['POST'])
@login_required
def update_plan(id):
    member = Member.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    new_plan_id = request.form['new_plan_id']
    payment_amount = request.form['payment_amount']
    
    new_plan = Plan.query.filter_by(id=new_plan_id, user_id=current_user.id).first()
    if new_plan:
        member.current_plan_id = new_plan.id
        # Extend expiry date from today
        today = date.today()
        # If active, could extend from current expiry, but usually renewals extend from today or expiry
        base_date = member.plan_expiry_date if member.plan_expiry_date and member.plan_expiry_date > today else today
        member.plan_expiry_date = base_date + timedelta(days=new_plan.duration_days)
        
        payment = Payment(
            member_id=member.id,
            amount=float(payment_amount),
            payment_date=today,
            type='Renewal/Upgrade',
            user_id=current_user.id
        )
        db.session.add(payment)
        db.session.commit()
        flash(f'Plan updated for {member.full_name}.', 'success')
    
    return redirect(url_for('members.list_members'))

@bp.route('/plans/add', methods=['GET', 'POST'])
@login_required
def add_plan():
    if request.method == 'POST':
        name = request.form['name']
        duration = request.form['duration_days']
        price = request.form['price']
        
        plan = Plan(name=name, duration_days=int(duration), price=float(price), user_id=current_user.id)
        db.session.add(plan)
        db.session.commit()
        flash('Plan created successfully!', 'success')
        return redirect(url_for('members.list_members'))
    return render_template('members/add_plan.html')

@bp.route('/plans/<int:id>/delete', methods=['POST'])
@login_required
def delete_plan(id):
    plan = Plan.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Check if there are members currently assigned to this plan
    active_members = Member.query.filter_by(current_plan_id=id, user_id=current_user.id).count()
    if active_members > 0:
        flash(f'Cannot delete plan "{plan.name}" because it is currently assigned to {active_members} member(s).', 'error')
    else:
        db.session.delete(plan)
        db.session.commit()
        flash(f'Plan "{plan.name}" deleted successfully!', 'success')
        
    return redirect(url_for('members.list_members'))

@bp.route('/<int:id>/send_reminder', methods=['POST'])
@login_required
def send_reminder(id):
    member = Member.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Log the reminder
    reminder = Reminder(
        member_id=member.id,
        date_sent=date.today(),
        type=member.status,
        user_id=current_user.id
    )
    db.session.add(reminder)
    db.session.commit()
    
    flash(f'Reminder logged for {member.full_name}.', 'success')
    
    # Calculate due days and construct message
    today = date.today()
    if member.plan_expiry_date:
        days_diff = (member.plan_expiry_date - today).days
        if days_diff < 0:
            message = f"Hello {member.full_name}, your gym membership expired {abs(days_diff)} days ago. Please renew your plan to continue."
        else:
            message = f"Hello {member.full_name}, your gym membership is expiring in {days_diff} days. Please renew soon!"
    else:
        message = f"Hello {member.full_name}, please update your gym membership plan."
        
    encoded_message = urllib.parse.quote(message)
    
    # Determine Action URL (Email prioritized over SMS)
    action_url = None
    if member.email and member.phone:
        # Prefer email
        action_url = f"mailto:{member.email}?subject=Gym Membership Reminder&body={encoded_message}"
    elif member.phone:
        action_url = f"sms:{member.phone}?body={encoded_message}"
        
    if action_url:
        # Render a simple script that redirects the user to the action URL then back to the list
        html = f'''
        <!DOCTYPE html>
        <html>
        <head><title>Redirecting...</title></head>
        <body>
            <p>Opening your default app to send the reminder...</p>
            <script>
                // Attempt to open the mailto or sms link
                window.location.href = "{action_url}";
                // Then redirect the current window back to the member list
                setTimeout(function() {{
                    window.location.href = "{url_for('members.list_members')}";
                }}, 500);
            </script>
        </body>
        </html>
        '''
        return render_template_string(html)
        
    return redirect(url_for('members.list_members'))

@bp.route('/<int:id>/attendance')
@login_required
def attendance_history(id):
    member = Member.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    # Get all attendance records for this member, ordered by most recent first
    records = Attendance.query.filter_by(member_id=id, user_id=current_user.id).order_by(Attendance.date.desc(), Attendance.entry_time.desc()).all()
    return render_template('members/attendance_history.html', member=member, records=records)
