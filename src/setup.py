"""The setup.py for the Python code of the project `Wealth`."""
import pathlib

import setuptools

with open(pathlib.Path.cwd().parent.joinpath("README.md"), "r") as file:
    long_description = file.read()

install_requires = [
    "ipywidgets",
    "matplotlib",
    "pandas",
    "python-dateutil",
    "pyyaml",
    "scipy",
]

setuptools.setup(
    author="Andreas Langenhagen jr.",
    author_email="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
    ],
    description='The Python sources for the Project "Wealth"',
    install_requires=install_requires,
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="wealth",
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    url="https://github.com/langenhagen/wealth",
    version="0.1.0",
)
