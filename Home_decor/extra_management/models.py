from django.db import models

# Create your models here.
class Banner(models.Model):
    # Banner name means -----> Banner Title
    banner_name         = models.CharField(max_length=100)
    banner_name_sub     = models.CharField(max_length=100,blank=True)
    banner_image        = models.ImageField(upload_to='media/banner/images/')
    banner_url          = models.URLField(blank=True,default='#')
    button_text         = models.CharField(max_length=10,default='Buy Now')
    is_active           = models.BooleanField(default=True)
    

    def __str__(self):
        return self.banner_name
