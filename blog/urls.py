from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.list_post, name='list_post'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/',
         views.post_detail, name='post_detail'),
    path('categories/', views.list_categories, name='list_category'),
    path('categories/<str:name>/', views.category_details, name='category_details'),
]