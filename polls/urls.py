from django.urls import path
from . import views
from .views import restaurants_json

app_name = "polls"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    path('list.json', views.response_list_json, name='response_list_json'),
    path('restaurants.json', restaurants_json, name='restaurants_json'),
]