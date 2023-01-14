from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in human_resources/__init__.py
from human_resources import __version__ as version

setup(
	name="human_resources",
	version=version,
	description="HR",
	author="sals",
	author_email="hr@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
