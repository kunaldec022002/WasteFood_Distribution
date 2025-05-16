document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize all popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Handle file input display
    const fileInputs = document.querySelectorAll('.custom-file-input');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            // Get the file name
            let fileName = this.files[0].name;
            // Find the label associated with this input
            const label = this.nextElementSibling;
            if (label) {
                label.innerText = fileName;
            }
            
            // Show image preview if applicable
            const previewContainer = document.getElementById(`${this.id}-preview`);
            if (previewContainer && this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewContainer.innerHTML = `<img src="${e.target.result}" class="img-thumbnail mb-2" alt="Preview">`;
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    });
    
    // Handle expiration date input validation
    const expirationDateInput = document.getElementById('expiration_date');
    if (expirationDateInput) {
        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        expirationDateInput.min = today;
        
        expirationDateInput.addEventListener('change', function() {
            const selectedDate = new Date(this.value);
            const now = new Date();
            
            // Check if date is in the past
            if (selectedDate < now) {
                this.setCustomValidity('Expiration date cannot be in the past');
            } else {
                this.setCustomValidity('');
            }
        });
    }
    
    // Handle pickup time input validation
    const pickupTimeInput = document.getElementById('pickup_time');
    if (pickupTimeInput) {
        // Set minimum time to now + 1 hour
        const now = new Date();
        now.setHours(now.getHours() + 1);
        const minDateTime = now.toISOString().slice(0, 16);
        pickupTimeInput.min = minDateTime;
        
        pickupTimeInput.addEventListener('change', function() {
            const selectedTime = new Date(this.value);
            const now = new Date();
            
            // Check if time is at least 1 hour in the future
            const minTime = new Date(now.getTime() + 60 * 60 * 1000);
            if (selectedTime < minTime) {
                this.setCustomValidity('Pickup time must be at least 1 hour from now');
            } else {
                this.setCustomValidity('');
            }
        });
    }
    
    // Initialize category badges with appropriate colors
    const categoryBadges = document.querySelectorAll('.category-badge');
    categoryBadges.forEach(badge => {
        const category = badge.dataset.category;
        let badgeClass = 'bg-secondary';
        
        // Assign colors based on category
        switch (category) {
            case 'prepared':
                badgeClass = 'bg-success';
                break;
            case 'produce':
                badgeClass = 'bg-warning text-dark';
                break;
            case 'baked':
                badgeClass = 'bg-purple';
                break;
            case 'canned':
                badgeClass = 'bg-primary';
                break;
            case 'dairy':
                badgeClass = 'bg-info';
                break;
            case 'meat':
                badgeClass = 'bg-danger';
                break;
            case 'other':
                badgeClass = 'bg-secondary';
                break;
        }
        
        badge.classList.add(badgeClass);
    });
    
    // Initialize countdown for expiration dates
    const expirationCounters = document.querySelectorAll('.expiration-counter');
    expirationCounters.forEach(counter => {
        const expirationDate = new Date(counter.dataset.expiration);
        const now = new Date();
        
        // Calculate days remaining
        const diff = Math.floor((expirationDate - now) / (1000 * 60 * 60 * 24));
        
        // Update counter text and color
        counter.textContent = `${diff} day${diff !== 1 ? 's' : ''} left`;
        
        if (diff <= 1) {
            counter.classList.add('text-danger', 'fw-bold');
        } else if (diff <= 3) {
            counter.classList.add('text-warning', 'fw-bold');
        } else {
            counter.classList.add('text-success');
        }
    });
});
