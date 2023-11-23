from celery import shared_task
from django.core.mail import send_mail
from .models import Order

@shared_task
def send_payment_reminder_email(order_id):
    order = Order.objects.get(id=order_id)

    send_mail(
        'Payment Reminder',
        'Your payment is due tomorrow.',
        'from@example.com',
        [order.customer.email],
        fail_silently=False,
    )
