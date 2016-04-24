#!/usr/bin/env python

from os.path import dirname, abspath
from setuptools import setup

source_directory = dirname(abspath(__file__))


setup(
    name="channels_rest",
    description="Provides tools to do django-rest-framework requests over a django-channels websocket.",
    author="Maikel Wever",
    author_email="maikelwever@gmail.com",
    packages=['channels_rest'],
    install_requires=[
        "Django>=1.8,<1.9",
        "djangorestframework",
        "channels"
    ],
    version="0.0.3",
)
