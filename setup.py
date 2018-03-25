from setuptools import setup

setup (
    name='image_downloader',
    version='1.0',
    # todo: downloaded_images needs to be added here in packages?
    packages=['', 'app.unittest', 'app.downloader', 'scripts'],
    install_requires=["requests", "tqdm"],
    url='https://github.com/mantoshkumar1',
    license='MIT License',
    author='Mantosh Kumar',
    author_email='mantoshkumar1@gmail.com',
    description='Document parser and web-image Downloader'
)
