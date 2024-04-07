import json
from django.http import HttpResponse
import pandas as pd
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rest_framework.decorators import api_view
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from knox.models import AuthToken
from rest_framework.authtoken.serializers import AuthTokenSerializer
from .serializers import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from rest_framework.permissions import IsAuthenticated


def load_news_data():
    try:
        response = requests.get('https://newsapi.org/v2/everything?sources=the-times-of-india&apiKey=f920a5d9981e42de91c052c8471db7a2')
        if response.status_code == 200:
            news_data = response.json()['articles']
            df = pd.DataFrame(news_data)[['title', 'description', 'url', 'publishedAt','urlToImage']]
            df['tags'] = df['title'] + df['description']
            df['tags'] = df['tags'].apply(lambda x: x.lower())
            return df
        else:
            raise Exception(response.text)
    except Exception as e:
        raise e
    
def recommend_articles(user_activities, num_recommendations=10):
    try:
        df = load_news_data()

        # Initialize TF-IDF vectorizer
        tfidf_vectorizer = TfidfVectorizer(max_features=1689, stop_words='english')
        tfidf_matrix = tfidf_vectorizer.fit_transform(df['tags'])
        # Combine the user's activities into a single string
        user_activity_text = ' '.join(user_activities)

        # Transform the user's activity using the same TF-IDF vectorizer
        user_profile = tfidf_vectorizer.transform([user_activity_text])

        # Calculate similarity between user profile and all articles
        cosine_scores = cosine_similarity(user_profile, tfidf_matrix)

        # Get indices of articles sorted by similarity score
        article_indices = cosine_scores.argsort()[0][::-1]

        # Recommend top num_recommendations articles
        recommended_articles = df.iloc[article_indices[:num_recommendations]]

        # Create a DataFrame with titles and links
        recommended_df = recommended_articles[['title', 'url', 'description', 'publishedAt','urlToImage']]
        return recommended_df.to_dict(orient='records')
    except Exception as e:
        raise e

# Create your views here.

def index(request):
    return HttpResponse("Welcome to index")

@api_view(['POST'])
def Login(request):
    serializer=AuthTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    print("Request Data:", request.data)
    user=serializer.validated_data['user']
    print("User:", user)
    # print("Hello world")
    
    _,token=AuthToken.objects.create(user)
    
    return Response({'user_info': user.pk,"token":token})

@api_view(["POST"])
def Register(request):
    serializer=RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    # user=serializer.validated_data['user']
    email = serializer.validated_data['email']
    # print(email)
    email_exists=User.objects.filter(email=email).exists()
    # username = serializer.validated_data['username']
    if email_exists:
        return Response({"Error": "User's email already exists"},status=status.HTTP_400_BAD_REQUEST)
    # username_exists = User.objects.filter(username=username).exists()
    # if username_exists:
    #     return Response({"Error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
    user=serializer.save()
    userdetails=userDetailsSerializer(data={'user':user.pk,"topic":request.data["topic"]})
    if userdetails.is_valid():
        userdetails.save()
        _,token=AuthToken.objects.create(user)
        return Response({'user_info': user.pk,"token":token},status=status.HTTP_201_CREATED,)
    else :
        user.delete()
        return Response({"error":"User not created"})
    
@api_view(["POST"])
@csrf_exempt
def recommend_news(request):
    if request.method == 'POST':
        # data = json.loads(request.body)
        data = json.loads(request.body)
        print(type(data))
        # print(data)
        user_activities = data
        print(type(user_activities))
        print(user_activities)
        # user_activities = request.POST.getlist("user_activities")
        # user_activities = request.getlist('user_activities[]',[])
        # print(type(user_activities))
        # print("--> this was my list",user_activities)
        if not user_activities:
            return HttpResponseBadRequest("User activities are required.")
        try:
            recommendations = recommend_articles(user_activities)
            return JsonResponse(recommendations, safe=False)
        except Exception as e:
            return HttpResponseServerError(str(e))
    else:
        return HttpResponseBadRequest("Invalid request method.")
    

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def RecommendAPI(request):
    user=request.user.pk
    title=request.data["title"]
    desc=request.data["desc"]
    titleList=[]
    serializer=RecommendSerializer(data={"user": user,},partial=True)
    if serializer.is_valid():
        ac=serializer.save()
        
        for i in range(len(title)):
            serail=TitleSerializer(data={"title":title[i],"desc":desc[i]})
            if serail.is_valid(raise_exception=True):
                titleData=serail.save()
                titleList.append(titleData.pk)
            else:
                return Response({"error":"Error"})
        titledetails=Title.objects.filter(id__in=titleList)
        recomm=Recommend.objects.get(id=ac.pk)
        recomm.title.add(*titledetails)
        recomm.save()
        return Response({"success":"Successfully created"})
                
    else:
        return Response({"error":"Error"})
@api_view(["GET"])
@permission_classes([IsAuthenticated]) 
def getDetails(request):
    user=User.objects.get(id=request.user.pk)
    di={
        "email":user.email,
        
    }
    details=userDetails.objects.get(user_id=request.user.pk)
    di["topic"]=details.topic
    return Response({"details":di})