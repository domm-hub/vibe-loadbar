from setuptools import setup, find_packages

setup(
    name="vibe-loadbar",
    version="0.1.5",
    author="Adam",
    description="A lightweight alternative to TQDM. Part of the vibe suite.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.11',
)