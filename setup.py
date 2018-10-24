import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ethereum-etl",
    version="0.0.1",
    author="Evgeny Medvedev",
    author_email="medvedev1088@gmail.com",
    description="Python scripts for ETL (extract, transform and load) jobs for Ethereum blocks, transactions... etc",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/blockchain-etl/ethereum-etl",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)