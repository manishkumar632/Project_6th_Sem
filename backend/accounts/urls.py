from django.urls import path
from . import views
from .views import UserRegisterView, UserProfileView, UserLoginView, UserLogoutView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('home/', views.Home, name='home'),
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('logout/', UserLogoutView.as_view(), name='logout'),  # Add this line
]
