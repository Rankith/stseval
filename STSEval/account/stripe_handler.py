import stripe
from management.models import Session
from account.models import Purchase
from datetime import datetime
from django.conf import settings
from .models import User
import decimal

def get_customer_cards(user):
    if settings.STRIPE_TEST_MODE:
        stripe.api_key = settings.STRIPE_API_KEY_TEST
    else:
        stripe.api_key = settings.STRIPE_API_KEY
    methods = stripe.PaymentMethod.list(customer=user.stripe_customer,type="card")

    return methods.data

def create_connect_account():
    if settings.STRIPE_TEST_MODE:
        stripe.api_key = settings.STRIPE_API_KEY_TEST
    else:
        stripe.api_key = settings.STRIPE_API_KEY
    account = stripe.Account.create(
              type='express',
              capabilities={
                'transfers': {
                  'requested': True,
                },
              },
            )

    return account.id

def get_account_link(user,session_id):
    if settings.STRIPE_TEST_MODE:
        stripe.api_key = settings.STRIPE_API_KEY_TEST
        if session_id != 0:
            return_url = 'https://stslivegym.com/management/setup_finish/' + str(session_id)
        else:
            return_url = 'https://stslivegym.com/account/payments/'
        account_links = stripe.AccountLink.create(
          account=user.stripe_connect_account,
          refresh_url='https://stslivegym.com/account/stripe_connect_account/',
          return_url=return_url,
          type='account_onboarding',
        )
    else:
        stripe.api_key = settings.STRIPE_API_KEY
        if session_id != 0:
            return_url = 'https://stslivegym.com/management/setup_finish/' + str(session_id)
        else:
            return_url = 'https://stslivegym.com/account/payments/'
        account_links = stripe.AccountLink.create(
          account=user.stripe_connect_account,
          refresh_url='https://stslivegym.com/account/stripe_connect_account/',
          return_url=return_url,
          type='account_onboarding',
        )
   

    return account_links.url

def get_dashboard_link(user):
    if settings.STRIPE_TEST_MODE:
        stripe.api_key = settings.STRIPE_API_KEY_TEST
    else:
        stripe.api_key = settings.STRIPE_API_KEY
    login_link = stripe.Account.create_login_link(user.stripe_connect_account)

    return login_link.url

def check_account_status(user):
    if settings.STRIPE_TEST_MODE:
        stripe.api_key = settings.STRIPE_API_KEY_TEST
    else:
        stripe.api_key = settings.STRIPE_API_KEY
    if user.stripe_connect_account != '':
        account = stripe.Account.retrieve(user.stripe_connect_account)
        if not account.details_submitted:
            return "details"
        else:
            if not account.payouts_enabled:
                return "payouts"
            else:
                return "complete"
    else:
        return "none"

def get_connect_account(user):
    if settings.STRIPE_TEST_MODE:
        stripe.api_key = settings.STRIPE_API_KEY_TEST
    else:
        stripe.api_key = settings.STRIPE_API_KEY
    if user.stripe_connect_account != '':
        account = stripe.Account.retrieve(user.stripe_connect_account)
        return account

    return None

def create_intent(user,session,type,amount,quantity):
    if settings.STRIPE_TEST_MODE:
        stripe.api_key = settings.STRIPE_API_KEY_TEST
    else:
        stripe.api_key = settings.STRIPE_API_KEY
    total = int(amount*quantity*100)#this is because stripe payments are in cents
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
                    'our_fee':0,
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
                    'our_fee':0,
                    },
                )
    elif type == Purchase.SPECTATOR:
        #spectator so calc our fee and split it out in the intent
        total_for_calc = amount*quantity
        our_fee = settings.OUR_FEE/100
        our_fee = float(total_for_calc)*our_fee
        if our_fee < settings.SPECTATOR_MINIMUM:
            our_fee = settings.SPECTATOR_MINIMUM
        our_fee = round(our_fee,2)
        our_fee = int(our_fee*100)#stripe uses pennies
        description = str(session.full_name()) + " Spectator Access"
        intent = stripe.PaymentIntent.create(
                amount=total,
                currency='usd',
                customer=user.stripe_customer,
                description=description,
                application_fee_amount=our_fee,
                transfer_data={
                    'destination': session.competition.admin.stripe_connect_account,
                    },
                metadata={
                    'type': type,
                    'session_id': session.id,
                    'individual_amount': amount,
                    'quantity': quantity,
                    'user':user.id,
                    'our_fee':our_fee/100,
                    },
                )
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
                    'our_fee':0,
                    },
                )
    elif type == Purchase.SCOREBOARD:
        description = str(session.full_name()) + " Scoreboard Access"
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
                    'our_fee':0,
                    },
                )
   
    return intent.client_secret

