import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="combined_workflow",
    version="0.0.1",
    author="Edwin Gao",
    author_email="egao@mozilla.com",
    description="A demonstration package to define and execute Bitbar testdroid projects and tests.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/worldomonation/combined_workflow",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent",
    ],
)
