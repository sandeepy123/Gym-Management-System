from app import create_app, db
from app.models import User, Member, Plan, Attendance, Payment, Expense, Enquiry, Visitor

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Member': Member, 'Plan': Plan, 
            'Attendance': Attendance, 'Payment': Payment, 
            'Expense': Expense, 'Enquiry': Enquiry, 'Visitor': Visitor}

if __name__ == '__main__':
    app.run(debug=True)
