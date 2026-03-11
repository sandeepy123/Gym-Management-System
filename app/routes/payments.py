from flask import Blueprint, render_template, request, abort
from flask_login import login_required, current_user
from app.models import Payment, Member
from app import db

bp = Blueprint('payments', __name__)

@bp.route('/')
@login_required
def list_payments():
    # Order by payment date descending, then ID descending
    payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.payment_date.desc(), Payment.id.desc()).all()
    return render_template('payments/list.html', payments=payments)

@bp.route('/<int:payment_id>/invoice')
@login_required
def invoice(payment_id):
    payment = Payment.query.filter_by(id=payment_id, user_id=current_user.id).first_or_404()
    # The member is available via the relationship: payment.member
    member = payment.member
    
    # Gym details can be passed to the template or hardcoded in the template
    # For a real application, these might come from a settings model or config
    gym_details = {
        'name': 'GYM PRO',
        'address': 'Shop no.1, Airoli',
        'city': 'Navi Mumbai 400708',
        'phone': '8657644378',
        'email': 'info@gympro.example.com'
    }
    
    return render_template('payments/invoice.html', payment=payment, member=member, gym=gym_details)
