function showNotification(message) {
    const messageElement = document.getElementById('notificationMessage');
    messageElement.innerHTML = message;
    $('#notificationModal').modal('show');
}

function showConfirmation(message, onConfirm) {
    const messageElement = document.getElementById('confirmationMessage');
    const confirmButton = document.getElementById('confirmButton');

    messageElement.textContent = message;
    $('#confirmationModal').modal('show');

    confirmButton.onclick = function() {
        $('#confirmationModal').modal('hide');
        onConfirm();
    };
}


// Delete a user
function deleteUser(userId, event) {
    event.stopPropagation();

    document.getElementById('confirmationMessage').innerText = 'Are you sure you want to delete this user?';
    $('#confirmationModal').modal('show');

    document.getElementById('confirmButton').onclick = function() {
        fetch(`/delete_user/${userId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
        .then(response => {
            if (response.ok) {
                // Remove the user row from the table
                document.querySelector(`tr[data-user-id="${userId}"]`).remove();
            } else {
                alert('Failed to delete user.');
            }
        });

        $('#confirmationModal').modal('hide');
    };
}

// Helper function to get CSRF token
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