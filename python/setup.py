# setup.py
from setuptools import setup, find_packages

setup(
    name="dotprompt",
    version="0.0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[], 
    python_requires=">=3.7",
    description="A library for working with .prompt files",
    author="Diego Ponce de Leon Franco",
    author_email="your.email@example.com",
)