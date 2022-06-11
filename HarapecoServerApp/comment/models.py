from django.db import models

# Create your models here.
class Comment(models.Model):
    text = models.TextField(max_length=5000)
    user = models.ForeignKey("app.User", on_delete=models.CASCADE)

 