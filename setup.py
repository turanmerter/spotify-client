from setuptools import setup

setup(
    name='spotifyapp',
    packages=['spotifyapp'],
    include_package_data=True,
    install_requires=[
        'flask', 'requests'
    ],
)