from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from PIL import Image
from .tasks import send_payment_reminder_email
import os


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    merchant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    thumbnail = models.ImageField(upload_to='product_thumbnails/', blank=True, null=True)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if self.image and is_new:
            self.generate_thumbnail()

    def get_thumbnail_path(self):
        base, ext = os.path.splitext(self.image.path)
        return f'{base}_thumbnail{ext}'

    def create_thumbnail_filename(self):
        base, ext = os.path.splitext(self.image.name)
        return f'{base}_thumbnail{ext}'

    def generate_thumbnail(self):
        try:
            img = Image.open(self.image.path)
            if img.width > 200:
                # Calculate the new height to maintain the aspect ratio
                ratio = (200.0 / img.width)
                new_height = int(img.height * ratio)

                output_size = (200, new_height)
                img.thumbnail(output_size, Image.ANTIALIAS)
                thumb_path = self.get_thumbnail_path()
                img.save(thumb_path)

                # Update the thumbnail field
                self.thumbnail = self.create_thumbnail_filename()
                self.save(update_fields=['thumbnail'])
        except IOError:
            print("Error in generating thumbnail for", self.image.path)

    def __str__(self):
        return self.name

class Order(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    delivery_address = models.CharField(max_length=255)
    order_date = models.DateTimeField(auto_now_add=True)
    payment_due = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if not self.id:
            if not self.order_date:
                self.order_date = timezone.now()
            self.payment_due = self.order_date + timedelta(days=5)
            if self._state.adding:
                reminder_time = self.payment_due - timedelta(days=1)
                send_payment_reminder_email.apply_async((self.id,), eta=reminder_time)
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"
