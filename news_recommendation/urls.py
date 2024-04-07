from django.urls import path
from news_recommendation import views


urlpatterns = [
    path("",views.index),
    path("recommend_news/",views.recommend_news),
    path("Login/",views.Login),
    path("Register/",views.Register),
    path("Recommend/",views.RecommendAPI),
    path("fetchUser/",views.getDetails),

]