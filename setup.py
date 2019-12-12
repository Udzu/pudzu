from setuptools import setup

VERSION='0.9.1'
URL='https://github.com/Udzu/pudzu-packages/'
AUTHOR='Uri Granta'
AUTHOR_EMAIL='uri.granta+python@gmail.com'
LICENSE='MIT'
CLASSIFIERS=[
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
]
PYTHON_REQUIRES='~=3.6'

setup(name='pudzu', version=VERSION, packages=['pudzu.experimental'], package_dir={'pudzu.experimental': 'modules'},
      description='Various dataviz-oriented utilities',
      long_description='Various utility functions, mostly geared towards dataviz and used to create the data visualisations at https://www.flickr.com/photos/zarfo/albums (most of which have been posted to reddit at some point by /u/Udzu).',
      keywords='pudzu visualization pillow',
      url=URL, author=AUTHOR, author_email=AUTHOR_EMAIL, license=LICENSE, classifiers=CLASSIFIERS,
      install_requires=[f'pudzu-utils>={VERSION}', f'pudzu-dates>={VERSION}', f'pudzu-pillar>={VERSION}', f'pudzu-charts>={VERSION}', 'beautifulsoup4'],
      python_requires=PYTHON_REQUIRES)
