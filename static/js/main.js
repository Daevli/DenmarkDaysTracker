// Main JavaScript for Denmark Days Tracker

document.addEventListener('DOMContentLoaded', function() {
    // Variables to track the currently selected category
    let selectedCategory = 'work'; // Default category

    // Set up category button handlers
    const categoryButtons = document.querySelectorAll('.btn-group [data-category]');
    categoryButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            categoryButtons.forEach(btn => btn.classList.remove('active'));

            // Add active class to clicked button
            this.classList.add('active');

            // Update selected category
            selectedCategory = this.getAttribute('data-category');
        });
    });

    // Set up calendar day click handlers
    const calendarCells = document.querySelectorAll('.calendar-table td[data-date]');
    calendarCells.forEach(cell => {
        cell.addEventListener('click', function() {
            const date = this.getAttribute('data-date');
            toggleDay(date, selectedCategory);
        });
    });

    // Set up reset button handler
    const resetButton = document.getElementById('resetDaysButton');
    if (resetButton) {
        resetButton.addEventListener('click', function() {
            if (confirm('Are you sure you want to reset all days? This action cannot be undone.')) {
                resetAllDays();
            }
        });
    }

    // Function to toggle a day's status via AJAX
    function toggleDay(date, category) {
        fetch('/toggle_day', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                date: date,
                category: category
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateCalendar(data.calendar_data);
            }
        })
        .catch(error => {
            console.error('Error toggling day:', error);
        });
    }

    // Function to reset all days via AJAX
    function resetAllDays() {
        fetch('/reset_days', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateCalendar(data.calendar_data);
            }
        })
        .catch(error => {
            console.error('Error resetting days:', error);
        });
    }

    // Function to update the calendar display with new data
    function updateCalendar(calendarData) {
        // For each year in the calendar data
        for (const [year, months] of Object.entries(calendarData)) {
            // For each month in the year
            for (const [monthNum, monthData] of Object.entries(months)) {
                const days = monthData.days;

                // Find the corresponding month in the DOM
                const monthElement = document.querySelector(`#year-${year} div[data-month="${monthNum}"]`);
                if (!monthElement) continue;

                // Update each day cell
                days.forEach((day, index) => {
                    if (!day.day) return; // Skip empty cells

                    // Find the corresponding day cell
                    const dayCells = monthElement.querySelectorAll('td[data-date]');
                    const dayCell = Array.from(dayCells).find(cell => cell.getAttribute('data-date') === day.date);

                    if (dayCell) {
                        // Update cell attributes
                        dayCell.setAttribute('data-in-denmark', day.in_denmark.toString());
                        dayCell.setAttribute('data-accumulated', day.accumulated);
                        dayCell.setAttribute('data-category', day.category);

                        // Update cell classes based on status
                        dayCell.className = ''; // Reset classes

                        if (day.in_denmark) {
                            if (day.category === 'work') dayCell.classList.add('bg-success', 'text-white');
                            if (day.category === 'holiday') dayCell.classList.add('bg-info', 'text-white');
                            if (day.category === 'other') dayCell.classList.add('bg-warning');
                            if (day.warning) dayCell.classList.add('border', 'border-danger', 'border-3');
                        }

                        if (day.past) dayCell.classList.add('bg-opacity-50');

                        // Update the day cell content
                        const dayContent = `
                            <div class="day-cell" title="Days in Denmark: ${day.accumulated}">
                                ${day.day}
                                ${day.in_denmark ? `<span class="badge rounded-pill bg-light text-dark">${day.accumulated}</span>` : ''}
                            </div>
                        `;
                        dayCell.innerHTML = dayContent;
                    }
                });
            }
        }
    }
});
