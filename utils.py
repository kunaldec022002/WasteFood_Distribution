import math
import os
from datetime import datetime
from models import User, FoodListing, Pickup
from app import app

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two points using Haversine formula
    Returns distance in miles
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 3956  # Radius of earth in miles
    return c * r

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_stats(donor_id=None, recipient_id=None):
    """Get statistics for the platform or for a specific user"""
    stats = {}
    
    # Get all data
    all_users = User.get_all_users()
    all_listings = FoodListing.get_all_listings()
    all_pickups = Pickup.get_all_pickups()
    
    # Filter by donor if specified
    if donor_id:
        donor_listings = [l for l in all_listings if l.donor_id == donor_id]
        donor_pickups = []
        for listing in donor_listings:
            donor_pickups.extend([p for p in all_pickups if p.listing_id == listing.id])
        
        stats['total_donations'] = len(donor_listings)
        stats['completed_donations'] = len([l for l in donor_listings if l.status == 'completed'])
        stats['pending_pickups'] = len([p for p in donor_pickups if p.status == 'pending'])
        stats['confirmed_pickups'] = len([p for p in donor_pickups if p.status == 'confirmed'])
        
        # Calculate impact
        stats['total_impact'] = stats['completed_donations']
        return stats
    
    # Filter by recipient if specified
    if recipient_id:
        recipient_pickups = [p for p in all_pickups if p.recipient_id == recipient_id]
        
        stats['requested_pickups'] = len(recipient_pickups)
        stats['completed_pickups'] = len([p for p in recipient_pickups if p.status == 'completed'])
        stats['pending_pickups'] = len([p for p in recipient_pickups if p.status == 'pending'])
        stats['confirmed_pickups'] = len([p for p in recipient_pickups if p.status == 'confirmed'])
        
        # Categories received
        listing_ids = [p.listing_id for p in recipient_pickups if p.status == 'completed']
        completed_listings = [l for l in all_listings if l.id in listing_ids]
        categories = {}
        for listing in completed_listings:
            if listing.category not in categories:
                categories[listing.category] = 0
            categories[listing.category] += 1
        
        stats['categories'] = categories
        return stats
    
    # Global stats
    stats['total_users'] = len(all_users)
    stats['donors'] = len([u for u in all_users if u.role == 'donor'])
    stats['recipients'] = len([u for u in all_users if u.role == 'recipient'])
    
    stats['total_listings'] = len(all_listings)
    stats['available_listings'] = len([l for l in all_listings if l.status == 'available'])
    stats['completed_donations'] = len([l for l in all_listings if l.status == 'completed'])
    
    stats['total_pickups'] = len(all_pickups)
    stats['completed_pickups'] = len([p for p in all_pickups if p.status == 'completed'])
    
    # Calculate food waste avoided
    # Let's say 1 listing is approximately 5 pounds of food
    stats['food_saved_lbs'] = stats['completed_donations'] * 5
    
    # Calculate carbon footprint reduction
    # Let's say 1 pound of food waste produces 2.5 kg of CO2
    stats['carbon_reduction_kg'] = stats['food_saved_lbs'] * 2.5
    
    return stats
