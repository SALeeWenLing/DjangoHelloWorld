
function deleteTask(taskId) {
    // Set the confirmation message
    document.getElementById('confirmationMessage').innerText = 'Are you sure you want to delete this task?';

    // Show the confirmation modal
    $('#confirmationModal').modal('show');

    // Handle the confirmation action
    document.getElementById('confirmButton').onclick = function() {
        fetch(`/task/delete/${taskId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
        .then(response => {
            if (response.ok) {
                document.querySelector(`li[data-id="${taskId}"]`).remove();
            } else {
                alert('Failed to delete task.');
            }
        });

        // Hide the confirmation modal
        $('#confirmationModal').modal('hide');
    };
}


function updateTask(taskId) {
    const currentUrl = window.location.pathname;
    const updateUrl = `/update_task/${taskId}/?next=${encodeURIComponent(currentUrl)}`;
    window.location.href = updateUrl;
}


function viewHistory(taskId) {
    document.getElementById("mySidebar").style.width = "300px";
    console.log(taskId)
    if (!taskId) {
        console.error('No taskId provided!');
        return; // Early exit if taskId is undefined
    }


    // Fetch the task history from the server
    fetch(`/task/viewHistory/${taskId}` )     
        .then((response) => response.json()) // Parse the JSON response
        .then((data) => {
            const taskHistoryPanel = document.getElementById("taskHistoryPanel"); // Select the panel where history will be displayed
            taskHistoryPanel.innerHTML = ""; // Clear existing content
           
            console.log(data)
            
            // Loop through each history record and add it to the side panel
            if (data.length === 0) {
                taskHistoryPanel.innerHTML = 'No history available.';
            } else {
                data.forEach(record => {
                    const historyItem = document.createElement('a');
                    historyItem.className = 'history-item';
                                
                    const dateContainer = document.createElement('div');
                    const DateIcon = document.createElement('i');
                    DateIcon.className = 'fa fa-calendar'; // Add Font Awesome classes
                    const dateElement = document.createElement('span');
                    dateElement.innerText = `      ${record.history_date}`;
                             
                    dateContainer.appendChild(DateIcon);
                    dateContainer.appendChild(dateElement);
           
                    const userContainer = document.createElement('div');
                    const UserIcon = document.createElement('i');
                    UserIcon.className = 'fa fa-user'; // Add Font Awesome classes
                    const userElement = document.createElement('span');
                    userElement.innerText = `       ${record.history_user}`;

                    userContainer.appendChild(UserIcon);
                    userContainer.appendChild(userElement);
                                
                    historyItem.appendChild(dateContainer);
                    historyItem.appendChild(userContainer);

                    taskHistoryPanel.appendChild(historyItem);
            });

        }})
        .catch(console.error);

}

function closeHistory() {
    document.getElementById("mySidebar").style.width = "0";
}



function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function addTaskToSprint(taskId, sprint_name, is_removing) {
    if (is_removing){
        alert(`Removing task ${taskId} from ${sprint_name}`);
    }
    else {
        alert(`Adding task ${taskId} to ${sprint_name}`);
    }
    // get task id
    
    // get the task from the database using the id
    fetch(`/task/${taskId}/`)
    .then(response => {
        console.log(`Response status: ${response.status}`);
        return response.json()})
    .then(data => {
        if (!data) {
            console.error('No data received');
            return;
        }
        console.log(data);
        // Handle the task data
        console.log(`Task Name: ${data['task']['name']}`);
        console.log(`Given Sprint Name: ${sprint_name}`);

        console.log(`Before Associated Sprint : ${data['task']['sprint_name']}`);


        // Add the sprint ID to the task data
        data['task']['sprint_name'] = sprint_name;
        console.log('is_removing:', is_removing);
        if (is_removing) {
            console.log('Removing task from sprint');
            data['task']['sprint_name'] = null;
        }

        console.log(`Sprint Name Before sending to db: ${data['task']['sprint_name']}`);


        // Update the task in the database
        return fetch(`/task/update/${taskId}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({task: data['task']}),
        });
    })
    .then(response => {
        console.log(`PUT Response status: ${response.status}`);
        return response.json();
    })
    .then(updatedData => {
        console.log('Updated task data:', updatedData);
        location.reload();
        if (updatedData['task']['sprint_name'] !== sprint_name) {
            console.error('Sprint name was not updated correctly.');
        } else {
            console.log('Task successfully added to sprint.');
        }
    })
}




document.addEventListener("DOMContentLoaded", function() {
    const detailsCells = document.querySelectorAll(".details-cell");

    detailsCells.forEach(function(cell) {
        const text = cell.textContent.trim();
        if (text.length > 150) {
            cell.textContent = text.substring(0, 150) + "...";
        }
    });

    const priorityElements = document.querySelectorAll(".priority");
    priorityElements.forEach(function(element) {
        const priorityText = element.textContent.trim().toLowerCase();
        if (priorityText === "low") {
            element.classList.add("low-priority");
        } else if (priorityText === "medium") {
            element.classList.add("medium-priority");
        } else if (priorityText === "important") {
            element.classList.add("important-priority");
        } else if (priorityText === "urgent") {
            element.classList.add("urgent-priority");
        }
    });
});




