from django.urls import path
from django.conf.urls import include, url
from . import views

app_name = 'blog'

urlpatterns = [
    url(r'^$', views.list_post, name='list_post'),
    path('blog/<int:year>/<int:month>/<int:day>/<slug:post>/',
         views.post_detail, name='post_detail'),
    path('categories/', views.list_categories, name='list_category'),
    path('categories/<str:name>/<slug:category>/', views.category_details, name='category_details'),
]