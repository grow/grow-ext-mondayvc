from setuptools import setup


setup(
    name='grow-ext-greenhouse',
    version='1.0.4',
    license='MIT',
    author='Grow SDK Authors',
    author_email='hello@grow.io',
    packages=[
        'greenhouse',
    ],
    install_requires = [
        'bleach',
    ],
)
