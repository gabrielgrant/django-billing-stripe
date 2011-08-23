from datetime import date
import sys

from django.db import models
from django.conf import settings

import stripe

#from billing.models import Account
from billing.processor.stripe import validators

class ConfigurationError(RuntimeError):
    pass

if getattr(settings, 'STRIPE_LIVE_MODE', False):
    try:
        STRIPE_SECRET_API_KEY = settings.STRIPE_LIVE_SECRET_API_KEY
    except AttributeError:
        raise ConfigurationError,  \
            "STIRPE_LIVE_MODE is True, but STRIPE_LIVE_SECRET_API_KEY isn't provided.",  \
            sys.exc_info()[2]
    try:
        STRIPE_PUBLIC_API_KEY = settings.STRIPE_LIVE_PUBLIC_API_KEY
    except AttributeError:
        raise ConfigurationError,  \
            "STIRPE_LIVE_MODE is True, but STRIPE_LIVE_PUBLIC_API_KEY isn't provided.",  \
            sys.exc_info()[2]
else:
    try:
        STRIPE_SECRET_API_KEY = settings.STRIPE_TEST_SECRET_API_KEY
    except AttributeError:
        raise ConfigurationError,  \
            "STIRPE_LIVE_MODE is False, but STRIPE_TEST_SECRET_API_KEY isn't provided.",  \
            sys.exc_info()[2]
    try:
        STRIPE_PUBLIC_API_KEY = settings.STRIPE_TEST_PUBLIC_API_KEY
    except AttributeError:
        raise ConfigurationError,  \
            "STIRPE_LIVE_MODE is False, but STRIPE_TEST_PUBLIC_API_KEY isn't provided.",  \
            sys.exc_info()[2]

stripe.api_key = STRIPE_SECRET_API_KEY


CARD_TYPES = (
    'Visa', 'MasterCard', 'American Express', 'Discover', 'JCB', 'Diners Club'
)
class CardManager(models.Manager):
    def create_from_stripe_object(self, stripe_card, customer, commit=True):
        card = self.model(
            type=stripe_card.type,
            country=stripe_card.country,
            last4=stripe_card.last4,
            exp_year=stripe_card.exp_year,
            exp_month=stripe_card.exp_month,
            customer=customer,
        )
        if commit:
            card.save()
        return card
    

class Card(models.Model):
    objects = CardManager()
    #stripe_id = models.CharField(max_length=32, unique=True),
    type = models.CharField(
        'Card Type (Visa, MasterCard, etc.)',
        max_length=100,
        choices=zip(CARD_TYPES, CARD_TYPES),
    )
    country = models.CharField(max_length=2)
    last4 = models.CharField(max_length=4, validators=[validators.last4])
    exp_year = models.IntegerField(validators=[validators.exp_year])
    exp_month = models.IntegerField(validators=[validators.exp_month])
    date_created = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey('Customer', related_name='cards')
    def get_expiry_date(self):
        return date(self.exp_year, self.exp_month, 1)
    class Meta:
        get_latest_by = 'date_created'
        ordering = ['-date_created']

class CustomerManager(models.Manager):
    def create_customer(self, card, billing_account, commit=True):
        """
        Creates a Stripe customer linked to the given billing account
        """
        stripe_customer = stripe.Customer.create(
            card=card,
            email=billing_account.owner.email,
            description='account_%s' % billing_account.id,
        )
        return self.create_from_stripe_object(stripe_customer, billing_account, commit=commit)
    
    def create_from_stripe_object(self, stripe_customer, billing_account, commit=True):
        customer = self.model(
            stripe_id=stripe_customer.id,
            description=stripe_customer.description,
            livemode=stripe_customer.livemode,
            billing_account=billing_account,
        )
        if commit:
            customer.save()
        stripe_card = stripe_customer.active_card
        try:
            card = Card.objects.create_from_stripe_object(stripe_card, customer, commit=commit)
        except:
            print stripe_card
        if not commit:
            customer._enqueue_card_for_save(card)
        return customer
        

class Customer(models.Model):
    objects = CustomerManager()
    stripe_id = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=200)
    livemode = models.BooleanField()
    date_created = models.DateTimeField(auto_now_add=True)
    billing_account = models.OneToOneField('billing.Account', related_name='stripe_customer')
    @property
    def active_card(self):
        return self.cards.objects.latest()
    def update_active_card(self, card, commit=True):
        stripe_customer = self.fetch_customer()
        stripe_customer.card = card
        stripe_customer.save()
        card = Card.objects.create_from_stripe_object(
            stripe_customer.active_card, customer=self, commit=commit)
        if not commit:
            self._enqueue_card_for_save(card)
        return card
    def fetch_customer(self):
        return stripe.Customer.retrieve(self.stripe_id)
    def _enqueue_card_for_save(self, card):
        if hasattr(self, '_unsaved_cards'):
            self._unsaved_cards.apend(card)
        else:
            self._unsaved_cards = [card]
    def save(self):
        ret = super(Customer, self).save()
        for c in getattr(self, '_unsaved_cards', []):
            c.save()
        self._unsaved_cards = []
        return ret

def has_valid_billing_details(account):
    try:
        customer = account.stripe_customer
    except Customer.DoesNotExist:
        return False
    today = date.today()
    exp_date = customer.cards.latest().get_expiry_date()
    return today < exp_date
"""
{
  "object": "customer",
  "description": "g@briel.ca",
  "livemode": false,
  "created": 1309622137,
  "active_card": {
    "type": "Visa",
    "object": "card",
    "country": "US",
    "exp_month": 7,
    "last4": "4242",
    "id": "cc_lpPNXWQOj2",
    "exp_year": 2012
  },
  "id": "cu_RFc2UB8qxR"
}
  
{
      "object": "customer",
      "description": "my_first_charge",
      "livemode": false,
      "created": 1305974416,
      "active_card": {
        "type": "Visa",
        "object": "card",
        "country": "US",
        "exp_month": 5,
        "last4": "4242",
        "id": "cc_f2jWdtB2GK",
        "exp_year": 2012
      },
      "subscription": {
        "current_period_end": 1306060846,
        "status": "trialing",
        "plan": {
          "interval": "month",
          "amount": 1000,
          "trial_period_days": 0,
          "object": "plan",
          "identifier": "Basic"
        },
        "current_period_start": 1305974416,
        "start": 1305974416,
        "object": "subscription",
        "trial_start": 1305974416,
        "trial_end": 1306060846,
        "customer": "O8ygDbcWW9aswmxctU9z",
      },
      "id": "O8ygDbcWW9aswmxctU9z"

  
}

"""
