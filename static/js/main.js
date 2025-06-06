// Custom JavaScript functions

// Function to format dates
function formatDate(date) {
    return new Date(date).toLocaleDateString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

// Function to format datetime
function formatDateTime(datetime) {
    return new Date(datetime).toLocaleString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Function to confirm delete actions
function confirmDelete(message) {
    return confirm(message || 'Êtes-vous sûr de vouloir supprimer cet élément ?');
}

// Function to handle AJAX errors
function handleAjaxError(xhr, status, error) {
    console.error('Erreur AJAX:', error);
    alert('Une erreur est survenue. Veuillez réessayer plus tard.');
}