from app import create_app, db
from app.models import User, Plan, Member, Payment

app = create_app()

with app.app_context():
    # Will create app.db since we switched to SQLite
    db.create_all()
    print("Database tables created successfully using SQLite!")
    
    # Create default admin user if not exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        new_admin = User(username='admin', email='admin@gym.com')
        new_admin.set_password('admin123')
        db.session.add(new_admin)
        print("Default admin user created (admin / admin123).")
        
    # Create default plans
    if Plan.query.count() == 0:
        p1 = Plan(name='Monthly Regular', duration_days=30, price=50.00)
        p2 = Plan(name='Quarterly Pro', duration_days=90, price=130.00)
        p3 = Plan(name='Annual VIP', duration_days=365, price=450.00)
        db.session.add_all([p1, p2, p3])
        print("Default plans loaded.")
        
    db.session.commit()
