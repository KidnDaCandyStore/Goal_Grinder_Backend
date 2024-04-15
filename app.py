from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
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

def create_tables():
    """Create database tables from the models."""
    with app.app_context():
        db.create_all()

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
    return jsonify({"success": True, "message": "Event added successfully"}), 201

@app.route('/events_by_month/<int:year>/<int:month>', methods=['GET'])
def get_events_by_month(year, month):
    try:
        # Find the first and last day of the given month
        first_day = datetime(year, month, 1)
        if month == 12:
            last_day = datetime(year + 1, 1, 1)
        else:
            last_day = datetime(year, month + 1, 1)

        # Query to find events within the specified month
        events = Event.query.filter(Event.date >= first_day.strftime('%Y-%m-%d'), Event.date < last_day.strftime('%Y-%m-%d')).all()

        # Extract just the date part from the events and eliminate duplicates
        event_dates = list(set([event.date for event in events]))

        # Sorting the dates might be helpful for easier readability/consumption
        event_dates.sort()

        # Return the list of dates with events
        return jsonify({
            "success": True,
            "event_dates": event_dates
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

if __name__ == '__main__':
    create_tables()  # Ensure tables are created before running the application
    app.run(debug=True)
