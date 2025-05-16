import json
import os
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, id, username, email, password_hash, role, name="", phone="", address="", latitude=None, longitude=None,  date_joined=None):
        self.id = id
        self.username = username
        self.email = email 
        self.password_hash = password_hash
        self.role = role
        self.name = name
        self.phone = phone
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
        self.date_joined = datetime.now().isoformat()
        self.date_joined = date_joined if date_joined else datetime.now().isoformat()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def get_by_id(cls, user_id):
        users = cls.get_all_users()
        for user in users:
            if user.id == user_id:
                return user
        return None

    @classmethod
    def get_by_username(cls, username):
        users = cls.get_all_users()
        for user in users:
            if user.username == username:
                return user
        return None

    @classmethod
    def get_by_email(cls, email):
        users = cls.get_all_users()
        for user in users:
            if user.email == email:
                return user
        return None

    @classmethod
    def get_all_users(cls):
        if not os.path.exists('data/users.json'):
            return []
            
        with open('data/users.json', 'r') as f:
            users_data = json.load(f)
            
        return [cls(**user_data) for user_data in users_data]

    @classmethod
    def get_next_id(cls):
        users = cls.get_all_users()
        if not users:
            return 1
        return max(user.id for user in users) + 1

    def save(self):
        users = self.get_all_users()
        
        # Check if user already exists (update)
        for i, user in enumerate(users):
            if user.id == self.id:
                users[i] = self
                break
        else:
            # User doesn't exist, add it
            users.append(self)
            
        # Save to JSON file
        with open('data/users.json', 'w') as f:
            json.dump([user.__dict__ for user in users], f, indent=2)
            
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'name': self.name,
            'phone': self.phone,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'date_joined': self.date_joined
        }


class FoodListing:
    def __init__(self, id, title, description, quantity, category, expiration_date, 
                 donor_id, status="available", image_filename=None, created_at=None,
                 location=None, latitude=None, longitude=None, donor=None):
        self.id = id
        self.title = title
        self.description = description
        self.quantity = quantity
        self.category = category
        self.expiration_date = expiration_date
        self.donor_id = donor_id
        self.status = status
        self.image_filename = image_filename
        self.created_at = created_at if created_at else datetime.now().isoformat()
        self.location = location
        self.latitude = latitude
        self.longitude = longitude
        self.donor = donor

    @classmethod
    def get_by_id(cls, listing_id):
        listings = cls.get_all_listings()
        for listing in listings:
            if listing.id == listing_id:
                return listing
        return None

    @classmethod
    def get_by_donor(cls, donor_id):
        return [listing for listing in cls.get_all_listings() if listing.donor_id == donor_id]

    @classmethod
    def get_available_listings(cls):
        return [listing for listing in cls.get_all_listings() if listing.status == "available"]

    @classmethod
    def get_all_listings(cls):
        if not os.path.exists('data/food_listings.json'):
            return []
            
        with open('data/food_listings.json', 'r') as f:
            listings_data = json.load(f)
            
        return [cls(**listing_data) for listing_data in listings_data]

    @classmethod
    def get_next_id(cls):
        listings = cls.get_all_listings()
        if not listings:
            return 1
        return max(listing.id for listing in listings) + 1

    def save(self):
        listings = self.get_all_listings()
        
        # Check if listing already exists (update)
        for i, listing in enumerate(listings):
            if listing.id == self.id:
                listings[i] = self
                break
        else:
            # Listing doesn't exist, add it
            listings.append(self)
            
        # Save to JSON file
        with open('data/food_listings.json', 'w') as f:
            json.dump([listing.__dict__ for listing in listings], f, indent=2)

    def delete(self):
        listings = self.get_all_listings()
        
        # Remove listing if it exists
        listings = [listing for listing in listings if listing.id != self.id]
            
        # Save to JSON file
        with open('data/food_listings.json', 'w') as f:
            json.dump([listing.__dict__ for listing in listings], f, indent=2)


class Pickup:
    def __init__(self, id, listing_id, recipient_id, pickup_time, status="pending", 
                 notes=None, created_at=None):
        self.id = id
        self.listing_id = listing_id
        self.recipient_id = recipient_id
        self.pickup_time = pickup_time
        self.status = status  # pending, confirmed, completed, cancelled
        self.notes = notes
        self.created_at = created_at if created_at else datetime.now().isoformat()

    @classmethod
    def get_by_id(cls, pickup_id):
        pickups = cls.get_all_pickups()
        for pickup in pickups:
            if pickup.id == pickup_id:
                return pickup
        return None

    @classmethod
    def get_by_listing(cls, listing_id):
        return [pickup for pickup in cls.get_all_pickups() if pickup.listing_id == listing_id]

    @classmethod
    def get_by_recipient(cls, recipient_id):
        return [pickup for pickup in cls.get_all_pickups() if pickup.recipient_id == recipient_id]

    @classmethod
    def get_all_pickups(cls):
        if not os.path.exists('data/pickups.json'):
            return []
            
        with open('data/pickups.json', 'r') as f:
            pickups_data = json.load(f)
            
        return [cls(**pickup_data) for pickup_data in pickups_data]

    @classmethod
    def get_next_id(cls):
        pickups = cls.get_all_pickups()
        if not pickups:
            return 1
        return max(pickup.id for pickup in pickups) + 1

    def save(self):
        pickups = self.get_all_pickups()
        
        # Check if pickup already exists (update)
        for i, pickup in enumerate(pickups):
            if pickup.id == self.id:
                pickups[i] = self
                break
        else:
            # Pickup doesn't exist, add it
            pickups.append(self)
            
        # Save to JSON file
        with open('data/pickups.json', 'w') as f:
            json.dump([pickup.__dict__ for pickup in pickups], f, indent=2)
