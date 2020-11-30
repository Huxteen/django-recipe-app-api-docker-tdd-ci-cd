from django.urls import path

from users import views

app_name = 'users'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('update/', views.ManageUserView.as_view(), name='update'),
]



