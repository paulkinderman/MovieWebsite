from django.urls import path
from . import views
from django.views.generic.base import TemplateView

app_name = 'Ebooking'

urlpatterns = [
    path('index/', TemplateView.as_view(template_name='website/index.html'), name='index'),
    path('login/', views.LogInView.as_view(), name='login'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('home/', views.MainView.as_view(), name='home'),
    path('detail/<pk>/', views.DetailView.as_view(), name='detail'),
    path('logout/', views.logoutFunc, name='logout'),
    path('getSeats/', views.getSeats, name='getSeats'),
    path('addToCart/', views.addToCart, name='addToCart'),
    path('viewCart/', views.ViewCart.as_view(), name='viewCart'),
    path('removeTicket/', views.removeTicket, name='removeTicket'),
    path('confirmOrder/', views.confirmOrder, name='confirmOrder'),
    path('myProfile/', views.ViewProfile.as_view(), name='myProfile'),
    path('previousOrders/', views.PreviousOrdersView.as_view(), name='previousOrders'),
    path('orderDetails/<pk>/', views.OrderDetailsView.as_view(), name='orderDetails'),
    path('editProfile/', views.EditProfile.as_view(), name='editProfile'),
    path('updateProfile/', views.updateProfile, name='updateProfile'),
    path('resetPasswordRequest/', views.ResetPasswordRequestView.as_view(), name='resetPasswordRequest'),
    path('resetPasswordRequest/login/', views.login2, name='login2'),
    path('resetPasswordConfirm/<slug:uidb64>-<token>/', views.PasswordResetConfirmView.as_view(), name='reset_password_confirm'),
    path('resetPasswordConfirm/<slug:uidb64>-<token>/login/', views.login3, name='reset_password_confirm_login'),
    path('checkEmail/', TemplateView.as_view(template_name='website/checkEmail.html'), name='checkEmail'),
    path('activate/<slug:uidb64>-<token>/', views.activate, name='activate'),
]
