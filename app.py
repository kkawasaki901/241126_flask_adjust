from flask import Flask, render_template, request, redirect, url_for
from models import db, User, Event, EventDate, Response
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    events = Event.query.all()
    return render_template('index.html', events=events)

@app.route('/event/<int:event_id>', methods=['GET', 'POST'])
def event(event_id):
    event = Event.query.get_or_404(event_id)
    event_dates = EventDate.query.filter_by(event_id=event_id).all()

    if request.method == 'POST':
        user_name = request.form['name']
        user = User.query.filter_by(name=user_name).first()
        if not user:
            user = User(name=user_name)
            db.session.add(user)
            db.session.commit()

        for date_id, availability in request.form.items():
            if date_id.startswith('date_'):
                date_id = int(date_id.split('_')[1])
                response = Response(
                    event_id=event_id,
                    user_id=user.id,
                    event_date_id=date_id,
                    availability=int(availability)
                )
                db.session.add(response)
        db.session.commit()
        return redirect(url_for('event', event_id=event_id))

    return render_template('event.html', event=event, event_dates=event_dates)

@app.route('/create', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        event_name = request.form['name']
        event = Event(name=event_name)
        db.session.add(event)
        db.session.commit()

        for date in request.form.getlist('dates'):
            event_date = EventDate(event_id=event.id, date=date)
            db.session.add(event_date)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('create.html')
if __name__ == '__main__':
    app.run(debug=True)
