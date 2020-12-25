import stripe
from management.models import Session
from account.models import Purchase
from datetime import datetime
from django.conf import settings
from .models import User

def get_customer_cards(user):
    stripe.api_key = settings.STRIPE_API_KEY
    methods = stripe.PaymentMethod.list(customer=user.stripe_customer,type="card")

    return methods.data

def create_intent(user,session,type,amount,quantity):
    stripe.api_key = settings.STRIPE_API_KEY
    total = amount*quantity*100#this is because stripe payments are in cents
    if type == Purchase.PANEL:
        description = str(session.full_name()) + " Activation"
        if session.payment_intent == '':
            intent = stripe.PaymentIntent.create(
                amount=total,
                currency='usd',
                customer=user.stripe_customer,
                description=description,
                metadata={
                    'type': type,
                    'session_id': session.id,
                    'individual_amount': amount,
                    'quantity': quantity,
                    'user':user.id,
                    },
                )
            session.payment_intent = intent.id
            session.save()
        else:
            intent = stripe.PaymentIntent.modify(
                session.payment_intent,
                amount=total,
                currency='usd',
                customer=user.stripe_customer,
                description=description,
                metadata={
                    'type': type,
                    'session_id': session.id,
                    'individual_amount': amount,
                    'quantity': quantity,
                    'user':user.id,
                    },
                )
    elif type == Purchase.SPECTATOR:
        description = str(session.full_name()) + " Spectate"
    elif type == Purchase.ACCESS_CODE:
        description = str(session.full_name()) + " Access Codes"
        intent = stripe.PaymentIntent.create(
                amount=total,
                currency='usd',
                customer=user.stripe_customer,
                description=description,
                metadata={
                    'type': type,
                    'session_id': session.id,
                    'individual_amount': amount,
                    'quantity': quantity,
                    'user':user.id,
                    },
                )
   
    return intent.client_secret