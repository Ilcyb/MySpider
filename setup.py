from setuptools import setup, find_packages

with open('requirements.txt', 'r', encoding='utf-8') as require_file:
    requirements = require_file.readlines()

setup(
    name='MySpider',
    version='0.0.1',
    description='A micro spider frameword.',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    author='ilcyb',
    package=find_packages(),
    install_required=requirements,
    license='MIT',
    classifiers=(
        'Development Status :: 1 - Planning',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5'
    )
)
