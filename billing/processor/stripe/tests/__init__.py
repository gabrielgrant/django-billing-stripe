#!/usr/bin/env python
from mock import Mock, patch

from django.utils import unittest
from django.test import TestCase

from billing.tests import UserTestCase

from billing.processor.stripe.models import *
from billing.processor.stripe.forms import *

class CustomerTestCase(UserTestCase):
    def setUp(self):
        super(CustomerTestCase, self).setUp()
        self.stripe_card = Mock(name='Stripe Card')
        for k,v in {
            "type": "Visa",
            "country": "US",
            "last4": "4242",
            "exp_year": 2015,
            "exp_month": 5,
        }.items():
            setattr(self.stripe_card, k, v)
        self.stripe_customer = Mock(name='Stripe Customer')
        self.stripe_customer.id = 'STRIPE_ID'
        self.stripe_customer.description = 'desc'
        self.stripe_customer.livemode = False
        self.stripe_customer.active_card = self.stripe_card
        self.mock_stripe = Mock()
        self.mock_stripe.Customer.create.return_value = self.stripe_customer
        self.ba = self.u.billing_account

## model tests

class CustomerTests(CustomerTestCase):
    def test_create_customer_from_stripe_object(self):
        c = Customer.objects.create_from_stripe_object(
            self.stripe_customer, self.ba)
        self.assertEqual(Customer.objects.get(), c)
    def test_create_customer_from_stripe_object_nocommit(self):
        c = Customer.objects.create_from_stripe_object(
            self.stripe_customer, self.ba, commit=False)
        self.assertEqual(Customer.objects.all().count(), 0)
    @unittest.skip('not implemented')
    def test_create_customer(self):
        pass
    @unittest.skip('not implemented')
    def test_create_customer_nocommit(self):
        pass
    @unittest.skip('not implemented')
    def test_fetch_customer(self):
        pass
    @unittest.skip('not implemented')
    def test_get_active_card(self):
        pass
    @patch.object(Customer, 'fetch_customer')
    def test_update_active_card(self, mock_fetch_customer):
        c = Customer.objects.create_from_stripe_object(
            self.stripe_customer, self.ba)
        mock_fetch_customer.return_value = self.stripe_customer
        c.update_active_card('fake card')
        self.assertEqual(c.cards.count(), 2)

## form tests

class FormDispatchTests(CustomerTestCase):
    def test_form_dispatch_update(self):
        c = Customer.objects.create_from_stripe_object(
            self.stripe_customer, self.ba)
        form = get_billing_details_form(self.ba)
        self.assertIs(form, CustomerUpdateForm)
    def test_form_dispatch_create(self):
        form = get_billing_details_form(self.ba)
        self.assertIs(form, CustomerCreationForm)


class CreateFormTests(CustomerTestCase):
    def test_save(self):
        form = CustomerCreationForm({'name':'Joe', 'stripe_token': 'token'})
        if not form.is_valid():
            raise Exception(form.errors)
        self.assertTrue(form.is_valid())
        form.billing_account = self.ba
        self.assertFalse(has_valid_billing_details(self.ba))
        with patch('billing.processor.stripe.models.stripe', self.mock_stripe):
            form.save()
        self.assertTrue(has_valid_billing_details(self.ba))
    @unittest.skip('not implemented')
    def test_save_nocommit(self):
        pass

class UpdateFormTests(CustomerTestCase):
    def test_save(self):
        form = CustomerCreationForm({'name':'Joe', 'stripe_token': 'token'})
        if not form.is_valid():
            raise Exception(form.errors)
        self.assertTrue(form.is_valid())
        form.billing_account = self.ba
        self.assertFalse(has_valid_billing_details(self.ba))
        with patch('billing.processor.stripe.models.stripe', self.mock_stripe):
            form.save()
        self.assertTrue(has_valid_billing_details(self.ba))
    @unittest.skip('not implemented')
    def test_save_nocommit(self):
        pass

