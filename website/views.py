from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.template import loader
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.contrib import messages
from django.db.models.query_utils import Q
from django.http import Http404
from django.contrib.auth.models import User
from django.views import generic
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View
from django.template import loader
from django.http import HttpResponse, JsonResponse
from django.core.mail import EmailMessage
from .forms import LogInForm, SignUpForm, RequestPasswordResetForm, SetPasswordForm
from .models import Movie, ShowTime, Ticket, ShoppingCart, Order
from .tokens import account_activation_token
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
                user.is_active=False
                user.save()
                shoppingcart = ShoppingCart(cart_owner=user)
                shoppingcart.save()
                mail_subject = 'Activate your Ebooking account.'
                message = render_to_string('website/acc_active_email.html', {
                        'user': user,
                        'domain': 'Ebooking',
                        'uid':urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                        'token':account_activation_token.make_token(user),
                        })
                to_email = form.cleaned_data.get('email')
                email = EmailMessage(
                    mail_subject, message, to=[to_email]
                    )
                email.send()
                return redirect(reverse('Ebooking:checkEmail'))
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

def updateProfile(request):
    user = request.user
    user.username = request.POST.get('username')
    user.save()
    request.user = user
    return redirect(reverse('Ebooking:home'))


class ResetPasswordRequestView(generic.FormView):
    template_name = "website/password_request_template.html" 
    success_url = 'login'
    form_class = RequestPasswordResetForm
    
    @staticmethod
    def validate_email_address(email):
        '''
        This method here validates the if the input is an email address or not. Its return type is boolean, True if the input is a email address or False if its not.
        '''
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False
        
    def post(self, request, *args, **kwargs):
        '''
        A normal post request which takes input from field "email_or_username" (in ResetPasswordRequestForm). 
        '''
        form = self.form_class(request.POST)
        if form.is_valid():
            data= form.cleaned_data["email_or_username"]
            if self.validate_email_address(data) is True:                 #uses the method written above
                '''
                If the input is an valid email address, then the following code will lookup for users associated with that email address. If found then an email will be sent to the address, else an error
                message will be printed on the screen.
                '''
                associated_users= User.objects.filter(Q(email=data)|Q(username=data))
                if associated_users.exists():
                    for user in associated_users:
                        c = {
                            'email': user.email,
                            'domain': request.META['HTTP_HOST'],
                            'site_name': 'Ebooking',
                            'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                            'user': user,
                            'token': default_token_generator.make_token(user),
                            'protocol': 'http',
                            }
                        subject_template_name='website/password_reset_subject.txt' 
                            # copied from django/contrib/admin/templates/registration/password_reset_subject.txt to templates directory
                        email_template_name='website/password_reset_email.html'    
                            # copied from django/contrib/admin/templates/registration/password_reset_email.html to templates directory
                        subject = loader.render_to_string(subject_template_name, c)
                            # Email subject *must not* contain newlines
                        subject = ''.join(subject.splitlines())
                        email = loader.render_to_string(email_template_name, c)
                        send_mail(subject, email, 'messenger@localhost.com' , [user.email], fail_silently=False)
                        result = self.form_valid(form)
                        messages.success(request, 'An email has been sent to ' + data +". Please check its inbox to continue reseting password.")
                    return result
                result = self.form_invalid(form)
                messages.error(request, 'No user is associated with this email address')
                return result
            else:
                '''
                If the input is an username, then the following code will lookup for users associated with that user. If found then an email will be sent to the user's address, else an error message will
                be printed on the screen.
                '''
                associated_users= User.objects.filter(username=data)
                if associated_users.exists():
                    for user in associated_users:
                        c = {
                            'email': user.email,
                            'domain': 'Ebooking.com', #or your domain
                            'site_name': 'Ebooking',
                            'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                            'user': user,
                            'token': default_token_generator.make_token(user),
                            'protocol': 'http',
                            }
                        subject_template_name='website/password_reset_subject.txt'
                        email_template_name='website/password_reset_email.html'
                        subject = loader.render_to_string(subject_template_name, c)
                        # Email subject *must not* contain newlines
                        subject = ''.join(subject.splitlines())
                        email = loader.render_to_string(email_template_name, c)
                        send_mail(subject, email, 'messenger@localhost.com' , [user.email], fail_silently=False)
                        result = self.form_valid(form)
                        messages.success(request, 'Email has been sent to ' + data +"'s email address. Please check its inbox to continue reseting password.")
                    return result
            result = self.form_invalid(form)
            messages.error(request, 'This username does not exist in the system.')
            return result
        messages.error(request, 'Invalid Input')
        return self.form_invalid(form)
    
class PasswordResetConfirmView(generic.FormView):
    template_name = "website/password_request_template.html"
    success_url = 'login'
    form_class = SetPasswordForm

    def post(self, request, uidb64=None, token=None, *arg, **kwargs):
        """
        View that checks the hash in a password reset link and presents a
        form for entering a new password.
        """
        UserModel = get_user_model()
        form = self.form_class(request.POST)
        assert uidb64 is not None and token is not None  # checked by URLconf
        try:
            print(uidb64[0:2])
            uid = urlsafe_base64_decode(uidb64[0:uidb64.find('-')])
            user = UserModel._default_manager.get(id=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None
        print(token)
        if user is not None:# and default_token_generator.check_token(user, token):
            print("here")
            if form.is_valid():
                new_password= form.cleaned_data['new_password2']
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password has been reset.')
                return self.form_valid(form)
            else:
                messages.error(request, 'Password reset has not been unsuccessful.')
                return self.form_invalid(form)
        else:
            messages.error(request,'The reset password link is no longer valid.')
            return self.form_invalid(form)

def login2(request):
    return redirect(reverse('Ebooking:login'))

def login3(request, uidb64, token):
    return redirect(reverse('Ebooking:login'))

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64[0:uidb64.find('-')]))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None: # and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return render(request, 'website/successactivate.html')
    else:
        return render(request, 'website/failactivate.html')
