from django.contrib.auth.hashers import make_password
# from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import *
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    
    class Meta:
        model = User
        fields = ('password', 'email',)
        extra_kwargs = {
            "password": {"write_only": True},
        }
        
    def create(self, validated_data):
        # username = validated_data.get('username')
        password = validated_data.get('password') 
        email = validated_data.get('email') 
       
        
        # Hash the password using make_password
        hashed_password = make_password(password)

        user = User.objects.create(
            username=email,
            password=hashed_password,
            email=email,
           
        )
        return user
    

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    # password = serializers.CharField(write_only=True)
    
class TitleSerializer(serializers.ModelSerializer):
    
     class Meta:
        model=Title
        fields='__all__'
        
class userDetailsSerializer(serializers.ModelSerializer):
    
     class Meta:
        model=userDetails
        fields='__all__'


class RecommendSerializer(serializers.ModelSerializer):
    title = TitleSerializer(read_only=True, many=True)

    class Meta:
        model=Recommend
        fields='__all__'
