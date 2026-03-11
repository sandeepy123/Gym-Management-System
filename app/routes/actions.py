from flask import Blueprint, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Visitor, Enquiry, Expense, Plan
from app import db
from datetime import date

bp = Blueprint('actions', __name__)


@bp.route('/visitor', methods=['POST'])
@login_required
def log_visitor():
    name = request.form.get('name')
    phone = request.form.get('phone')
    visitor = Visitor(name=name, phone=phone, user_id=current_user.id)
    db.session.add(visitor)
    db.session.commit()
    flash('Visitor logged successfully.', 'success')
    return redirect(request.referrer or url_for('dashboard.index'))


@bp.route('/enquiry', methods=['POST'])
@login_required
def log_enquiry():
    name = request.form.get('name')
    phone = request.form.get('phone')
    notes = request.form.get('notes')
    enquiry = Enquiry(name=name, phone=phone, notes=notes, user_id=current_user.id)
    db.session.add(enquiry)
    db.session.commit()
    flash('Enquiry saved.', 'success')
    return redirect(request.referrer or url_for('dashboard.index'))


@bp.route('/expense', methods=['POST'])
@login_required
def log_expense():
    description = request.form.get('description')
    amount = request.form.get('amount')
    expense = Expense(description=description, amount=float(amount), date=date.today(), user_id=current_user.id)
    db.session.add(expense)
    db.session.commit()
    flash(f'Expense of ₹{amount} logged.', 'success')
    return redirect(request.referrer or url_for('dashboard.index'))


@bp.route('/notify', methods=['POST'])
@login_required
def send_notification():
    # Placeholder for actual mail/SMS logic
    flash('Notifications sent to appropriate members.', 'success')
    return redirect(request.referrer or url_for('dashboard.index'))


# DELETE PLAN
@bp.route("/delete_plan/<int:id>")
@login_required
def delete_plan(id):
    plan = Plan.query.filter_by(id=id, user_id=current_user.id).first()
    if plan:
        db.session.delete(plan)
        db.session.commit()
        flash("Plan deleted successfully.", "success")
    else:
        flash("Plan not found.", "danger")

    return redirect(url_for("dashboard.index"))