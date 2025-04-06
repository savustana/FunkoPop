from rest_framework import serializers
from .models import Stuff, User

class FunkoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stuff
        fields = ('collection', 'title', 'price', 'description', 'image', 'category', 'stock', 'series')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_staff')