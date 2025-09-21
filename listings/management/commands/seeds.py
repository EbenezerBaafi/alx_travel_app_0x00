from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Listing, Booking, Review
from decimal import Decimal
from datetime import date, timedelta
import random
import uuid


class Command(BaseCommand):
    help = 'Seed the database with sample listing data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--listings',
            type=int,
            default=10,
            help='Number of listings to create (default: 10)'
        )
        parser.add_argument(
            '--users',
            type=int,
            default=5,
            help='Number of users to create (default: 5)'
        )
        parser.add_argument(
            '--bookings',
            type=int,
            default=20,
            help='Number of bookings to create (default: 20)'
        )
        parser.add_argument(
            '--reviews',
            type=int,
            default=15,
            help='Number of reviews to create (default: 15)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Review.objects.all().delete()
            Booking.objects.all().delete()
            Listing.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))
        
        # Create users
        self.stdout.write('Creating users...')
        users = self.create_users(options['users'])
        
        # Create listings
        self.stdout.write('Creating listings...')
        listings = self.create_listings(options['listings'], users)
        
        # Create bookings
        self.stdout.write('Creating bookings...')
        bookings = self.create_bookings(options['bookings'], listings, users)
        
        # Create reviews
        self.stdout.write('Creating reviews...')
        reviews = self.create_reviews(options['reviews'], listings, users, bookings)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded database with:\n'
                f'- {len(users)} users\n'
                f'- {len(listings)} listings\n'
                f'- {len(bookings)} bookings\n'
                f'- {len(reviews)} reviews'
            )
        )
    
    def create_users(self, count):
        """Create sample users"""
        users = []
        user_data = [
            {'username': 'john_doe', 'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com'},
            {'username': 'jane_smith', 'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane@example.com'},
            {'username': 'bob_wilson', 'first_name': 'Bob', 'last_name': 'Wilson', 'email': 'bob@example.com'},
            {'username': 'alice_johnson', 'first_name': 'Alice', 'last_name': 'Johnson', 'email': 'alice@example.com'},
            {'username': 'charlie_brown', 'first_name': 'Charlie', 'last_name': 'Brown', 'email': 'charlie@example.com'},
            {'username': 'diana_davis', 'first_name': 'Diana', 'last_name': 'Davis', 'email': 'diana@example.com'},
            {'username': 'frank_miller', 'first_name': 'Frank', 'last_name': 'Miller', 'email': 'frank@example.com'},
            {'username': 'grace_taylor', 'first_name': 'Grace', 'last_name': 'Taylor', 'email': 'grace@example.com'},
        ]
        
        for i in range(count):
            if i < len(user_data):
                data = user_data[i]
            else:
                data = {
                    'username': f'user_{i+1}',
                    'first_name': f'User{i+1}',
                    'last_name': f'Test{i+1}',
                    'email': f'user{i+1}@example.com'
                }
            
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'email': data['email'],
                    'password': 'pbkdf2_sha256$260000$dummy$dummy'
                }
            )
            users.append(user)
            
            if created:
                self.stdout.write(f'  Created user: {user.username}')
        
        return users
    
    def create_listings(self, count, users):
        """Create sample listings"""
        listings = []
        sample_listings = [
            {
                'title': 'Cozy Downtown Apartment',
                'description': 'Beautiful apartment in the heart of the city with modern amenities.',
                'property_type': 'apartment',
                'location': '123 Main Street',
                'city': 'New York',
                'state': 'NY',
                'country': 'USA',
                'bedrooms': 2,
                'bathrooms': 1,
                'max_guests': 4,
                'price_per_night': Decimal('120.00'),
                'amenities': 'WiFi, Kitchen, Air Conditioning, Heating'
            },
            {
                'title': 'Luxury Beach House',
                'description': 'Stunning oceanfront property with private beach access.',
                'property_type': 'house',
                'location': '456 Ocean Drive',
                'city': 'Miami',
                'state': 'FL',
                'country': 'USA',
                'bedrooms': 4,
                'bathrooms': 3,
                'max_guests': 8,
                'price_per_night': Decimal('350.00'),
                'amenities': 'WiFi, Pool, Beach Access, Kitchen, Parking'
            },
            {
                'title': 'Mountain Cabin Retreat',
                'description': 'Peaceful cabin surrounded by nature, perfect for a getaway.',
                'property_type': 'cabin',
                'location': '789 Mountain Road',
                'city': 'Aspen',
                'state': 'CO',
                'country': 'USA',
                'bedrooms': 3,
                'bathrooms': 2,
                'max_guests': 6,
                'price_per_night': Decimal('200.00'),
                'amenities': 'Fireplace, Hiking Trails, Kitchen, Parking'
            },
        ]
        
        for i in range(count):
            data = random.choice(sample_listings)
            listing = Listing.objects.create(
                title=f"{data['title']} #{uuid.uuid4().hex[:4]}",
                description=data['description'],
                property_type=data['property_type'],
                location=data['location'],
                city=data['city'],
                state=data['state'],
                country=data['country'],
                bedrooms=data['bedrooms'],
                bathrooms=data['bathrooms'],
                max_guests=data['max_guests'],
                price_per_night=data['price_per_night'],
                amenities=data['amenities'],
                host=random.choice(users)
            )
            listings.append(listing)
        return listings
    
    def create_bookings(self, count, listings, users):
        """Create sample bookings"""
        bookings = []
        for _ in range(count):
            listing = random.choice(listings)
            user = random.choice(users)
            start_date = date.today() + timedelta(days=random.randint(1, 30))
            end_date = start_date + timedelta(days=random.randint(1, 7))
            booking = Booking.objects.create(
                listing=listing,
                user=user,
                start_date=start_date,
                end_date=end_date,
                guests=random.randint(1, listing.max_guests)
            )
            bookings.append(booking)
        return bookings
    
    def create_reviews(self, count, listings, users, bookings):
        """Create sample reviews"""
        reviews = []
        sample_texts = [
            'Amazing stay! Highly recommend.',
            'Very clean and comfortable.',
            'Great location and friendly host.',
            'Would definitely book again.',
            'The property was just as described.',
        ]
        for _ in range(count):
            listing = random.choice(listings)
            user = random.choice(users)
            text = random.choice(sample_texts)
            rating = random.randint(3, 5)
            review = Review.objects.create(
                listing=listing,
                user=user,
                rating=rating,
                comment=text,
                booking=random.choice(bookings) if bookings else None
            )
            reviews.append(review)
        return reviews
