from django.db import models

# Create your models here.
class Movie(models.Model):
    movie_title = models.CharField(max_length=100)
    movie_producer = models.CharField(max_length=50)
    movie_director = models.CharField(max_length=50)
    movie_synopsis = models.CharField(max_length=1000)

    def __str__(self):
        return self.movie_title

class Actor(models.Model):
    movies = models.ManyToManyField(Movie)
    actor_name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.actor_name

class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    review = models.CharField(max_length=100)
        

class ShowTime(models.Model):
    time = models.DateTimeField()
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

