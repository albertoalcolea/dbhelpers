import os
import re
from setuptools import setup


version = ''
with open('dbhelpers/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')


with open('README.md', 'r') as f:
    readme = f.read()


requires = []


setup(
	name='dbhelpers',
    version=version,
    description='Database helpers and utilities .',
    long_description=readme,
    author='Alberto Alcolea',
    author_email='albertoalcolea@gmail.com',
    url='http://albertoalcolea.com',
    packages=['dbhelpers'],
    package_dir={'dbhelpers': 'dbhelpers'},
    package_data={'': ['LICENSE']},
    include_package_data=True,
    install_requires=requires,
    license='Apache 2.0',
    zip_safe=False,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
)
