from django.http import Http404
from django.contrib.auth.models import User
from django.views import generic
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View
from django.template import loader
from django.http import HttpResponse, JsonResponse
from .forms import LogInForm, SignUpForm
from .models import Movie, ShowTime, Ticket, ShoppingCart, Order
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt # add this
from django.shortcuts import get_object_or_404
import json
import decimal

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
                shoppingcart = ShoppingCart(cart_owner=user)
                shoppingcart.save()
                user = authenticate(username=username, password=password)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return redirect(reverse('Ebooking:home'))
        return render(request, self.template_name, {'form':form})
     
def logoutFunc(request):
    logout(request)
    return redirect(reverse('Ebooking:index'))

def getSeats(request):
    showtime_string = str(request.GET['showtime'])
    showtime = datetime.strptime(showtime_string+'+0000', "%m %d, %Y, %H:%M+0000")
    movie_title = request.GET['movie']
    movie_object = Movie.objects.get(movie_title=movie_title)
    showtime_object = ShowTime.objects.get(movie=movie_object.pk, time=showtime)
    tickets = Ticket.objects.filter(showtime=showtime_object.pk)
    ticket_list = list(tickets.values('row','seat', 'available'))
    return JsonResponse(ticket_list, safe=False)

@csrf_exempt
def addToCart(request):
    js_tickets = json.loads(request.POST['tickets'])
    showtime = datetime.strptime(str(request.POST['showtime']) + '+0000', "%m %d, %Y, %H:%M+0000")
    movie = request.POST['movie']
    movie_object = Movie.objects.get(movie_title=movie)
    showtime_object = ShowTime.objects.get(movie=movie_object.pk, time=showtime)
    db_tickets = Ticket.objects.filter(showtime=showtime_object.pk)    
    cart = ShoppingCart.objects.get(cart_owner=request.user.id)
    for ticket in js_tickets:
        temp_ticket = db_tickets.filter(row=int(ticket['seatnumber'][:1]), seat=int(ticket['seatnumber'][1:2]))[0]
        temp_ticket.cart = cart
        temp_ticket.available = False
        if ticket['tickettype'] == 'student':
            temp_ticket.type = 'Student'
            temp_ticket.price = decimal.Decimal(5.50)
        if ticket['tickettype'] == 'adult':
            temp_ticket.type = 'Adult'
            temp_ticket.price = decimal.Decimal(7.50)
        if ticket['tickettype'] == 'senior':
            temp_ticket.type = 'Senior'
            temp_ticket.price = decimal.Decimal(4.50)
        temp_ticket.save()
    cart.set_subtotal()
    cart.save()
    return HttpResponse("success")


class ViewCart(generic.DetailView):
    model = ShoppingCart
    template_name = 'website/viewCart.html'
    
    def get_object(self): 
        user = self.request.user
        return ShoppingCart.objects.get(cart_owner=user)
        
@csrf_exempt
def removeTicket(request):
    try:
        cart = ShoppingCart.objects.get(cart_owner=request.user.id)
        ticket = Ticket.objects.get(pk=int(request.POST['id']), cart=cart)
        ticket.cart = None
        ticket.available = True
        ticket.type = 'NA'
        ticket.price = decimal.Decimal(0.00)
        ticket.save()
        cart.set_subtotal()
        cart.save()
        subtotal = cart.subtotal
    except Ticket.DoesNotExist:
        raise Http404
    return HttpResponse(subtotal)

@csrf_exempt
def confirmOrder(request):
    try:
        cart = ShoppingCart.objects.get(cart_owner=request.user)
        tickets = Ticket.objects.filter(cart=cart)
        order = Order(user=request.user, order_price=cart.subtotal)
        order.save()
        for ticket in tickets:
            ticket.order = order
            ticket.cart = None
            ticket.save()
        cart.set_subtotal()
        cart.save()
    except Ticket.DoesNotExist:
        raise Http404
    return HttpResponse("Success")

class ViewProfile(generic.DetailView):
    model = User
    template_name = 'website/myprofile.html'

    def get_object(self):
        return self.request.user


class PreviousOrdersView(generic.ListView):
    template_name = 'website/previousorders.html'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderDetailsView(generic.DetailView):
    model = Order
    template_name = 'website/orderdetail.html'
    
    def get_queryset(self):
#        return get_object_or_404(Order, user=self.request.user, pk=self.kwargs['pk'])
        return Order.objects.filter(user=self.request.user, pk=self.kwargs['pk'])


class EditProfile(generic.edit.UpdateView):
    model = User
    fields = ['username', ]
    template_name = 'website/user_update_form.html'
    
    def get_object(self):
        return User.objects.get(username=self.request.user.username)
