from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class Listing(models.Model):
    """
    Model representing a property listing
    """
    PROPERTY_TYPES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('condo', 'Condo'),
        ('villa', 'Villa'),
        ('studio', 'Studio'),
        ('loft', 'Loft'),
        ('cabin', 'Cabin'),
        ('other', 'Other'),
    ]
    
    listing_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the listing"
    )
    
    host = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='listings',
        help_text="The user who owns this listing"
    )
    
    title = models.CharField(
        max_length=200,
        help_text="Title of the listing"
    )
    
    description = models.TextField(
        help_text="Detailed description of the property"
    )
    
    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPES,
        default='apartment',
        help_text="Type of property"
    )
    
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Price per night in USD"
    )
    
    location = models.CharField(
        max_length=200,
        help_text="Property location/address"
    )
    
    city = models.CharField(
        max_length=100,
        help_text="City where the property is located"
    )
    
    state = models.CharField(
        max_length=100,
        help_text="State/Province where the property is located"
    )
    
    country = models.CharField(
        max_length=100,
        help_text="Country where the property is located"
    )
    
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Latitude coordinate"
    )
    
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Longitude coordinate"
    )
    
    bedrooms = models.PositiveIntegerField(
        default=1,
        help_text="Number of bedrooms"
    )
    
    bathrooms = models.PositiveIntegerField(
        default=1,
        help_text="Number of bathrooms"
    )
    
    max_guests = models.PositiveIntegerField(
        default=2,
        help_text="Maximum number of guests allowed"
    )
    
    amenities = models.TextField(
        blank=True,
        help_text="Comma-separated list of amenities (e.g., WiFi, Pool, Parking)"
    )
    
    is_available = models.BooleanField(
        default=True,
        help_text="Whether the listing is currently available for booking"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the listing was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the listing was last updated"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['city', 'country']),
            models.Index(fields=['property_type']),
            models.Index(fields=['price_per_night']),
            models.Index(fields=['is_available']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.city}, {self.country}"
    
    @property
    def average_rating(self):
        """Calculate the average rating from reviews"""
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    @property
    def review_count(self):
        """Get the total number of reviews"""
        return self.reviews.count()


class Booking(models.Model):
    """
    Model representing a booking for a listing
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('refunded', 'Refunded'),
    ]
    
    booking_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the booking"
    )
    
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text="The listing being booked"
    )
    
    guest = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text="The user making the booking"
    )
    
    check_in_date = models.DateField(
        help_text="Check-in date"
    )
    
    check_out_date = models.DateField(
        help_text="Check-out date"
    )
    
    num_guests = models.PositiveIntegerField(
        default=1,
        help_text="Number of guests"
    )
    
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Total booking price"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the booking"
    )
    
    special_requests = models.TextField(
        blank=True,
        help_text="Any special requests from the guest"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the booking was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the booking was last updated"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['check_in_date', 'check_out_date']),
            models.Index(fields=['status']),
            models.Index(fields=['guest']),
            models.Index(fields=['listing']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_out_date__gt=models.F('check_in_date')),
                name='check_out_after_check_in'
            ),
        ]
    
    def __str__(self):
        return f"Booking {self.booking_id} - {self.listing.title}"
    
    @property
    def duration_nights(self):
        """Calculate the number of nights for this booking"""
        return (self.check_out_date - self.check_in_date).days
    
    @property
    def is_past_checkout(self):
        """Check if the checkout date has passed"""
        return self.check_out_date < timezone.now().date()
    
    def clean(self):
        """Custom validation"""
        from django.core.exceptions import ValidationError
        
        if self.check_in_date and self.check_out_date:
            if self.check_out_date <= self.check_in_date:
                raise ValidationError("Check-out date must be after check-in date")
            
            if self.check_in_date < timezone.now().date():
                raise ValidationError("Check-in date cannot be in the past")
        
        if self.num_guests and self.listing:
            if self.num_guests > self.listing.max_guests:
                raise ValidationError("Number of guests exceeds listing capacity")


class Review(models.Model):
    """
    Model representing a review for a listing
    """
    review_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the review"
    )
    
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="The listing being reviewed"
    )
    
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="The user writing the review"
    )
    
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='review',
        null=True,
        blank=True,
        help_text="The booking associated with this review"
    )
    
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    
    comment = models.TextField(
        help_text="Review comment/feedback"
    )
    
    cleanliness_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Cleanliness rating (1-5)"
    )
    
    communication_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Host communication rating (1-5)"
    )
    
    location_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Location rating (1-5)"
    )
    
    value_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Value for money rating (1-5)"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the review was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the review was last updated"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['rating']),
            models.Index(fields=['listing']),
            models.Index(fields=['reviewer']),
        ]
        constraints = [
            # Ensure a user can only review a listing once per booking
            models.UniqueConstraint(
                fields=['listing', 'reviewer'],
                name='unique_review_per_listing_reviewer'
            ),
        ]
    
    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.listing.title} - {self.rating} stars"
    
    def clean(self):
        """Custom validation"""
        from django.core.exceptions import ValidationError
        
        # Ensure reviewer is not the host of the listing
        if self.reviewer == self.listing.host:
            raise ValidationError("Hosts cannot review their own listings")
        
        # If booking is provided, ensure it matches the listing and reviewer
        if self.booking:
            if self.booking.listing != self.listing:
                raise ValidationError("Booking must be for the same listing")
            if self.booking.guest != self.reviewer:
                raise ValidationError("Review must be by the guest who made the booking")
            if self.booking.status != 'completed':
                raise ValidationError("Can only review completed bookings")