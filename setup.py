from setuptools import setup

setup (
    name='image_downloader',
    version='1.0',
    packages=[ 'implementation', 'implementation.unittest' ],
    install_requires=[ "requests", "tqdm" ],
    url='https://github.com/mantoshkumar1',
    license='MIT License',
    author='Mantosh Kumar',
    author_email='mantoshkumar1@gmail.com',
    description='Document parser and web-image Downloader'
)
