from setuptools import setup, find_packages

requirements = []

test_requirements = [
    'behave'
]

setup(
    name='chasm',
    version='0.0.1',
    description='ABCI for peercoin',
    authors=['Daniel Bigos', 'Piotr Żelazko'],
    url='https://github.com/bidzyyys/chasm.git',
    download_url='https://github.com/bidzyyys/chasm.git/archive/0.0.1.tar.gz',
    license='GPL-3.0',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'chasm = chasm.chasm:cli',
        ],
    },
    classifiers=[
        'Development Status :: 1 - Alpha',
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=False
)
