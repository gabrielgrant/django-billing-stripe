from django.forms.widgets import HiddenInput, TextInput
from django.utils.safestring import mark_safe
from django.conf import settings
from django.template.loader import render_to_string

class StripeTokenInput(HiddenInput):
    """
    This widget doesn't render a field at all, because the relevant field is added by
    the Javascript. We do, however, want it processed by Django.
    """
    def render(self, name, value, attrs=None, *args, **kwargs):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(self._format_value(value))
        context = dict(pubKey=settings.STRIPE_PUBLIC_API_KEY, name=name, attrs=final_attrs)
        
        #return mark_safe(render_to_string('stripe/stripe_form_script_v0.html', context))
        return mark_safe(render_to_string('stripe/stripe_token_input.html', context))


class CardNumberInput(TextInput):
    def render(self, name, value, attrs=None, *args, **kwargs):
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        context = dict(name=name, attrs=final_attrs)
        return mark_safe(render_to_string('stripe/card_number_input.html', context))

class CVCInput(TextInput):
    def render(self, name, value, attrs=None, *args, **kwargs):
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        context = dict(name=name, attrs=final_attrs)
        return mark_safe(render_to_string('stripe/cvc_input.html', context))
    
class ExpirationInput(TextInput):
    def render(self, name, value, attrs=None, *args, **kwargs):
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        context = dict(name=name, attrs=final_attrs)
        return mark_safe(render_to_string('stripe/expiration_input.html', context))
