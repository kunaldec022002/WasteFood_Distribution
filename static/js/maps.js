// Initialize the map when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Check if there's a map container on the page
    const mapContainer = document.getElementById('map');
    if (!mapContainer) return;

    // Initialize the map
    const map = L.map('map').setView([40.7128, -74.0060], 12); // Default to NYC
    
    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    
    // Create different icons for donors and listings
    const donorIcon = L.icon({
        iconUrl: 'https://cdn.jsdelivr.net/npm/leaflet@1.7.1/dist/images/marker-icon.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowUrl: 'https://cdn.jsdelivr.net/npm/leaflet@1.7.1/dist/images/marker-shadow.png',
        shadowSize: [41, 41]
    });
    
    const listingIcon = L.icon({
        iconUrl: 'https://cdn.jsdelivr.net/npm/leaflet@1.7.1/dist/images/marker-icon-red.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowUrl: 'https://cdn.jsdelivr.net/npm/leaflet@1.7.1/dist/images/marker-shadow.png',
        shadowSize: [41, 41]
    });
    
    // Add markers based on the page
    const pageType = mapContainer.dataset.pageType;
    
    if (pageType === 'listings') {
        // Show food listings on the map
        fetch('/api/map/listings')
            .then(response => response.json())
            .then(listings => {
                if (listings.length === 0) {
                    map.setView([40.7128, -74.0060], 12); // Default view if no listings
                    return;
                }
                
                const bounds = L.latLngBounds();
                
                listings.forEach(listing => {
                    const marker = L.marker([listing.latitude, listing.longitude], {icon: listingIcon}).addTo(map);
                    marker.bindPopup(`
                        <strong>${listing.title}</strong><br>
                        Category: ${listing.category}<br>
                        Donor: ${listing.donor_name}<br>
                        <a href="${listing.url}" class="btn btn-sm btn-primary mt-2">View Details</a>
                    `);
                    
                    bounds.extend([listing.latitude, listing.longitude]);
                });
                
                // Fit map to bounds with padding
                map.fitBounds(bounds, { padding: [50, 50] });
            })
            .catch(error => console.error('Error fetching listing data:', error));
    } else if (pageType === 'donors') {
        // Show donors on the map
        fetch('/api/map/donors')
            .then(response => response.json())
            .then(donors => {
                if (donors.length === 0) {
                    map.setView([40.7128, -74.0060], 12); // Default view if no donors
                    return;
                }
                
                const bounds = L.latLngBounds();
                
                donors.forEach(donor => {
                    const marker = L.marker([donor.latitude, donor.longitude], {icon: donorIcon}).addTo(map);
                    marker.bindPopup(`
                        <strong>${donor.name}</strong><br>
                        ${donor.address}
                    `);
                    
                    bounds.extend([donor.latitude, donor.longitude]);
                });
                
                // Fit map to bounds with padding
                map.fitBounds(bounds, { padding: [50, 50] });
            })
            .catch(error => console.error('Error fetching donor data:', error));
    } else if (pageType === 'location-picker') {
        // Special map for picking a location (used in forms)
        let marker;
        const latInput = document.getElementById(mapContainer.dataset.latField);
        const lngInput = document.getElementById(mapContainer.dataset.lngField);
        const addressInput = document.getElementById(mapContainer.dataset.addressField);
        
        // Check if we already have coordinates in the form
        if (latInput.value && lngInput.value) {
            map.setView([latInput.value, lngInput.value], 15);
            marker = L.marker([latInput.value, lngInput.value], {draggable: true}).addTo(map);
        } else {
            // Try to geolocate the user
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    position => {
                        map.setView([position.coords.latitude, position.coords.longitude], 15);
                        marker = L.marker([position.coords.latitude, position.coords.longitude], {draggable: true}).addTo(map);
                        
                        // Update form fields
                        latInput.value = position.coords.latitude;
                        lngInput.value = position.coords.longitude;
                        
                        // Get address for this location
                        reverseGeocode(position.coords.latitude, position.coords.longitude, addressInput);
                    },
                    error => {
                        console.error('Error getting location:', error);
                        map.setView([40.7128, -74.0060], 12); // Default to NYC
                    }
                );
            } else {
                map.setView([40.7128, -74.0060], 12); // Default to NYC
            }
        }
        
        // Handle map clicks to set marker
        map.on('click', function(e) {
            if (marker) {
                marker.setLatLng(e.latlng);
            } else {
                marker = L.marker(e.latlng, {draggable: true}).addTo(map);
            }
            
            // Update form fields
            latInput.value = e.latlng.lat;
            lngInput.value = e.latlng.lng;
            
            // Get address for this location
            reverseGeocode(e.latlng.lat, e.latlng.lng, addressInput);
        });
        
        // If a marker exists and is draggable, handle dragend event
        if (marker) {
            marker.on('dragend', function(e) {
                const latlng = e.target.getLatLng();
                
                // Update form fields
                latInput.value = latlng.lat;
                lngInput.value = latlng.lng;
                
                // Get address for this location
                reverseGeocode(latlng.lat, latlng.lng, addressInput);
            });
        }
        
        // If address input exists, add a geocoding search feature
        if (addressInput) {
            addressInput.addEventListener('change', function() {
                geocodeAddress(addressInput.value, map, marker, latInput, lngInput);
            });
        }
    }
});

// Geocode an address to get coordinates
function geocodeAddress(address, map, marker, latInput, lngInput) {
    // Using Nominatim for geocoding (free OpenStreetMap service)
    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}&limit=1`)
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                const lat = parseFloat(data[0].lat);
                const lng = parseFloat(data[0].lon);
                
                // Update map view
                map.setView([lat, lng], 15);
                
                // Update or create marker
                if (marker) {
                    marker.setLatLng([lat, lng]);
                } else {
                    marker = L.marker([lat, lng], {draggable: true}).addTo(map);
                }
                
                // Update form fields
                latInput.value = lat;
                lngInput.value = lng;
            }
        })
        .catch(error => console.error('Error geocoding address:', error));
}

// Reverse geocode coordinates to get an address
function reverseGeocode(lat, lng, addressInput) {
    if (!addressInput) return;
    
    // Using Nominatim for reverse geocoding (free OpenStreetMap service)
    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`)
        .then(response => response.json())
        .then(data => {
            if (data && data.display_name) {
                addressInput.value = data.display_name;
            }
        })
        .catch(error => console.error('Error reverse geocoding:', error));
}
