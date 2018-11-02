from setuptools import setup

setup(name='pudzu',
      version='0.9.1',
      description='Various dataviz-oriented utilities',
      long_description='Various utility functions, mostly geared towards dataviz and used to create the data visualisations at https://www.flickr.com/photos/zarfo/albums (most of which have been posted to reddit at some point by /u/Udzu).',
      keywords='visualization pillow',
      url='https://github.com/Udzu/pudzu/',
      author='Uri Granta',
      author_email='uri.granta+python@gmail.com',
      license='MIT',
      classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
      ],
      package_dir={'pudzu': '.'},
      py_modules=['pudzu.utils', 'pudzu.dates', 'pudzu.pillar', 'pudzu.bamboo', 'pudzu.tureen', 'pudzu.charts'],
      python_requires='~=3.6',
      install_requires=[ 'toolz', 'pillow', 'numpy', 'pandas', 'beautifulsoup4' ]
)
