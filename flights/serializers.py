from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Flight, Booking, Profile


class FlightSerializer(serializers.ModelSerializer):
	class Meta:
		model = Flight
		fields = [ 'destination', 'time', 'price', 'id']


class BookingSerializer(serializers.ModelSerializer):
	flight = serializers.SlugRelatedField(
        read_only=True,
        slug_field='destination'
     )

	class Meta:
		model = Booking
		fields = ['flight', 'date', 'id']


class BookingDetailsSerializer(serializers.ModelSerializer):
	total = serializers.SerializerMethodField()
	flight = FlightSerializer()
	class Meta:
		model = Booking
		fields = ['total', 'flight', 'date', 'passengers', 'id']

	def get_total(self, obj):
		return obj.passengers * obj.flight.price


class AdminUpdateBookingSerializer(serializers.ModelSerializer):
	class Meta:
		model = Booking
		fields = ['date', 'passengers']


class UpdateBookingSerializer(serializers.ModelSerializer):
	class Meta:
		model = Booking
		fields = ['passengers']


class RegisterSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True)
	class Meta:
		model = User
		fields = ['username', 'password', 'first_name', 'last_name']

	def create(self, validated_data):
		username = validated_data['username']
		password = validated_data['password']
		first_name = validated_data['first_name']
		last_name = validated_data['last_name']
		new_user = User(username=username, first_name=first_name, last_name=last_name)
		new_user.set_password(password)
		new_user.save()
		return validated_data


class ProfileSerializer(serializers.ModelSerializer):
	user = serializers.SerializerMethodField()
	past_bookings = serializers.SerializerMethodField()
	tier = serializers.SerializerMethodField()
	class Meta:
		model = Profile
		fields = ['user', 'miles', 'past_bookings','tier']

	def get_user(self, obj):
		return {'first_name' : obj.user.first_name, 'last_name' : obj.user.last_name}

	def get_past_bookings(self, obj):
		booking_obj = obj.user.bookings.filter(date__lt= timezone.now())
		booking_json = BookingSerializer(booking_obj, many=True).data
		return booking_json

	def get_tier(self, obj):
		if 0 <= obj.miles <= 9999:
			return "Blue"
		elif 10000 <= obj.miles <= 59999:
			return "Silver"
		elif 60000 <= obj.miles <= 99999:
			return "Gold"
		elif 100000  <= obj.miles:
			return "Platinum"
