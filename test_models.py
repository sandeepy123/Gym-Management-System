from app import create_app, db
from app.models import Attendance, Plan, Member
from datetime import date, datetime

app = create_app()

with app.app_context():
    # Verify Attendance columns
    print("Attendance columns:")
    for col in Attendance.__table__.columns:
        print(f"- {col.name}: {col.type}")

    print("\nPlan columns:")
    for col in Plan.__table__.columns:
        print(f"- {col.name}: {col.type}")

    print("\nVerified successfully!")
