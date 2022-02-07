from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from . import views
from .views import GetImdbMovies

urlpatterns = [
    path('index/', views.index, name='index'),
    path('hello/', views.HelloView.as_view(), name='hello'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('search_movies/', GetImdbMovies.as_view(), name='search_movies')
]
