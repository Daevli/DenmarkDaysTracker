from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
import pandas as pd
from datetime import datetime, timedelta, date
import calendar
import json
import io
import os

app = Flask(__name__)
app.secret_key = 'denmark_days_tracker_secret_key'  # Required for session

# Constants
LOOKBACK_PERIOD = 180  # 180 days lookback period
MAX_DAYS_IN_DENMARK = 42  # Maximum 42 days allowed in Denmark

# Initialize session data if not present
def init_session_data():
    if 'days_in_denmark' not in session:
        session['days_in_denmark'] = {}

    # Convert string keys back to datetime objects for processing
    days_data = {}
    for date_str, data in session['days_in_denmark'].items():
        days_data[date_str] = data

    return days_data

# Calculate days in Denmark over the lookback period
def calculate_days_in_denmark(days_data):
    # Define the range of dates to cover the last 365 days and future 365 days
    end_date = date.today() + timedelta(days=365)
    start_date = date.today() - timedelta(days=365)

    # Generate a list of all dates in the range
    all_dates = pd.date_range(start=start_date, end=end_date)

    # Create the DataFrame
    df = pd.DataFrame({'Date': all_dates})

    # Add the InDenmark column
    df['InDenmark'] = df['Date'].apply(
        lambda x: x.strftime('%Y-%m-%d') in days_data
    )

    # Calculate the Accumulated column
    accumulated = []
    for i in range(len(df)):
        # Define the lookback window ending on the current date
        window_start = df.loc[i, 'Date'] - timedelta(days=LOOKBACK_PERIOD-1)
        window_end = df.loc[i, 'Date']

        # Count the number of days in Denmark within the window
        count = df[(df['Date'] >= window_start) & (df['Date'] <= window_end) & df['InDenmark']].shape[0]
        accumulated.append(count)

    df['Accumulated'] = accumulated

    # Add category information
    df['Category'] = df['Date'].apply(
        lambda x: days_data.get(x.strftime('%Y-%m-%d'), {}).get('category', 'none')
    )

    return df

@app.route('/')
def index():
    days_data = init_session_data()
    df = calculate_days_in_denmark(days_data)

    # Prepare calendar data for the template
    calendar_data = prepare_calendar_data(df, days_data)

    # Get current year for active tab
    current_year = datetime.now().year

    return render_template('index.html',
                          calendar_data=calendar_data,
                          max_days=MAX_DAYS_IN_DENMARK,
                          lookback_period=LOOKBACK_PERIOD,
                          current_year=current_year)

def prepare_calendar_data(df, days_data):
    # Extract year and month information
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    df['Weekday'] = df['Date'].dt.weekday  # Monday=0, Sunday=6

    # Get unique years and months
    current_year = datetime.now().year
    years = [current_year - 1, current_year, current_year + 1]

    calendar_data = {}

    for year in years:
        calendar_data[year] = {}

        for month in range(1, 13):
            # Get the days for the month
            month_data = df[(df['Year'] == year) & (df['Month'] == month)]

            # Get the first day of the month and the number of days
            first_day = datetime(year, month, 1).weekday()
            days_in_month = calendar.monthrange(year, month)[1]

            # Prepare month data
            month_days = []
            day_counter = 1

            # Add empty cells for days before the 1st of the month
            for _ in range(first_day):
                month_days.append({
                    'day': '',
                    'in_denmark': False,
                    'accumulated': 0,
                    'category': 'none',
                    'warning': False
                })

            # Add the actual days of the month
            while day_counter <= days_in_month:
                day_date = datetime(year, month, day_counter).date()
                day_str = day_date.strftime('%Y-%m-%d')

                day_data = month_data[month_data['Day'] == day_counter]

                if not day_data.empty:
                    in_denmark = bool(day_data['InDenmark'].values[0])
                    accumulated = int(day_data['Accumulated'].values[0])
                    category = days_data.get(day_str, {}).get('category', 'none')
                    warning = accumulated > MAX_DAYS_IN_DENMARK
                else:
                    in_denmark = False
                    accumulated = 0
                    category = 'none'
                    warning = False

                month_days.append({
                    'day': day_counter,
                    'date': day_str,
                    'in_denmark': in_denmark,
                    'accumulated': accumulated,
                    'category': category,
                    'warning': warning,
                    'past': day_date < date.today()
                })

                day_counter += 1

            calendar_data[year][month] = {
                'name': calendar.month_name[month],
                'days': month_days
            }

    return calendar_data

@app.route('/toggle_day', methods=['POST'])
def toggle_day():
    data = request.get_json()
    day_date = data.get('date')
    category = data.get('category', 'work')  # Default to 'work' if not specified

    days_data = init_session_data()

    if day_date in days_data:
        # If the day is already in Denmark with the same category, remove it
        if days_data[day_date].get('category') == category:
            del days_data[day_date]
        else:
            # Update the category
            days_data[day_date] = {'category': category}
    else:
        # Add the day with the specified category
        days_data[day_date] = {'category': category}

    session['days_in_denmark'] = days_data

    # Recalculate and return updated data
    df = calculate_days_in_denmark(days_data)
    calendar_data = prepare_calendar_data(df, days_data)

    return jsonify({
        'success': True,
        'calendar_data': calendar_data
    })

@app.route('/export_schedule')
def export_schedule():
    days_data = init_session_data()

    # Create a DataFrame from the days data
    export_data = []
    for date_str, data in days_data.items():
        export_data.append({
            'date': date_str,
            'category': data.get('category', 'work')
        })

    df = pd.DataFrame(export_data)

    # Create a CSV in memory
    output = io.StringIO()
    df.to_csv(output, index=False)

    # Create a BytesIO object from the StringIO object
    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)

    return send_file(
        mem,
        as_attachment=True,
        download_name='denmark_schedule.csv',
        mimetype='text/csv'
    )

@app.route('/import_schedule', methods=['POST'])
def import_schedule():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        return redirect(url_for('index'))

    if file and file.filename.endswith('.csv'):
        # Read the CSV file
        df = pd.read_csv(file)

        # Update the session data
        days_data = init_session_data()

        for _, row in df.iterrows():
            date_str = row['date']
            category = row.get('category', 'work')
            days_data[date_str] = {'category': category}

        session['days_in_denmark'] = days_data

    return redirect(url_for('index'))

@app.route('/reset_days', methods=['POST'])
def reset_days():
    # Clear the days_in_denmark session data
    session['days_in_denmark'] = {}

    # Initialize empty data
    days_data = {}

    # Recalculate and return updated data
    df = calculate_days_in_denmark(days_data)
    calendar_data = prepare_calendar_data(df, days_data)

    return jsonify({
        'success': True,
        'calendar_data': calendar_data
    })

if __name__ == '__main__':
    app.run(debug=True)
