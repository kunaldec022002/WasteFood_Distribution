document.addEventListener('DOMContentLoaded', function() {
    // Check if there are charts on the page
    const donationsChart = document.getElementById('donationsChart');
    const categoriesChart = document.getElementById('categoriesChart');
    
    // Initialize donation history chart if element exists
    if (donationsChart) {
        const ctx = donationsChart.getContext('2d');
        const months = JSON.parse(donationsChart.dataset.months || '[]');
        const counts = JSON.parse(donationsChart.dataset.counts || '[]');
        
        // Format month names for better display
        const formattedMonths = months.map(month => {
            const [year, monthNum] = month.split('-');
            return new Date(year, monthNum - 1).toLocaleString('default', { month: 'short', year: 'numeric' });
        });
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: formattedMonths,
                datasets: [{
                    label: 'Completed Donations/Pickups',
                    data: counts,
                    backgroundColor: 'rgba(40, 167, 69, 0.2)',
                    borderColor: 'rgba(40, 167, 69, 1)',
                    borderWidth: 2,
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true
                    },
                    tooltip: {
                        callbacks: {
                            title: function(tooltipItems) {
                                return tooltipItems[0].label;
                            },
                            label: function(context) {
                                return `${context.dataset.label}: ${context.raw}`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Initialize food categories chart if element exists
    if (categoriesChart) {
        const ctx = categoriesChart.getContext('2d');
        const categories = JSON.parse(categoriesChart.dataset.categories || '[]');
        const counts = JSON.parse(categoriesChart.dataset.counts || '[]');
        
        // Format category names for better display
        const formattedCategories = categories.map(category => {
            return category.charAt(0).toUpperCase() + category.slice(1);
        });
        
        // Generate colors based on categories
        const backgroundColors = [
            'rgba(40, 167, 69, 0.7)',    // Green (prepared)
            'rgba(255, 193, 7, 0.7)',    // Yellow (produce)
            'rgba(220, 53, 69, 0.7)',    // Red (meat)
            'rgba(23, 162, 184, 0.7)',   // Cyan (dairy)
            'rgba(111, 66, 193, 0.7)',   // Purple (baked)
            'rgba(0, 123, 255, 0.7)',    // Blue (canned)
            'rgba(108, 117, 125, 0.7)'   // Gray (other)
        ];
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: formattedCategories,
                datasets: [{
                    data: counts,
                    backgroundColor: backgroundColors.slice(0, categories.length),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Handle pickup status updates via AJAX
    const pickupStatusButtons = document.querySelectorAll('.pickup-status-btn');
    pickupStatusButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const pickupId = this.dataset.pickupId;
            const newStatus = this.dataset.status;
            const url = `/pickup/${pickupId}/status/${newStatus}`;
            
            // Show confirmation dialog for cancellations
            if (newStatus === 'cancelled') {
                if (!confirm('Are you sure you want to cancel this pickup?')) {
                    return;
                }
            }
            
            // Submit the form
            const form = this.closest('form');
            form.submit();
        });
    });
});
