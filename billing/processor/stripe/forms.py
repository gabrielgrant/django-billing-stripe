from django import forms

from billing.processor.stripe.models import Customer, Card
from billing.processor.stripe.widgets import CardNumberInput, CVCInput
from billing.processor.stripe.widgets import ExpirationInput, StripeTokenInput

class BaseBillingDetailsForm(forms.Form):
    name = forms.CharField(label="Cardholder's name")
    card_number = forms.CharField(widget=CardNumberInput, required=False)
    expiration = forms.CharField(widget=ExpirationInput, required=False)
    cvc = forms.CharField(widget=CVCInput, required=False, label='Security code')
    stripe_token = forms.CharField(widget=StripeTokenInput)
    #def __init__(self, billing_account, *args, **kwargs):
    #    super(BaseBillingDetailsForm, self).__init__(*args, **kwargs)
    #    self.billing_account = billing_account
    class Media:
        js = (
            'https://js.stripe.com/v1/',
            'https://ajax.aspnetcdn.com/ajax/jquery.validate/1.8.1/jquery.validate.min.js',
            'stripe/stripe_form.js',
        )

class CustomerCreationForm(BaseBillingDetailsForm):
    """
    A form that creates a validated stripe customer
    """
    def save(self, commit=True):
        # create customer
        customer = Customer.objects.create_customer(
            billing_account=self.billing_account,
            card=self.cleaned_data['stripe_token'],
            commit=commit,
        )
        if commit:
            customer.save()
        return customer

class CustomerUpdateForm(BaseBillingDetailsForm):
    #def __init__(self, stripe_customer, *args, **kwargs):
    #    super(CustomerUpdateForm, self).__init__(*args, **kwargs)
    #    self.stripe_customer = stripe_customer
    def save(self, commit=True):
        customer = self.billing_account.stripe_customer
        token = self.cleaned_data['stripe_token']
        card = customer.update_active_card(token, commit=commit)
        return card

def get_billing_details_form(billing_account):
    """
    If the billing account already has a stripe customer, return the update
    form. If there isn't a customer yet, then return the creation form
    """
    try:
        customer = billing_account.stripe_customer
        return CustomerUpdateForm
    except Customer.DoesNotExist:
        return CustomerCreationForm

