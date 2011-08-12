
# from http://www.travisswicegood.com/2010/01/17/django-virtualenv-pip-and-fabric/

from django.conf import settings
from django.core.management import call_command

def main():
    # Dynamically configure the Django settings with the minimum necessary to
    # get Django running tests
    settings.configure(
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.admin',
            'django.contrib.sessions',
            'billing',
            'billing.processor.stripe',
        ),
        # Django replaces this, but it still wants it. *shrugs*
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': '/tmp/django_login.db',
            }
        },
        MEDIA_ROOT = '/tmp/django_test_media/',
        ROOT_URLCONF = '',
        DEBUG = True,
		TEMPLATE_DEBUG = True,
		STRIPE_SECRET_API_KEY = 'SECRET_API_KEY',
		STRIPE_PUBLIC_API_KEY = 'PUBLIC_API_KEY',
    ) 
    
    #call_command('syncdb')
    
    # Fire off the tests
    call_command('test', 'stripe')
    

if __name__ == '__main__':
    main()

