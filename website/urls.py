from django.urls import path
from . import views
from django.views.generic.base import TemplateView

app_name = 'Ebooking'

urlpatterns = [
    path('index/', TemplateView.as_view(template_name='website/index.html'), name='index'),
    path('login/', views.LogInView.as_view(), name='login'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('home/', views.MainView.as_view(), name='home'),
    path('user_main/<pk>/', views.DetailView.as_view(), name='detail'),
    path('logout/', views.logoutFunc, name='logout')
]
