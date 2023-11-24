from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.UserRegisterAPI.as_view()),
    path('login-muid/', views.LoginWithMuid.as_view()),
    path('connect-muid/',views.ConnectWithMuid.as_view()),
    path('qr-code/show/', views.UserQrCodeAPI.as_view()),
    path('qr-code/scan/', views.UserQrCodeScanner.as_view()),
    path('profile/', views.UserProfileAPI.as_view()),


    path('user-treasure/show/', views.TreasureShow.as_view()),
    path('user-treasure/create/', views.UserTreasureAPI.as_view()),
]
