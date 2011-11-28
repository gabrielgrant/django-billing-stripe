from setuptools import setup

setup(
    name='django-billing.processor.stripe',
    version='0.1.1dev',
    author='Gabriel Grant',
    author_email='g@briel.ca',
    packages=['billing.processor.stripe', 'billing.processor.stripe.tests'],
    license='LGPL',
    long_description=open('README').read(),
    namespace_packages=['billing', 'billing.processor'],
    install_requires=[
        'django-billing',
        'stripe',
    ],
    dependency_links = [
    	'http://github.com/gabrielgrant/django-billing/tarball/master#egg=django-billing',
    ]
)
