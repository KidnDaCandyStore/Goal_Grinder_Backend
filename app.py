from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///goalgrinder.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Event model to manage calendar events
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    location = db.Column(db.String(100))
    date = db.Column(db.String(10))
    start_time = db.Column(db.String(10))
    end_time = db.Column(db.String(10))
    completed = db.Column(db.Boolean)
    completed_on_time = db.Column(db.Boolean)

# Settings model to store user preferences
class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_public = db.Column(db.Boolean, default=True)
    opted_in_ai_services = db.Column(db.Boolean, default=True)
    auto_adjust_schedule = db.Column(db.Boolean, default=True)
    track_my_location = db.Column(db.Boolean, default=False)


# Endpoint to update user settings
@app.route('/update_settings', methods=['POST'])
def update_settings():
    data = request.json
    settings = Settings.query.first() or Settings()
    settings.account_public = data.get('account_public', settings.account_public)
    settings.opted_in_ai_services = data.get('opted_in_ai_services', settings.opted_in_ai_services)
    settings.auto_adjust_schedule = data.get('auto_adjust_schedule', settings.auto_adjust_schedule)
    settings.track_my_location = data.get('track_my_location', settings.track_my_location)
    db.session.add(settings)
    db.session.commit()
    return jsonify({"success": True, "message": "Settings updated"}), 200

# Endpoint to get settings
@app.route('/settings', methods=['GET'])
def get_settings():
    settings = Settings.query.first()
    if not settings:
        return jsonify({"error": "Settings not found"}), 404
    return jsonify({
        "account_public": settings.account_public,
        "opted_in_ai_services": settings.opted_in_ai_services,
        "auto_adjust_schedule": settings.auto_adjust_schedule,
        "track_my_location": settings.track_my_location
    }), 200

# Endpoint to retrieve event by date
@app.route('/events/<date>', methods=['GET'])
def get_event(date):
    event = Event.query.filter_by(date=date).first()
    if event:
        return jsonify({
            "title": event.title,
            "location": event.location,
            "date": event.date,
            "start_time": event.start_time,
            "end_time": event.end_time,
            "completed": event.completed,
            "completed_on_time": event.completed_on_time
        }), 200
    return jsonify({"error": "No event found for the specified date"}), 404

# Endpoint to add a new event
@app.route('/add_event', methods=['POST'])
def add_event():
    data = request.json
    print("Adding new event:", data)  # Confirm addition
    new_event = Event(
        title=data['title'],
        location=data['location'],
        date=data['date'],
        start_time=data['start_time'],
        end_time=data['end_time'],
        completed=data.get('completed', False),
        completed_on_time=data.get('completed_on_time', False)
    )
    db.session.add(new_event)
    db.session.commit()
    print("New event added.")  # Confirm addition
    return jsonify({"success": True, "message": "Event added successfully"}), 201

@app.route('/events_by_month/<int:year>/<int:month>', methods=['GET'])
def get_events_by_month(year, month):
    first_day = datetime(year, month, 1).date()
    last_day = datetime(year, month + 1, 1).date() if month != 12 else datetime(year + 1, 1, 1).date()
    print(f"Querying events from {first_day} to {last_day}")  # Debug print
    events = Event.query.filter(Event.date >= first_day.strftime('%Y-%m-%d'), Event.date < last_day.strftime('%Y-%m-%d')).all()
    print(f"Found {len(events)} events")  # Debug print
    event_dates = [{"date": event.date, "color": "rgb(38, 233, 57)" if event.completed_on_time else "rgb(252, 111, 111)"} for event in events]

    event_dates.sort(key=lambda x: x['date'])
    return jsonify({"success": True, "event_dates": event_dates}), 200


# CREATE DATABASE TABLES: FUNCTION: 
@app.before_first_request
def create_tables():
    db.create_all()  # Create database tables

    # Check if the events table is empty and only then add example events
    if not Event.query.first():
        events = [
            Event(title="Project Kickoff", location="Conference Room A", date="2024-04-05", start_time="09:00 AM", end_time="11:00 AM", completed=False, completed_on_time=False),
            Event(title="Team Meeting", location="Conference Room B", date="2024-04-12", start_time="10:00 AM", end_time="12:00 PM", completed=False, completed_on_time=False),
            Event(title="Client Review", location="Conference Room C", date="2024-04-19", start_time="02:00 PM", end_time="03:00 PM", completed=False, completed_on_time=False),
            Event(title="Product Launch", location="Main Hall", date="2024-04-22", start_time="01:00 PM", end_time="05:00 PM", completed=False, completed_on_time=False),
            Event(title="Quarterly Planning", location="Conference Room D", date="2024-04-29", start_time="09:00 AM", end_time="11:00 AM", completed=False, completed_on_time=False)
        ]

        # Add all events to the database
        db.session.bulk_save_objects(events)
        db.session.commit()  # Commit the changes to the database
        print("Added example events to the database.")  # Confirm addition in the console
        
if __name__ == '__main__':
    app.run(debug=True)