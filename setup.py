from setuptools import setup, find_packages

setup(
    name='cleudocode',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'rich',
        'requests',
        'python-dotenv'
    ],
    entry_points={
        'console_scripts': [
            'cleudocode=cli.main:cli',
        ],
    },
)