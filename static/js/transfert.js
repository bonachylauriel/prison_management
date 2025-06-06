document.addEventListener('DOMContentLoaded', function() {
    const sourcePrison = document.getElementById('sourcePrison');
    const destinationPrison = document.getElementById('destinationPrison');
    const sourceInmates = document.getElementById('sourceInmates');
    const transferZone = document.getElementById('transferZone');
    const processTransfer = document.getElementById('processTransfer');
    const transferInfo = document.getElementById('transferInfo');
    const confirmTransferModal = new bootstrap.Modal(document.getElementById('confirmTransferModal'));
    const confirmTransferBtn = document.getElementById('confirmTransferBtn');

    // Configuration Sortable.js
    const sourceList = new Sortable(sourceInmates, {
        group: {
            name: 'inmates',
            pull: 'clone',
            put: false
        },
        sort: false,
        animation: 150,
        onStart: function(evt) {
            evt.item.classList.add('is-dragging');
        },
        onEnd: function(evt) {
            evt.item.classList.remove('is-dragging');
        }
    });

    const transferList = new Sortable(transferZone, {
        group: 'inmates',
        animation: 150,
        onAdd: function() {
            updateTransferButton();
        },
        onRemove: function() {
            updateTransferButton();
        }
    });

    // Événements
    sourcePrison.addEventListener('change', function() {
        loadInmates(this.value);
        loadAvailableDestinations(this.value);
    });

    destinationPrison.addEventListener('change', function() {
        updateTransferInfo();
        updateTransferButton();
    });

    processTransfer.addEventListener('click', function() {
        showConfirmationModal();
    });

    confirmTransferBtn.addEventListener('click', function() {
        processTransferRequest();
    });

    // Fonctions
    function loadInmates(prisonId) {
        if (!prisonId) {
            sourceInmates.innerHTML = getEmptyStateHTML('prison');
            return;
        }

        fetch(`/prisons/get-inmates/${prisonId}/`)
            .then(response => response.json())
            .then(inmates => {
                if (inmates.length === 0) {
                    sourceInmates.innerHTML = getEmptyStateHTML('inmates');
                    return;
                }

                sourceInmates.innerHTML = inmates.map(inmate => `
                    <div class="inmate-card" data-id="${inmate.id}">
                        <div class="inmate-number">${inmate.inmate_number}</div>
                        <div class="inmate-name">${inmate.first_name} ${inmate.last_name}</div>
                    </div>
                `).join('');
            });
    }

    function loadAvailableDestinations(prisonId) {
        if (!prisonId) {
            destinationPrison.innerHTML = '<option value="">Sélectionnez une prison</option>';
            destinationPrison.disabled = true;
            return;
        }

        fetch(`/prisons/get-connections/${prisonId}/`)
            .then(response => response.json())
            .then(connections => {
                destinationPrison.innerHTML = '<option value="">Sélectionnez une prison</option>' +
                    connections.map(conn => `
                        <option value="${conn.prison_to__id}" 
                                data-capacity="${conn.max_transfer_capacity}">
                            ${conn.prison_to__name}
                        </option>
                    `).join('');
                destinationPrison.disabled = false;
            });
    }

    function updateTransferInfo() {
        const selectedOption = destinationPrison.selectedOptions[0];
        if (selectedOption && selectedOption.dataset.capacity) {
            transferInfo.querySelector('.transfer-capacity-info').textContent =
                `Capacité maximale de transfert: ${selectedOption.dataset.capacity} détenus`;
            transferInfo.classList.remove('d-none');
        } else {
            transferInfo.classList.add('d-none');
        }
    }

    function updateTransferButton() {
        const hasInmates = transferZone.children.length > 0;
        const hasDestination = destinationPrison.value !== '';
        processTransfer.disabled = !(hasInmates && hasDestination);
    }

    function showConfirmationModal() {
        const inmates = Array.from(transferZone.children);
        const summary = document.getElementById('transferSummary');

        summary.innerHTML = `
            <p><strong>Nombre de détenus:</strong> ${inmates.length}</p>
            <p><strong>De:</strong> ${sourcePrison.selectedOptions[0].text}</p>
            <p><strong>Vers:</strong> ${destinationPrison.selectedOptions[0].text}</p>
        `;

        confirmTransferModal.show();
    }

    function processTransferRequest() {
        const formData = new FormData();
        formData.append('source_prison', sourcePrison.value);
        formData.append('destination_prison', destinationPrison.value);

        Array.from(transferZone.children).forEach(inmate => {
            formData.append('inmates[]', inmate.dataset.id);
        });

        fetch('/prisons/process-transfer/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            confirmTransferModal.hide();

            if (data.success) {
                showAlert('success', data.message);
                resetTransferZone();
                loadInmates(sourcePrison.value);
            } else {
                showAlert('danger', data.message);
            }
        })
        .catch(error => {
            confirmTransferModal.hide();
            showAlert('danger', 'Une erreur est survenue lors du transfert');
        });
    }

    function showAlert(type, message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.querySelector('.container-fluid').insertBefore(
            alertDiv,
            document.querySelector('.row')
        );

        setTimeout(() => alertDiv.remove(), 5000);
    }

    function resetTransferZone() {
        transferZone.innerHTML = getEmptyStateHTML('transfer');
        updateTransferButton();
    }

    function getEmptyStateHTML(type) {
        const messages = {
            prison: 'Sélectionnez une prison pour voir les détenus',
            inmates: 'Aucun détenu dans cette prison',
            transfer: 'Glissez les détenus ici'
        };

        return `
            <div class="text-center text-muted py-4">
                <i class="fas fa-info-circle mb-2"></i>
                <p>${messages[type]}</p>
            </div>
        `;
    }

    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
});