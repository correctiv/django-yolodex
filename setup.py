import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-yolodex',
    version='0.0.1',
    packages=['yolodex'],
    zip_safe=False,
    include_package_data=True,
    license='MIT License',
    description='A Django app for managing relationships between entities.',
    long_description=README,
    url='https://github.com/correctiv/django-yolodex/',
    author='Stefan Wehrmeyer',
    author_email='mail@stefanwehrmeyer.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'Django',
        'djangorestframework',
        'django-parler',
        'networkx'
    ],
)
