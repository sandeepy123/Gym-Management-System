from app import create_app, db
from app.models import Member, Plan, Payment, Attendance, Visitor, Enquiry, Expense, Reminder

app = create_app()

with app.app_context():
    print("Clearing database records...")
    
    # Delete dependent child tables first to avoid foreign key constraints
    Attendance.query.delete()
    Payment.query.delete()
    Reminder.query.delete()
    
    # Delete parent tables
    Member.query.delete()
    Plan.query.delete()
    
    # Delete independent tables
    Visitor.query.delete()
    Enquiry.query.delete()
    Expense.query.delete()
    
    db.session.commit()
    
    print("Database cleared successfully! Admin/Staff users and all database structures were kept intact.")
