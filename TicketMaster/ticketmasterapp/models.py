from django.db import models

class FavoriteEvent(models.Model):
    name = models.CharField(max_length=255)
    image = models.URLField(blank=True)
    date = models.CharField(max_length=100)
    time = models.CharField(max_length=100)
    venue = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    ticket_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
