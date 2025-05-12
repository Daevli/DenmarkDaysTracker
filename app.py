import pandas as pd
from datetime import date, timedelta
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import calendar

matplotlib.use('TkAgg')

# Function to calculate the accumulated days in Denmark
def calculate_days_in_denmark(datesInDenmark):
    # Convert the input list to a set of datetime objects for fast lookup
    denmark_days = set(pd.to_datetime(datesInDenmark))

    # Define the range of dates to cover the last 365 days and future 365 days
    end_date = date.today() + timedelta(days=365)
    start_date = date.today() - timedelta(days=365)

    # Generate a list of all dates in the range
    all_dates = pd.date_range(start=start_date, end=end_date)

    # Create the DataFrame
    df = pd.DataFrame({'Date': all_dates})

    # Add the InDenmark column
    df['InDenmark'] = df['Date'].isin(denmark_days)

    # Calculate the Accumulated column
    accumulated = []
    for i in range(len(df)):
        # Define the 183-day window ending on the current date
        window_start = df.loc[i, 'Date'] - timedelta(days=182)
        window_end = df.loc[i, 'Date']

        # Count the number of days in Denmark within the window
        count = df[(df['Date'] >= window_start) & (df['Date'] <= window_end) & df['InDenmark']].shape[0]
        accumulated.append(count)

    df['Accumulated'] = accumulated

    return df


def plot_calendar(df):
    # Extract year, month, and day information
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day

    # Get unique years and months
    unique_years = sorted(df['Year'].unique())
    unique_months = sorted(df['Month'].unique())

    # Create a calendar visualization for each year
    for year in unique_years:
        fig, axes = plt.subplots(len(unique_months), 1, figsize=(12, len(unique_months) * 2))
        fig.suptitle(f"Calendar for {year}", fontsize=16)

        if len(unique_months) == 1:
            axes = [axes]  # Ensure axes is always iterable

        for i, month in enumerate(unique_months):
            ax = axes[i]

            # Filter the DataFrame for the current year and month
            month_data = df[(df['Year'] == year) & (df['Month'] == month)]
            days_in_month = calendar.monthrange(year, month)[1]

            # Create an array to hold coloring information
            calendar_days = np.zeros(days_in_month)
            for _, row in month_data.iterrows():
                if row['InDenmark']:
                    calendar_days[row['Day'] - 1] = 1

            # Plot the month data
            ax.imshow(calendar_days.reshape(1, -1), cmap='cool', aspect='auto', extent=[1, days_in_month + 1, 0, 1])
            ax.set_xticks(range(1, days_in_month + 1))
            ax.set_yticks([])
            ax.set_xlim(1, days_in_month + 1)
            ax.set_title(calendar.month_name[month], fontsize=12)
            ax.set_xlabel('Days')

        plt.tight_layout()
        plt.show()


def plot_compact_calendar(df):
    # Extract year, month, and day information
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    df['Weekday'] = df['Date'].dt.weekday  # Monday=0, Sunday=6

    # Get unique years
    unique_years = sorted(df['Year'].unique())

    for year in unique_years:
        # Filter the DataFrame for the current year
        year_data = df[df['Year'] == year]

        # Create a figure for the year
        fig, ax = plt.subplots(4, 3, figsize=(12, 10))
        fig.suptitle(f"Compact Calendar for {year}", fontsize=16)

        for month in range(1, 13):
            # Get the corresponding subplot
            row, col = divmod(month - 1, 3)
            ax_month = ax[row, col]

            # Get the days for the month
            month_data = year_data[year_data['Month'] == month]
            days_in_month = calendar.monthrange(year, month)[1]

            # Create a grid for the month
            month_grid = np.zeros((6, 7))  # 6 rows (max weeks) x 7 columns (days)
            for _, row_data in month_data.iterrows():
                week, weekday = divmod(row_data['Day'] - 1, 7)
                if row_data['InDenmark']:
                    month_grid[week, row_data['Weekday']] = 1

            # Display the grid
            ax_month.imshow(month_grid, cmap="cool", aspect="auto", alpha=0.8)

            # Add day labels
            ax_month.set_xticks(range(7))
            ax_month.set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], fontsize=8)
            ax_month.set_yticks(range(6))
            ax_month.set_yticklabels([f"Week {i + 1}" for i in range(6)], fontsize=8)

            # Add the month title
            ax_month.set_title(calendar.month_name[month], fontsize=12)

            # Hide grid lines and ticks
            ax_month.grid(False)
            ax_month.tick_params(left=False, bottom=False)

        # Adjust layout
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()


# Example input
dates_in_denmark = ['2024-02-18', '2024-02-19', '2024-02-20', '2024-02-21', '2024-02-22', '2024-02-23', '2024-02-24',
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

futureDaysLocked = ['2024-05-18', '2024-05-19', '2024-05-20', '2024-05-21', '2024-05-22', '2024-05-23', '2024-05-24']

trialDays = ['2025-02-09', '2025-02-10', '2025-02-11', '2025-02-12', '2025-02-13', '2025-02-14', '2025-02-15']

# Weeks that are no good
# trialDays = ['2025-01-26', '2025-01-27', '2025-01-28', '2025-01-29', '2025-01-30', '2025-01-31', '2025-02-01']

# Call the function
df_result = calculate_days_in_denmark(dates_in_denmark + futureDaysLocked + trialDays)

badDays = df_result[df_result['Accumulated'] >= 41]

# Display the result
# print(df_result[df_result['Accumulated'] >= 40])
# Call the function
plot_compact_calendar(df_result)
# plot_calendar(df_result)
