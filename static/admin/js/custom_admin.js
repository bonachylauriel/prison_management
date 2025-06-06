document.addEventListener('DOMContentLoaded', function() {
    // Initialisation des graphiques si l'élément canvas existe
    const teamsChartElement = document.getElementById('teamsChart');
    if (teamsChartElement) {
        const ctx = teamsChartElement.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Équipe A', 'Équipe B', 'Équipe C', 'Équipe D'],
                datasets: [{
                    label: 'Nombre de membres',
                    data: [12, 19, 8, 15],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 99, 132, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Fonction pour les confirmations d'actions
    const confirmAction = (e) => {
        if (!confirm('Êtes-vous sûr de vouloir effectuer cette action ?')) {
            e.preventDefault();
        }
    };

    // Ajouter la confirmation aux boutons d'action
    document.querySelectorAll('.action-button').forEach(button => {
        button.addEventListener('click', confirmAction);
    });
});

// Fonction pour rafraîchir automatiquement les données du tableau de bord
function refreshDashboard() {
    // À implémenter si nécessaire
}