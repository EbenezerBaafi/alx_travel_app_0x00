from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Listing, Booking, Review


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model (for nested representations)
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class ListingSerializer(serializers.ModelSerializer):
    """
    Serializer for Listing model
    """
    host = UserSerializer(read_only=True)
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Listing
        fields = [
            'listing_id',
            'host',
            'title',
            'description',
            'property_type',
            'price_per_night',
            'location',
            'city',
            'state',
            'country',
            'latitude',
            'longitude',
            'bedrooms',
            'bathrooms',
            'max_guests',
            'amenities',
            'is_available',
            'created_at',
            'updated_at',
            'average_rating',
            'review_count',
        ]
        read_only_fields = ['listing_id', 'created_at', 'updated_at', 'average_rating', 'review_count']
    
    def create(self, validated_data):
        """
        Create a new listing with the current user as host
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['host'] = request.user
        return super().create(validated_data)
    
    def validate_price_per_night(self, value):
        """
        Validate that price per night is positive
        """
        if value <= 0:
            raise serializers.ValidationError("Price per night must be greater than 0")
        return value
    
    def validate_max_guests(self, value):
        """
        Validate that max guests is reasonable
        """
        if value <= 0:
            raise serializers.ValidationError("Maximum guests must be at least 1")
        if value > 50:
            raise serializers.ValidationError("Maximum guests cannot exceed 50")
        return value


class ListingCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating listings
    """
    class Meta:
        model = Listing
        fields = [
            'title',
            'description',
            'property_type',
            'price_per_night',
            'location',
            'city',
            'state',
            'country',
            'latitude',
            'longitude',
            'bedrooms',
            'bathrooms',
            'max_guests',
            'amenities',
            'is_available',
        ]
    
    def create(self, validated_data):
        """
        Create a new listing with the current user as host
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['host'] = request.user
        return super().create(validated_data)


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking model
    """
    guest = UserSerializer(read_only=True)
    listing = ListingSerializer(read_only=True)
    listing_id = serializers.UUIDField(write_only=True)
    duration_nights = serializers.ReadOnlyField()
    is_past_checkout = serializers.ReadOnlyField()
    
    class Meta:
        model = Booking
        fields = [
            'booking_id',
            'listing',
            'listing_id',
            'guest',
            'check_in_date',
            'check_out_date',
            'num_guests',
            'total_price',
            'status',
            'special_requests',
            'created_at',
            'updated_at',
            'duration_nights',
            'is_past_checkout',
        ]
        read_only_fields = ['booking_id', 'created_at', 'updated_at', 'duration_nights', 'is_past_checkout']
    
    def create(self, validated_data):
        """
        Create a new booking with the current user as guest
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['guest'] = request.user
        
        # Get the listing from listing_id
        listing_id = validated_data.pop('listing_id')
        try:
            listing = Listing.objects.get(listing_id=listing_id)
            validated_data['listing'] = listing
        except Listing.DoesNotExist:
            raise serializers.ValidationError("Invalid listing ID")
        
        return super().create(validated_data)
    
    def validate(self, data):
        """
        Validate booking dates and guest count
        """
        check_in_date = data.get('check_in_date')
        check_out_date = data.get('check_out_date')
        num_guests = data.get('num_guests')
        listing_id = data.get('listing_id')
        
        # Validate dates
        if check_in_date and check_out_date:
            if check_out_date <= check_in_date:
                raise serializers.ValidationError("Check-out date must be after check-in date")
            
            from django.utils import timezone
            if check_in_date < timezone.now().date():
                raise serializers.ValidationError("Check-in date cannot be in the past")
        
        # Validate guest count against listing capacity
        if listing_id and num_guests:
            try:
                listing = Listing.objects.get(listing_id=listing_id)
                if num_guests > listing.max_guests:
                    raise serializers.ValidationError(
                        f"Number of guests ({num_guests}) exceeds listing capacity ({listing.max_guests})"
                    )
            except Listing.DoesNotExist:
                raise serializers.ValidationError("Invalid listing ID")
        
        # Check if listing is available
        if listing_id:
            try:
                listing = Listing.objects.get(listing_id=listing_id)
                if not listing.is_available:
                    raise serializers.ValidationError("This listing is not currently available for booking")
            except Listing.DoesNotExist:
                raise serializers.ValidationError("Invalid listing ID")
        
        return data
    
    def validate_total_price(self, value):
        """
        Validate that total price is positive
        """
        if value <= 0:
            raise serializers.ValidationError("Total price must be greater than 0")
        return value
    
    def validate_num_guests(self, value):
        """
        Validate that number of guests is reasonable
        """
        if value <= 0:
            raise serializers.ValidationError("Number of guests must be at least 1")
        return value


class BookingCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating bookings
    """
    listing_id = serializers.UUIDField()
    
    class Meta:
        model = Booking
        fields = [
            'listing_id',
            'check_in_date',
            'check_out_date',
            'num_guests',
            'total_price',
            'special_requests',
        ]
    
    def create(self, validated_data):
        """
        Create a new booking with the current user as guest
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['guest'] = request.user
        
        # Get the listing from listing_id
        listing_id = validated_data.pop('listing_id')
        try:
            listing = Listing.objects.get(listing_id=listing_id)
            validated_data['listing'] = listing
        except Listing.DoesNotExist:
            raise serializers.ValidationError("Invalid listing ID")
        
        return super().create(validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review model
    """
    reviewer = UserSerializer(read_only=True)
    listing = ListingSerializer(read_only=True)
    listing_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Review
        fields = [
            'review_id',
            'listing',
            'listing_id',
            'reviewer',
            'booking',
            'rating',
            'comment',
            'cleanliness_rating',
            'communication_rating',
            'location_rating',
            'value_rating',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['review_id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """
        Create a new review with the current user as reviewer
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['reviewer'] = request.user
        
        # Get the listing from listing_id
        listing_id = validated_data.pop('listing_id')
        try:
            listing = Listing.objects.get(listing_id=listing_id)
            validated_data['listing'] = listing
        except Listing.DoesNotExist:
            raise serializers.ValidationError("Invalid listing ID")
        
        return super().create(validated_data)
    
    def validate_rating(self, value):
        """
        Validate that rating is between 1 and 5
        """
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    
    def validate(self, data):
        """
        Validate that reviewer is not the host
        """
        listing_id = data.get('listing_id')
        request = self.context.get('request')
        
        if listing_id and request and hasattr(request, 'user'):
            try:
                listing = Listing.objects.get(listing_id=listing_id)
                if request.user == listing.host:
                    raise serializers.ValidationError("Hosts cannot review their own listings")
            except Listing.DoesNotExist:
                raise serializers.ValidationError("Invalid listing ID")
        
        return data