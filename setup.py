import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tkScribe",
    version="1.0.1",
    author="Neil Brown",
    author_email="NeilBrownEmail@gmail.com",
    description="A plugin wordprocessor for Tkinter applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Neil-Brown/tkScribe/",
    install_requires=["pillow"],
    packages=["tkScribe"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
)