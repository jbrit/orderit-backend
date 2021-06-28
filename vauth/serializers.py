from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password


User = get_user_model()

class RegisterUserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    
    def validate_confirm_password(self, value):
        """
        Check that the passwords are the same.
        """
        data = self.initial_data
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("The passwords don't match")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['email'], validated_data['password'])
        return user
    
    class Meta:
        model = User
        fields = ['email','password', 'confirm_password']