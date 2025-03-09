from rest_framework import serializers
from .models import FunkoPop, User

class FunkoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FunkoPop
        fields = ('collection', 'title', 'price', 'description', 'image', 'rate')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_staff')