from django.views import generic
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View
from django.template import loader
from django.http import HttpResponse
from .forms import LogInForm, SignUpForm
from .models import Movie


class MainView(generic.ListView):
    template_name = 'website/home.html'

    def get_queryset(self):
        return Movie.objects.all()

class DetailView(generic.DetailView):
    model = Movie
    template_name = 'website/detail.html'

class LogInView(View):
    form_class = LogInForm
    template_name = 'website/login_form.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(reverse('Ebooking:home'))
        return render(request, self.template_name, {'form':form})

class SignUpView(View):
    form_class = SignUpForm
    template_name = 'website/signup_form.html'
    
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            username = request.POST['username']
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']
            if password == confirm_password:
                user.set_password(password)
                user.save()
                user = authenticate(username=username, password=password)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return redirect(reverse('Ebooking:home'))
        return render(request, self.template_name, {'form':form})
     
def logoutFunc(request):
    logout(request)
    return redirect(reverse('Ebooking:index'))
