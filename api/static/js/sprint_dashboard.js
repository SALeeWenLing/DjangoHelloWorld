$(document).ready(function() {

    // Handle date input changes
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');

    if (startDateInput && endDateInput) {
        startDateInput.addEventListener('change', function() {
            const startDate = new Date(this.value);
            const minEndDate = new Date(startDate);
            minEndDate.setDate(minEndDate.getDate() + 1);
            endDateInput.min = minEndDate.toISOString().split('T')[0];
        });
    }

    // Handle status button interactions
    const statusButtons = document.querySelectorAll('.status-btn');
    const rows = $('.clickable-row');

    statusButtons.forEach(button => {
        if (!button.dataset.listenerAdded) {
            button.dataset.listenerAdded = 'true';

            button.addEventListener('mouseover', function() {
                if (button.dataset.status === 'Active') {
                    button.textContent = 'End Sprint';
                } else if (button.dataset.status === 'Inactive') {
                    button.textContent = 'Start Sprint';
                }
            });

            button.addEventListener('mouseout', function() {

                button.textContent = button.dataset.status;
                if (button.dataset.status === 'Inactive') {
                    button.textContent = 'Not Started';
                }
            });

            button.addEventListener('click', function(event) {
                event.stopPropagation(); // Prevent the row click event from firing
                const sprintId = button.dataset.sprintId;
                const currentStatus = button.dataset.status;

                // Prevent changes if the sprint is already completed
                if (currentStatus === 'Completed') {
                    const sprintName = button.closest('tr').querySelector('td:first-child').textContent;
                    showNotification(`${sprintName} has been completed and cannot be modified.`);
                    return;
                }

                // Check if there is already an active sprint
                const activeSprint = document.querySelector('.status-btn[data-status="Active"]');
                if (currentStatus === 'Inactive' && activeSprint) {
                    showNotification('There is currently an ongoing Sprint.<br>Please end it before starting a new one.');
                    return;
                }

                const newStatus = currentStatus === 'Active' ? 'Completed' : 'Active';
                const sprintName = button.closest('tr').querySelector('td:first-child').textContent;

                // Show confirmation modal
                const confirmationMessage = `Are you sure you want to ${newStatus === 'Active' ? 'start' : 'complete'} ${sprintName}?`;
                showConfirmation(confirmationMessage, function() {
                    // Send an AJAX request to update the status
                    fetch(`/update_sprint_status/${sprintId}/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken') // Ensure CSRF token is included
                        },
                        body: JSON.stringify({ status: newStatus, endSprint: newStatus === 'Completed' }),
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Update the button's status and text
                            button.dataset.status = newStatus;
                            button.textContent = newStatus;

                            // Update the button's class to reflect the new status
                            button.classList.remove('btn-success', 'btn-danger');

                            if (newStatus === 'Active') {
                                button.classList.add('btn-success');
                                // button.dataset.activated = 'True';
                                
                                // Change the status of row
                                rows.each(function() {
                                    const row = $(this);
                                    if (row.data('sprint-id') == sprintId) {
                                        row.data('status', 'Active');
                                    }
                                });

                            } else if (newStatus === 'Completed') {
                                button.classList.add('btn-secondary');
                                // Change the status of row
                                rows.each(function() {
                                    const row = $(this);
                                    if (row.data('sprint-id') == sprintId) {
                                        row.data('status', 'Completed');
                                    }
                                });

                                // Send an AJAX to update the sprint name of the task
                                fetch(`/update_sprint_name/${sprintId}/`, {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                        'X-CSRFToken': getCookie('csrftoken') // Ensure CSRF token is included
                                    },
                                    body: JSON.stringify({ name: null }), // Set sprint name to null
                                })
                                .then(response => response.json())
                                .then(data => {
                                    if (!data.success) {
                                        console.error(data.error);
                                    }
                                })
                                .catch(error => {
                                    console.error('Error:', error);
                                });
                            }
                        } else {
                            console.error(data.error);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
                });
            });
        }
    });

    // Handle row click interactions
    rows.each(function() {
        const row = $(this);
        row.on('click', function() {
            const sprintId = row.data('sprint-id');
            const status = row.data('status');
            if (sprintId) {
                let url;
                if (status === "Inactive") {
                    url = `/inactive_sprint/${sprintId}/`;
                } else if (status === "Active") {
                    url = `/active_sprint/${sprintId}/`;
                } else if (status === "Completed") {
                    url = `/completed_sprint/${sprintId}/`;
                }
                if (url) {
                    window.location.href = url;
                } else {
                    console.error("Invalid sprint status");
                }
            } else {
                console.error("Sprint ID is undefined");
            }
        });

        // // Change background color on hover
        // row.on('mouseover', function() {
        //     row.css('background-color', 'red');
        // });

        // row.on('mouseout', function() {
        //     row.css('background-color', '');
        // });
    });
});


// delete an inactive sprint  
function deleteSprint(sprintId, event) {
    event.stopPropagation();

    const sprintRow = document.querySelector(`tr[data-sprint-id="${sprintId}"]`);
    const sprintStatus = sprintRow.dataset.status; 

    if (sprintStatus !== "Inactive") {
        alert('Only inactive sprints can be deleted.');
        return;
    }

    document.getElementById('confirmationMessage').innerText = 'Are you sure you want to delete this inactive sprint?';
    $('#confirmationModal').modal('show');

    document.getElementById('confirmButton').onclick = function() {
        fetch(`/delete_sprint/${sprintId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
        .then(response => {
            if (response.ok) {
                // Remove the sprint row from the table
                document.querySelector(`tr[data-sprint-id="${sprintId}"]`).remove();

                // Move tasks back to product backlog UI (update the DOM if necessary)
                reassignTasksToBacklog(sprintId);
            } else {
                alert('Failed to delete sprint.');
            }
        });

        $('#confirmationModal').modal('hide');
    };
}

// Function to reassign tasks back to the product backlog
function reassignTasksToBacklog(sprintId) {
    // Assuming that each task has a class or data attribute linking it to a sprint
    const tasks = document.querySelectorAll(`.task[data-sprint-id="${sprintId}"]`);
    const backlogContainer = document.getElementById('productBacklogContainer'); // ID of the product backlog container

    tasks.forEach(task => {
        // Update the task's sprint association (remove sprint ID)
        task.dataset.sprintId = null;
        task.querySelector('.task-sprint').innerText = 'None'; // Assuming there's an element showing sprint

        // Move the task element back to the product backlog in the UI
        backlogContainer.appendChild(task);
    });
}




// Function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
