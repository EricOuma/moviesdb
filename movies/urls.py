from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.home, name='home'),
    path('movies/', views.movie_list, name='movie_list'),
    path('movies/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('tv-shows/', views.tv_show_list, name='tv_show_list'),
    path('tv-shows/<int:tv_show_id>/', views.tv_show_detail, name='tv_show_detail'),
    path('actors/', views.actor_list, name='actor_list'),
    path('actors/<int:actor_id>/', views.actor_detail, name='actor_detail'),
    path('directors/', views.director_list, name='director_list'),
    path('directors/<int:director_id>/', views.director_detail, name='director_detail'),
    path('search/', views.search, name='search'),
]
