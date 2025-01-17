import tkinter as tk
from datetime import datetime, timedelta
import calendar


class DenmarkStayTrackerGUI:
    def __init__(self, master, initial_dates=None):
        self.master = master
        self.master.title("Denmark Stay Tracker")
        self.frame = tk.Frame(self.master)
        self.frame.pack(padx=10, pady=10)

        # Initialize data
        self.dates_in_denmark = set(
            datetime.strptime(date, "%Y-%m-%d").date() for date in initial_dates or []
        )
        self.lookback_period = 91
        self.max_days_in_denmark = 41

        # Multi-Year Display
        self.start_year = datetime.today().year - 1
        self.end_year = datetime.today().year

        # Create the calendar
        self.create_calendar()

    def create_calendar(self):
        """Creates a multi-year calendar grid."""
        # Clear existing widgets
        for widget in self.frame.winfo_children():
            widget.destroy()

        # Display all months for last year, this year, and next year
        row = 0
        col = 0
        for year in range(self.start_year, self.end_year + 1):
            for month in range(1, 13):
                self.create_month(row, col, year, month)
                col += 1
                if col > 5:  # 6 columns (Jan, Feb, Mar in a row)
                    col = 0
                    row += 1

    def create_month(self, row, col, year, month):
        """Displays a single month's calendar in the specified grid position."""
        month_frame = tk.Frame(self.frame, relief="ridge", borderwidth=1)
        month_frame.grid(row=row, column=col, padx=5, pady=5)

        # Month and year title
        tk.Label(
            month_frame,
            text=f"{calendar.month_name[month]} {year}",
            font=("Helvetica", 10, "bold"),
        ).grid(row=0, column=0, columnspan=7)

        # Weekday headers
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for col_idx, day in enumerate(days):
            tk.Label(month_frame, text=day, font=("Helvetica", 8)).grid(row=1, column=col_idx)

        # Days in the month
        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.monthdatescalendar(year, month)
        for row_idx, week in enumerate(month_days, start=2):
            for col_idx, day in enumerate(week):
                if day.month == month:
                    button_color = self.get_day_color(day)
                    day_button = tk.Button(
                        month_frame,
                        text=str(day.day),
                        bg=button_color,
                        command=lambda d=day: self.toggle_date(d),
                        width=2,
                    )
                    day_button.grid(row=row_idx, column=col_idx, padx=1, pady=1)

    def toggle_date(self, date):
        """Toggles a date in the Denmark stay tracker."""
        if date in self.dates_in_denmark:
            self.dates_in_denmark.remove(date)
        else:
            self.dates_in_denmark.add(date)

        self.create_calendar()

    def get_day_color(self, date):
        """Determines the color of a date based on constraints."""
        cutoff_date_start = date - timedelta(days=self.lookback_period)
        cutoff_date_end = date + timedelta(days=self.lookback_period)
        overlapping_dates = [
            d for d in self.dates_in_denmark if cutoff_date_start <= d <= cutoff_date_end
        ]

        if date < datetime.today().date():
            if date in self.dates_in_denmark:
                return "darkgray"  # Blue for violating dates that are selected
            else:
                return "lightgray"  # Lighter red for violating dates that are not selected

        if len(overlapping_dates) > self.max_days_in_denmark:
            if date in self.dates_in_denmark:
                return "blue"  # Blue for violating dates that are selected
            else:
                return "salmon"  # Lighter red for violating dates that are not selected
        elif date in self.dates_in_denmark:
            return "limegreen"  # Green for selected dates within limits
        else:
            return "white"  # White for unselected dates


if __name__ == "__main__":
    # Days in the past that cannot be changed (Can be in the app, but shouldn't be)
    pastDates = ['2024-02-18', '2024-02-19', '2024-02-20', '2024-02-21', '2024-02-22', '2024-02-23', '2024-02-24',
                 '2024-04-14', '2024-04-15', '2024-04-16', '2024-04-17', '2024-04-18', '2024-04-19', '2024-04-20',
                 '2024-05-04',
                 '2024-05-08', '2024-05-09', '2024-05-10', '2024-05-11', '2024-05-12',
                 '2024-06-02', '2024-06-03', '2024-06-04', '2024-06-05', '2024-06-06', '2024-06-07', '2024-06-08',
                 '2024-08-09', '2024-08-10', '2024-08-11', '2024-08-12', '2024-08-13', '2024-08-14', '2024-08-15',
                  '2024-08-16', '2024-08-17', '2024-08-18', '2024-08-19', '2024-08-20', '2024-08-21', '2024-08-22',
                  '2024-08-23', '2024-08-24', '2024-08-25', '2024-08-26',
                 '2024-11-03', '2024-11-04', '2024-11-05', '2024-11-06', '2024-11-07', '2024-11-08', '2024-11-09',
                 '2024-12-15', '2024-12-16', '2024-12-17', '2024-12-18', '2024-12-19', '2024-12-20', '2024-12-21',
                  '2024-12-22', '2024-12-23', '2024-12-24', '2024-12-25', '2024-12-26', '2024-12-27', '2024-12-28',
                  '2024-12-29'
                ]

    # Obligatory days
    futureDaysLocked = ['2025-05-18', '2025-05-19', '2025-05-20', '2025-05-21', '2025-05-22', '2025-05-23', '2025-05-24']

    # Days to check if they break the 42 day constraint (with a 1 day buffer)
    # See at the bottom of the script for whole weeks from sunday to saturday
    trialDays = (
            ['2025-02-16', '2025-02-17', '2025-02-18', '2025-02-19', '2025-02-20', '2025-02-21', '2025-02-22'] +
            ['2025-03-30', '2025-03-31', '2025-04-01', '2025-04-02', '2025-04-03', '2025-04-04', '2025-04-05'] +
            ['2025-06-29', '2025-06-30', '2025-07-01', '2025-07-02', '2025-07-03', '2025-07-04', '2025-07-05']
        )

    initialDates = pastDates + futureDaysLocked + trialDays

    root = tk.Tk()
    app = DenmarkStayTrackerGUI(root, initial_dates=initialDates)
    root.mainloop()


    """
    dates_2025 = pd.date_range(start='2025-01-05', end='2025-12-28')

    # Create lists for each week of the year
    weeks_2025 = []
    current_week = []

    for date in dates_2025:
        current_week.append(date.strftime('%Y-%m-%d'))
        if len(current_week) == 7:
            weeks_2025.append(current_week)
            current_week = []
    
    2025 weeks, just to make it easier to copy/paste
    
    ['2025-01-05', '2025-01-06', '2025-01-07', '2025-01-08', '2025-01-09', '2025-01-10', '2025-01-11']
    ['2025-01-12', '2025-01-13', '2025-01-14', '2025-01-15', '2025-01-16', '2025-01-17', '2025-01-18']
    ['2025-01-19', '2025-01-20', '2025-01-21', '2025-01-22', '2025-01-23', '2025-01-24', '2025-01-25']
    ['2025-01-26', '2025-01-27', '2025-01-28', '2025-01-29', '2025-01-30', '2025-01-31', '2025-02-01']
    ['2025-02-02', '2025-02-03', '2025-02-04', '2025-02-05', '2025-02-06', '2025-02-07', '2025-02-08']
    ['2025-02-09', '2025-02-10', '2025-02-11', '2025-02-12', '2025-02-13', '2025-02-14', '2025-02-15']
    ['2025-02-16', '2025-02-17', '2025-02-18', '2025-02-19', '2025-02-20', '2025-02-21', '2025-02-22']
    ['2025-02-23', '2025-02-24', '2025-02-25', '2025-02-26', '2025-02-27', '2025-02-28', '2025-03-01']
    ['2025-03-02', '2025-03-03', '2025-03-04', '2025-03-05', '2025-03-06', '2025-03-07', '2025-03-08']
    ['2025-03-09', '2025-03-10', '2025-03-11', '2025-03-12', '2025-03-13', '2025-03-14', '2025-03-15']
    ['2025-03-16', '2025-03-17', '2025-03-18', '2025-03-19', '2025-03-20', '2025-03-21', '2025-03-22']
    ['2025-03-23', '2025-03-24', '2025-03-25', '2025-03-26', '2025-03-27', '2025-03-28', '2025-03-29']
    ['2025-03-30', '2025-03-31', '2025-04-01', '2025-04-02', '2025-04-03', '2025-04-04', '2025-04-05']
    ['2025-04-06', '2025-04-07', '2025-04-08', '2025-04-09', '2025-04-10', '2025-04-11', '2025-04-12']
    ['2025-04-13', '2025-04-14', '2025-04-15', '2025-04-16', '2025-04-17', '2025-04-18', '2025-04-19']
    ['2025-04-20', '2025-04-21', '2025-04-22', '2025-04-23', '2025-04-24', '2025-04-25', '2025-04-26']
    ['2025-04-27', '2025-04-28', '2025-04-29', '2025-04-30', '2025-05-01', '2025-05-02', '2025-05-03']
    ['2025-05-04', '2025-05-05', '2025-05-06', '2025-05-07', '2025-05-08', '2025-05-09', '2025-05-10']
    ['2025-05-11', '2025-05-12', '2025-05-13', '2025-05-14', '2025-05-15', '2025-05-16', '2025-05-17']
    ['2025-05-18', '2025-05-19', '2025-05-20', '2025-05-21', '2025-05-22', '2025-05-23', '2025-05-24']
    ['2025-05-25', '2025-05-26', '2025-05-27', '2025-05-28', '2025-05-29', '2025-05-30', '2025-05-31']
    ['2025-06-01', '2025-06-02', '2025-06-03', '2025-06-04', '2025-06-05', '2025-06-06', '2025-06-07']
    ['2025-06-08', '2025-06-09', '2025-06-10', '2025-06-11', '2025-06-12', '2025-06-13', '2025-06-14']
    ['2025-06-15', '2025-06-16', '2025-06-17', '2025-06-18', '2025-06-19', '2025-06-20', '2025-06-21']
    ['2025-06-22', '2025-06-23', '2025-06-24', '2025-06-25', '2025-06-26', '2025-06-27', '2025-06-28']
    ['2025-06-29', '2025-06-30', '2025-07-01', '2025-07-02', '2025-07-03', '2025-07-04', '2025-07-05']
    ['2025-07-06', '2025-07-07', '2025-07-08', '2025-07-09', '2025-07-10', '2025-07-11', '2025-07-12']
    ['2025-07-13', '2025-07-14', '2025-07-15', '2025-07-16', '2025-07-17', '2025-07-18', '2025-07-19']
    ['2025-07-20', '2025-07-21', '2025-07-22', '2025-07-23', '2025-07-24', '2025-07-25', '2025-07-26']
    ['2025-07-27', '2025-07-28', '2025-07-29', '2025-07-30', '2025-07-31', '2025-08-01', '2025-08-02']
    ['2025-08-03', '2025-08-04', '2025-08-05', '2025-08-06', '2025-08-07', '2025-08-08', '2025-08-09']
    ['2025-08-10', '2025-08-11', '2025-08-12', '2025-08-13', '2025-08-14', '2025-08-15', '2025-08-16']
    ['2025-08-17', '2025-08-18', '2025-08-19', '2025-08-20', '2025-08-21', '2025-08-22', '2025-08-23']
    ['2025-08-24', '2025-08-25', '2025-08-26', '2025-08-27', '2025-08-28', '2025-08-29', '2025-08-30']
    ['2025-08-31', '2025-09-01', '2025-09-02', '2025-09-03', '2025-09-04', '2025-09-05', '2025-09-06']
    ['2025-09-07', '2025-09-08', '2025-09-09', '2025-09-10', '2025-09-11', '2025-09-12', '2025-09-13']
    ['2025-09-14', '2025-09-15', '2025-09-16', '2025-09-17', '2025-09-18', '2025-09-19', '2025-09-20']
    ['2025-09-21', '2025-09-22', '2025-09-23', '2025-09-24', '2025-09-25', '2025-09-26', '2025-09-27']
    ['2025-09-28', '2025-09-29', '2025-09-30', '2025-10-01', '2025-10-02', '2025-10-03', '2025-10-04']
    ['2025-10-05', '2025-10-06', '2025-10-07', '2025-10-08', '2025-10-09', '2025-10-10', '2025-10-11']
    ['2025-10-12', '2025-10-13', '2025-10-14', '2025-10-15', '2025-10-16', '2025-10-17', '2025-10-18']
    ['2025-10-19', '2025-10-20', '2025-10-21', '2025-10-22', '2025-10-23', '2025-10-24', '2025-10-25']
    ['2025-10-26', '2025-10-27', '2025-10-28', '2025-10-29', '2025-10-30', '2025-10-31', '2025-11-01']
    ['2025-11-02', '2025-11-03', '2025-11-04', '2025-11-05', '2025-11-06', '2025-11-07', '2025-11-08']
    ['2025-11-09', '2025-11-10', '2025-11-11', '2025-11-12', '2025-11-13', '2025-11-14', '2025-11-15']
    ['2025-11-16', '2025-11-17', '2025-11-18', '2025-11-19', '2025-11-20', '2025-11-21', '2025-11-22']
    ['2025-11-23', '2025-11-24', '2025-11-25', '2025-11-26', '2025-11-27', '2025-11-28', '2025-11-29']
    ['2025-11-30', '2025-12-01', '2025-12-02', '2025-12-03', '2025-12-04', '2025-12-05', '2025-12-06']
    ['2025-12-07', '2025-12-08', '2025-12-09', '2025-12-10', '2025-12-11', '2025-12-12', '2025-12-13']
    ['2025-12-14', '2025-12-15', '2025-12-16', '2025-12-17', '2025-12-18', '2025-12-19', '2025-12-20']
    ['2025-12-21', '2025-12-22', '2025-12-23', '2025-12-24', '2025-12-25', '2025-12-26', '2025-12-27']
    
    
    """
