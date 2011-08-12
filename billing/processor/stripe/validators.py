from django.core.exceptions import ValidationError

def exp_year(value):
    if not 2000 < value <= 2025:
        raise ValidationError(u'%s is not a valid expiration year' % value)
    

def exp_month(value):
    if not 0 < value <= 12:
        raise ValidationError(u'%s is not a valid month' % value)

def last4(value):
    if not value.isdigit():
        raise ValidationError(u'%s is not a valid piece of a card number' % value)
