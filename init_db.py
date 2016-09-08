from app.models import db
from igenwo import create_app

db.create_all(app=create_app())
