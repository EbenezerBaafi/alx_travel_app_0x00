# ALX Travel App 0x00 - Database Modeling and Data Seeding

A Django-based travel booking platform with comprehensive database models, API serializers, and data seeding capabilities.

## Features

### Database Models
- **Listing**: Property listings with detailed information, location data, and amenities
- **Booking**: Reservation system with date validation and status tracking
- **Review**: Rating and feedback system with detailed scoring categories

### API Serialization
- **ListingSerializer**: Full listing data with host information and calculated fields
- **BookingSerializer**: Booking management with validation and computed properties
- **ReviewSerializer**: Review handling with user authentication and validation

### Data Seeding
- Management command to populate database with realistic sample data
- Configurable number of users, listings, bookings, and reviews
- Relationship-aware data generation ensuring referential integrity

## Installation

### 1. Clone and Setup
```bash
git clone https://github.com/YOUR_USERNAME/alx_travel_app_0x00.git
cd alx_travel_app_0x00
```

### 2. Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate.bat  # Windows
# or
source venv/bin/activate   # macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Database
DB_NAME=alx_travel_db
DB_USER=your_postgres_username
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432

# Celery Configuration
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
```

### 5. Database Setup
```bash
# Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE alx_travel_db;"

# Run migrations
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

## Usage

### Running the Server
```bash
python manage.py runserver
```

### API Documentation
- **Swagger UI**: http://127.0.0.1:8000/swagger/
- **ReDoc**: http://127.0.0.1:8000/redoc/
- **Admin Panel**: http://127.0.0.1:8000/admin/

### Data Seeding

Populate your database with sample data using the management command:

```bash
# Basic seeding with default amounts
python manage.py seed

# Custom amounts
python manage.py seed --listings 20 --users 10 --bookings 50 --reviews 30

# Clear existing data and seed fresh
python manage.py seed --clear --listings 15 --users 8 --bookings 40 --reviews 25
```

#### Seeding Options:
- `--listings`: Number of property listings to create (default: 10)
- `--users`: Number of users to create (default: 5)
- `--bookings`: Number of bookings to create (default: 20)
- `--reviews`: Number of reviews to create (default: 15)
- `--clear`: Clear existing data before seeding

## API Endpoints

### Listings
- `GET /api/listings/` - List all listings
- `POST /api/listings/` - Create new listing
- `GET /api/listings/{id}/` - Retrieve specific listing
- `PUT /api/listings/{id}/` - Update listing
- `DELETE /api/listings/{id}/` - Delete listing

### Bookings
- `GET /api/bookings/` - List user's bookings
- `POST /api/bookings/` - Create new booking
- `GET /api/bookings/{id}/` - Retrieve specific booking
- `PUT /api/bookings/{id}/` - Update booking
- `DELETE /api/bookings/{id}/` - Cancel booking

### Reviews
- `GET /api/reviews/` - List reviews
- `POST /api/reviews/` - Create new review
- `GET /api/reviews/{id}/` - Retrieve specific review

## Database Schema

### Listing Model
- UUID primary key for security
- Host relationship (Foreign Key to User)
- Property details (type, bedrooms, bathrooms, etc.)
- Location with optional coordinates
- Pricing and availability
- Amenities and descriptions
- Timestamps and calculated fields

### Booking Model
- UUID primary key
- Listing and Guest relationships
- Date range with validation
- Guest count and pricing
- Status tracking (pending, confirmed, cancelled, completed, refunded)
- Special requests and metadata

### Review Model
- UUID primary key
- Listing and Reviewer relationships
- Overall rating (1-5 stars)
- Detailed ratings (cleanliness, communication, location, value)
- Comment and feedback
- Booking relationship (optional)

## Model Features

### Validation
- Date validation (check-out after check-in, no past dates)
- Guest capacity limits
- Rating constraints (1-5 stars)
- Host self-review prevention

### Computed Properties
- Average ratings and review counts for listings
- Booking duration and status checks
- Coordinate validation

### Database Optimization
- Strategic indexing on frequently queried fields
- Database constraints for data integrity
- Efficient relationship queries

## Development

### Project Structure
```
alx_travel_app_0x00/
├── manage.py
├── requirements.txt
├── .env
├── alx_travel_app/          # Django project settings
├── listings/                # Main application
│   ├── models.py           # Database models
│   ├── serializers.py      # API serializers
│   ├── views.py            # API views (to be implemented)
│   └── management/
│       └── commands/
│           └── seed.py     # Data seeding command
└── README.md
```

### Adding More Data
The seeder creates realistic relationships:
- Users are assigned as hosts and guests
- Bookings reference valid listings and users
- Reviews are tied to completed bookings where possible
- Geographic data includes US cities and coordinates

### Customization
The models include extensive help text and validation. Extend the seeder by:
- Adding more sample data arrays
- Including international locations
- Creating seasonal pricing variations
- Adding more property types and amenities

## Technologies Used
- **Django 4.2.7**: Web framework
- **Django REST Framework**: API development
- **PostgreSQL**: Primary database
- **drf-yasg**: Swagger/OpenAPI documentation
- **Celery**: Task queue (configured)
- **django-environ**: Environment variable management

## License
This project is part of the ALX Software Engineering program.

## Contributing
This is an educational project. Feel free to fork and experiment with additional features.