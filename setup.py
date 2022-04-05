import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="constraint-solver",
    version="0.1.0",
    author="Kenneth Brown",
    author_email="siegel.zero@gmail.com",
    description="Constraint Satisfaction solver",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/siegelzero/constraint-solver",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
