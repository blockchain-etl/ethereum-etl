import os

from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


long_description = read('README.md') if os.path.isfile("README.md") else ""

setup(
    name='ethereum-etl',
    version='1.3.1',
    author='Evgeny Medvedev',
    author_email='evge.medvedev@gmail.com',
    description='Tools for exporting Ethereum blockchain data to CSV or JSON',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/blockchain-etl/ethereum-etl',
    packages=find_packages(exclude=['schemas', 'tests']),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    keywords='ethereum',
    # web3.py doesn't work on 3.5.2 and less (https://github.com/ethereum/web3.py/issues/1012)
    python_requires='>=3.5.3,<3.8.0',
    install_requires=[
        'web3==4.7.2',
        'eth-utils==1.3.0',
        'eth-abi==1.2.0',
        # TODO: This has to be removed when "ModuleNotFoundError: No module named 'eth_utils.toolz'" is fixed at eth-abi
        'python-dateutil==2.7.0',
        'click==7.0',
        'ethereum-dasm==0.1.4'
    ],
    extras_require={
        'streaming': [
            'timeout-decorator==0.4.1',
            'google-cloud-pubsub==0.39.1'
        ],
        'dev': [
            'pytest~=4.3.0'
        ]
    },
    entry_points={
        'console_scripts': [
            'ethereumetl=ethereumetl.cli:cli',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/blockchain-etl/ethereum-etl/issues',
        'Chat': 'https://gitter.im/ethereum-etl/Lobby',
        'Source': 'https://github.com/blockchain-etl/ethereum-etl',
    },
)
