from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='ethereum-etl',
    version='0.0.1',
    author='Evgeny Medvedev',
    author_email='evge.medvedev@gmail.com',
    description='Export data components of Ethereum Blockchain',
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
    ],
    keywords='ethereum',
    python_requires='>=3.5.0,<3.7.0',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'export_all=ethereumetl.cli.export_all:cli',
            'export_blocks_and_transactions=ethereumetl.cli.export_blocks_and_transactions:cli',
            'export_contracts=ethereumetl.cli.export_contracts:cli',
            'export_receipts_and_logs=ethereumetl.cli.export_receipts_and_logs:cli',
            'export_token_transfers=ethereumetl.cli.export_token_transfers:cli',
            'export_tokens=ethereumetl.cli.export_tokens:cli',
            'export_traces=ethereumetl.cli.export_traces:cli',
            'extract_token_transfers=ethereumetl.cli.extract_token_transfers:cli',
            'get_block_range_for_date=ethereumetl.cli.get_block_range_for_date:cli',
            'get_block_range_for_timestamps=ethereumetl.cli.get_block_range_for_timestamps:cli',
            'get_keccak_hash=ethereumetl.cli.get_keccak_hash:cli',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/blockchain-etl/ethereum-etl/issues',
        'Chat': 'https://gitter.im/ethereum-etl/Lobby',
        'Source': 'https://github.com/blockchain-etl/ethereum-etl',
    },
)
