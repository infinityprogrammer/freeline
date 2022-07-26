from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in freeline/__init__.py
from freeline import __version__ as version

setup(
	name="freeline",
	version=version,
	description="freeline",
	author="RAFI",
	author_email="freeline@freeline.ae",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
