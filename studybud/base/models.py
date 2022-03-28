from django.db import models
from django.contrib.auth.models import User


# la clase sería la tabla, los atributos son las columnas


class Topic(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name

class Room(models.Model): #hijo de Topic
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200,default='')
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants',blank=True) #se usa related_name porque User ya esta usado en la linea host
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True) # a diferencia de auto_now, cuando se guarda sólo queda la fecha de creacion

    class Meta: # esto es para darle orden a los posteos de create_room
        ordering = ['-updated','-created'] # el - es para reversed

    def __str__(self):
        return self.name

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,)
    room = models.ForeignKey(Room, on_delete=models.CASCADE) # cuando borro la DB Room, tmb borra los models hijos (CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta: # esto es para darle orden a los posteos de create_room
        ordering = ['-updated','-created'] # el - es para reversed

    def __str__(self):
        return self.body[0:50] #solo quiero la primer parte del body

