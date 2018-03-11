from django.contrib import admin
from .models import Movie, Actor, ShowTime, Ticket, ShoppingCart, Discount, Order

# Register your models here.
admin.site.register(Movie)
admin.site.register(Actor)
admin.site.register(ShowTime)
admin.site.register(Ticket)
admin.site.register(ShoppingCart)
admin.site.register(Discount)
admin.site.register(Order)
