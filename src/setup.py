import sys

from setuptools import find_packages, setup
print(sys.path)
setup(
    name='reefscanner',
    packages=['reefscanner.basic_model'],
    version='0.1.6',
    description='aims_reef_scanner_data_model',
    author='Greg',
    license='MIT',
)