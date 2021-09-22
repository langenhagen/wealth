"""The setup.py for the Python code of the project `Wealth`."""
import pathlib

import setuptools

readme_path = pathlib.Path.cwd().parent.joinpath("README.md")
with open(readme_path, "r", encoding="UTF-8") as file:
    long_description = file.read()

setuptools.setup(
    author="Andreas Langenhagen jr.",
    author_email="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
    ],
    description='The Python sources for the Project "Wealth"',
    install_requires=[
        "ipywidgets",
        "matplotlib",
        "pandas",
        "python-dateutil",
        "pyyaml",
        "scipy",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="wealth",
    packages=setuptools.find_packages(),
    python_requires=">=3.9",
    url="https://github.com/langenhagen/wealth",
    version="0.1.1",
)
