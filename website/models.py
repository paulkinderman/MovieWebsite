from django.db import models
from django.contrib.auth.models import User
import decimal 
from django.utils import timezone
# Create your models here.

class Movie(models.Model):
    movie_title = models.CharField(max_length=100)
    movie_producer = models.CharField(max_length=50)
    movie_director = models.CharField(max_length=50)
    movie_synopsis = models.CharField(max_length=1000)
    movie_picture = models.FileField(upload_to='media/')
    def __str__(self):
        return self.movie_title

class Actor(models.Model):
    movies = models.ManyToManyField(Movie)
    actor_name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.actor_name        

class ShowTime(models.Model):
    time = models.DateTimeField()
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.time) + ' - ' +  self.movie.movie_title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method.
        self.create_tickets()

    def create_tickets(self):
        for x in range (1,10):
            for y in range (1,10):
                ticket = Ticket(showtime=self, row=x, seat=y)
                ticket.save()

class ShoppingCart(models.Model):
    cart_owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.cart_owner.email + "'s Cart: " + str(self.subtotal)

    def set_subtotal(self):
        tickets = Ticket.objects.filter(cart=self.pk)
        total = decimal.Decimal(0.0)
        for ticket in tickets:
            total = total + ticket.price
        self.subtotal = total
        self.save()

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    order_time = models.DateTimeField(default=timezone.now)
    order_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.user.email + "'s Order at " + str(self.order_time)

    def setprice(self, price):
        self.total_price = price
        self.save()

class Ticket(models.Model):
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE, null=True)
    showtime = models.ForeignKey(ShowTime, on_delete=models.CASCADE)
    row = models.IntegerField()
    seat = models.IntegerField()
    available = models.BooleanField(default=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    type = models.CharField(
        default='NA',
        max_length=10,
    )
    price = models.DecimalField(default=5.50, max_digits=10, decimal_places=2)
    
    def __str__(self):
        return str(self.row) + str(self.seat) + ' - ' + self.showtime.movie.movie_title + ' - ' + str(self.showtime.time) + ' - ' + str(self.available)


