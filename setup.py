from pathlib import Path

from setuptools import find_packages, setup


def load_requirements():
    requirements_path = Path(__file__).with_name("requirements.txt")
    requirements = []

    for line in requirements_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        requirements.append(line)

    return requirements

setup(
    name='cleudocode',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=load_requirements(),
    entry_points={
        'console_scripts': [
            'cleudocode=cli.main:cli',
        ],
    },
)
