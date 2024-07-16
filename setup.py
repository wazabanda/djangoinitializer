# setup.py
from setuptools import setup, find_packages
import os

def read_requirements():
    """Read the requirements from the requirements.txt file."""
    with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
        return f.read().splitlines()

setup(
    name='django-init',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'django-init = django_initializer.__main__:main',
        ],
    },
    install_requires=read_requirements(),
    include_package_data=True,
    package_data={
        '':['templates/*']
    }
)
