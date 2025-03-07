from setuptools import setup, find_packages
import os

setup(
    name="dotprompt",
    version="0.0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    description="Una biblioteca para trabajar con archivos de formato .prompt",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    author="Tu Nombre",
    author_email="tu@email.com",
    url="https://github.com/dponcedeleonf/dotprompt",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)