import os
import json
from datetime import datetime, timedelta
import uuid
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from app import app
from models import User, FoodListing, Pickup
from forms import (
    LoginForm, RegistrationForm, FoodListingForm, PickupForm, 
    UpdateProfileForm, SearchForm
)
from utils import calculate_distance, allowed_file, get_stats

# Home page
@app.route('/')
def index():
    # Get some statistics for the homepage
    stats = get_stats()
    
    # Get latest 5 available listings
    latest_listings = [listing for listing in FoodListing.get_all_listings() 
                      if listing.status == "available"]
    latest_listings.sort(key=lambda x: x.created_at, reverse=True)
    latest_listings = latest_listings[:5]
    
    return render_template('index.html', 
                          latest_listings=latest_listings,
                          stats=stats)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username already exists
        if User.get_by_username(form.username.data):
            flash('Username already taken.', 'danger')
            return render_template('register.html', form=form)
            
        # Check if email already exists
        if User.get_by_email(form.email.data):
            flash('Email already registered.', 'danger')
            return render_template('register.html', form=form)
            
        # Create new user
        user = User(
            id=User.get_next_id(),
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            role=form.role.data,
            name=form.name.data,
            phone=form.phone.data,
            address=form.address.data,
            latitude=form.latitude.data if form.latitude.data else None,
            longitude=form.longitude.data if form.longitude.data else None
        )
        user.save()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'donor':
        # Get all listings for this donor
        listings = FoodListing.get_by_donor(current_user.id)
        
        # Get all pickups for these listings
        pickups = []
        for listing in listings:
            listing_pickups = Pickup.get_by_listing(listing.id)
            for pickup in listing_pickups:
                pickup.listing = listing
                pickup.recipient = User.get_by_id(pickup.recipient_id)
                pickups.append(pickup)
                
        return render_template('dashboard.html', 
                              listings=listings, 
                              pickups=pickups,
                              stats=get_stats(donor_id=current_user.id))
    else:
        # For recipients, show claimed items and available listings
        my_pickups = Pickup.get_by_recipient(current_user.id)
        
        # Get the associated listings
        for pickup in my_pickups:
            pickup.listing = FoodListing.get_by_id(pickup.listing_id)
            pickup.donor = User.get_by_id(pickup.listing.donor_id)
            
        # Get available listings
        available_listings = FoodListing.get_available_listings()
        
        # Sort by distance if we have user coordinates
        if current_user.latitude and current_user.longitude:
            for listing in available_listings:
                donor = User.get_by_id(listing.donor_id)
                if donor.latitude and donor.longitude:
                    listing.distance = calculate_distance(
                        float(current_user.latitude), 
                        float(current_user.longitude),
                        float(donor.latitude), 
                        float(donor.longitude)
                    )
                else:
                    listing.distance = None
                    
            # Sort listings with distance by distance, then those without
            listings_with_distance = [l for l in available_listings if hasattr(l, 'distance') and l.distance is not None]
            listings_without_distance = [l for l in available_listings if not hasattr(l, 'distance') or l.distance is None]
            
            listings_with_distance.sort(key=lambda x: x.distance)
            available_listings = listings_with_distance + listings_without_distance
            
        return render_template('dashboard.html', 
                             my_pickups=my_pickups, 
                             available_listings=available_listings[:10],
                             stats=get_stats(recipient_id=current_user.id))

# Food listing routes
@app.route('/food/create', methods=['GET', 'POST'])
@login_required
def create_listing():
    if current_user.role != 'donor':
        flash('Only donors can create food listings.', 'danger')
        return redirect(url_for('dashboard'))
        
    form = FoodListingForm()
    if form.validate_on_submit():
        # Handle image upload
        image_filename = None
        if form.image.data:
            if allowed_file(form.image.data.filename):
                filename = secure_filename(form.image.data.filename)
                # Add a UUID to ensure uniqueness
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                image_filename = unique_filename
        
        # Create new food listing
        listing = FoodListing(
            id=FoodListing.get_next_id(),
            title=form.title.data,
            description=form.description.data,
            quantity=form.quantity.data,
            category=form.category.data,
            expiration_date=form.expiration_date.data.isoformat(),
            donor_id=current_user.id,
            image_filename=image_filename,
            location=form.location.data,
            latitude=form.latitude.data if form.latitude.data else None,
            longitude=form.longitude.data if form.longitude.data else None
        )
        listing.save()
        
        flash('Food listing created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    # Pre-fill location info from user profile
    form.location.data = current_user.address
    form.latitude.data = current_user.latitude
    form.longitude.data = current_user.longitude
    
    return render_template('create_listing.html', form=form)

@app.route('/food/listings')
def food_listings():
    form = SearchForm(request.args, meta={'csrf': False})
    
    # Get all available listings
    listings = FoodListing.get_available_listings()
    
    # Apply search filters if provided
    if form.validate():
        # Filter by category
        if form.category.data and form.category.data != 'all':
            listings = [l for l in listings if l.category == form.category.data]
            
        # Filter by search query
        if form.query.data:
            query = form.query.data.lower()
            listings = [l for l in listings if 
                      query in l.title.lower() or 
                      query in l.description.lower()]
                      
        # Filter by distance
        if current_user.is_authenticated and form.distance.data and form.distance.data != '0':
            max_distance = int(form.distance.data)
            
            if current_user.latitude and current_user.longitude:
                filtered_listings = []
                
                for listing in listings:
                    donor = User.get_by_id(listing.donor_id)
                    
                    if donor.latitude and donor.longitude:
                        distance = calculate_distance(
                            float(current_user.latitude),
                            float(current_user.longitude),
                            float(donor.latitude),
                            float(donor.longitude)
                        )
                        
                        if distance <= max_distance:
                            listing.distance = distance
                            filtered_listings.append(listing)
                
                listings = filtered_listings
    
    # Get donor info for each listing
    for listing in listings:
        listing.donor = User.get_by_id(listing.donor_id)
        
    # Sort listings - newest first
    listings.sort(key=lambda x: x.created_at, reverse=True)
        
    return render_template('food_listings.html', listings=listings, form=form)

@app.route('/food/<int:listing_id>')
def food_detail(listing_id):
    listing = FoodListing.get_by_id(listing_id)
    
    if not listing:
        flash('Listing not found.', 'danger')
        return redirect(url_for('food_listings'))
        
    # Get donor info
    listing.donor = User.get_by_id(listing.donor_id)
    
    # Calculate distance for logged-in recipients
    if current_user.is_authenticated and current_user.role == 'recipient':
        if current_user.latitude and current_user.longitude and listing.donor.latitude and listing.donor.longitude:
            listing.distance = calculate_distance(
                float(current_user.latitude),
                float(current_user.longitude),
                float(listing.donor.latitude),
                float(listing.donor.longitude)
            )
    
    return render_template('food_detail.html', listing=listing)

@app.route('/food/<int:listing_id>/request', methods=['GET', 'POST'])
@login_required
def request_pickup(listing_id):
    if current_user.role != 'recipient':
        flash('Only recipients can request food pickups.', 'danger')
        return redirect(url_for('food_detail', listing_id=listing_id))
        
    listing = FoodListing.get_by_id(listing_id)
    
    if not listing:
        flash('Listing not found.', 'danger')
        return redirect(url_for('food_listings'))
        
    if listing.status != 'available':
        flash('This food listing is no longer available.', 'danger')
        return redirect(url_for('food_detail', listing_id=listing_id))
    
    form = PickupForm()
    if form.validate_on_submit():
        # Create pickup request
        pickup = Pickup(
            id=Pickup.get_next_id(),
            listing_id=listing_id,
            recipient_id=current_user.id,
            pickup_time=form.pickup_time.data.isoformat(),
            notes=form.notes.data
        )
        pickup.save()
        
        # Update listing status
        listing.status = 'pending'
        listing.save()
        
        flash('Pickup request submitted successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    # Pre-fill form with default pickup time (tomorrow)
    if not form.pickup_time.data:
        form.pickup_time.data = datetime.now() + timedelta(days=1)
    
    return render_template('pickup_delivery.html', form=form, listing=listing)

@app.route('/pickup/<int:pickup_id>/status/<status>', methods=['POST'])
@login_required
def update_pickup_status(pickup_id, status):
    pickup = Pickup.get_by_id(pickup_id)
    
    if not pickup:
        flash('Pickup request not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    listing = FoodListing.get_by_id(pickup.listing_id)
    
    if not listing:
        flash('Associated food listing not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Verify permissions
    if current_user.role == 'donor' and listing.donor_id != current_user.id:
        flash('You do not have permission to update this pickup.', 'danger')
        return redirect(url_for('dashboard'))
    
    if current_user.role == 'recipient' and pickup.recipient_id != current_user.id:
        flash('You do not have permission to update this pickup.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Update pickup status
    valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled']
    if status not in valid_statuses:
        flash('Invalid status.', 'danger')
        return redirect(url_for('dashboard'))
    
    pickup.status = status
    pickup.save()
    
    # Update listing status
    if status == 'confirmed':
        listing.status = 'reserved'
    elif status == 'completed':
        listing.status = 'completed'
    elif status == 'cancelled' and listing.status != 'completed':
        listing.status = 'available'
    
    listing.save()
    
    flash(f'Pickup status updated to {status}.', 'success')
    return redirect(url_for('dashboard'))

# User profile
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        # Update user info
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        current_user.latitude = form.latitude.data
        current_user.longitude = form.longitude.data
        
        current_user.save()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', form=form)

# Analytics
@app.route('/analytics')
@login_required
def analytics():
    # Different analytics based on user role
    stats = get_stats(
        donor_id=current_user.id if current_user.role == 'donor' else None,
        recipient_id=current_user.id if current_user.role == 'recipient' else None
    )
    
    # Get donor's completed pickups with their listings
    if current_user.role == 'donor':
        listings = FoodListing.get_by_donor(current_user.id)
        
        # Get all pickups for these listings
        completed_pickups = []
        for listing in listings:
            listing_pickups = [p for p in Pickup.get_by_listing(listing.id) if p.status == 'completed']
            for pickup in listing_pickups:
                pickup.listing = listing
                pickup.recipient = User.get_by_id(pickup.recipient_id)
                completed_pickups.append(pickup)
        
        # Get monthly donation data
        monthly_data = {}
        for pickup in completed_pickups:
            month = datetime.fromisoformat(pickup.completed_at if hasattr(pickup, 'completed_at') else pickup.created_at).strftime('%Y-%m')
            if month not in monthly_data:
                monthly_data[month] = 0
            monthly_data[month] += 1
            
        # Sort by month
        sorted_months = sorted(monthly_data.keys())
        monthly_counts = [monthly_data[month] for month in sorted_months]
        
        return render_template('analytics.html', 
                           stats=stats, 
                           pickups=completed_pickups,
                           months=sorted_months,
                           monthly_counts=monthly_counts)
    
    # Get recipient's completed pickups with their listings
    if current_user.role == 'recipient':
        my_pickups = [p for p in Pickup.get_by_recipient(current_user.id) if p.status == 'completed']
        
        # Get the associated listings
        for pickup in my_pickups:
            pickup.listing = FoodListing.get_by_id(pickup.listing_id)
            pickup.donor = User.get_by_id(pickup.listing.donor_id)
            
        # Get monthly pickup data
        monthly_data = {}
        for pickup in my_pickups:
            month = datetime.fromisoformat(pickup.completed_at if hasattr(pickup, 'completed_at') else pickup.created_at).strftime('%Y-%m')
            if month not in monthly_data:
                monthly_data[month] = 0
            monthly_data[month] += 1
            
        # Sort by month
        sorted_months = sorted(monthly_data.keys())
        monthly_counts = [monthly_data[month] for month in sorted_months]
        
        # Get category distribution
        categories = {}
        for pickup in my_pickups:
            category = pickup.listing.category
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
            
        return render_template('analytics.html', 
                           stats=stats, 
                           pickups=my_pickups,
                           months=sorted_months,
                           monthly_counts=monthly_counts,
                           categories=list(categories.keys()),
                           category_counts=list(categories.values()))
    
    return render_template('analytics.html', stats=stats)

# Admin route
@app.route('/admin')
@login_required
def admin():
    # Check if user is admin
    if not hasattr(current_user, 'role') or current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    users = User.get_all_users()
    listings = FoodListing.get_all_listings()
    pickups = Pickup.get_all_pickups()
    
    stats = get_stats()
    
    return render_template('admin.html', 
                         users=users,
                         listings=listings,
                         pickups=pickups,
                         stats=stats)

# Map data endpoints
@app.route('/api/map/donors')
def map_donors():
    donors = [user for user in User.get_all_users() if user.role == 'donor' and user.latitude and user.longitude]
    return jsonify([{
        'id': donor.id,
        'name': donor.name,
        'latitude': donor.latitude,
        'longitude': donor.longitude,
        'address': donor.address
    } for donor in donors])

@app.route('/api/map/listings')
def map_listings():
    listings = FoodListing.get_available_listings()
    result = []
    
    for listing in listings:
        donor = User.get_by_id(listing.donor_id)
        if donor and donor.latitude and donor.longitude:
            result.append({
                'id': listing.id,
                'title': listing.title,
                'category': listing.category,
                'latitude': donor.latitude if not listing.latitude else listing.latitude,
                'longitude': donor.longitude if not listing.longitude else listing.longitude,
                'donor_name': donor.name,
                'url': url_for('food_detail', listing_id=listing.id)
            })
    
    return jsonify(result)
