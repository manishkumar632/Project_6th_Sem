from rest_framework import serializers
from decouple import config
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'bio', 'profileImage', 'gender', 'password')
        extra_kwargs = {
            'password': {'write_only': True},  # Ensure the password is write-only
            'bio': {'required': False, 'allow_null': True, 'default': ''},
            'profileImage': {'required': False, 'allow_null': True, 'default': config('DEFAULT_PROFILE_IMAGE')},
            'gender': {'required': False, 'default': 'M'},
        }

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            bio=validated_data.get('bio', ''),
            profileImage=validated_data.get('profileImage', ''),
            gender=validated_data.get('gender', 'M'),
        )
        user.set_password(validated_data['password'])  # Encrypt the password before saving
        user.save()
        return user
