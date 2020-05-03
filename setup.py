from setuptools import setup
from dbhelpers import __version__


with open('README.md', 'r') as f:
    readme = f.read()


setup(
	name='dbhelpers',
    version=__version__,
    description='Database helpers and utilities.',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Alberto Alcolea',
    author_email='albertoalcolea@gmail.com',
    url='http://albertoalcolea.com',
    packages=['dbhelpers'],
    include_package_data=True,
    license='Apache 2.0',
    zip_safe=False,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ),
)
