from distutils.core import setup

setup(name='pudzu',
      version='0.9',
      description='Various Python Utilities',
      author='Uri Granta',
      author_email='uri.granta+python@gmail.com',
      long_description='Various Python 3.6+ utility functions, mostly geared towards dataviz and used to create the data visualisations at https://www.flickr.com/photos/zarfo/albums. Most have been posted to reddit at some point by /u/Udzu.',
      url='https://github.com/Udzu/pudzu/',
      package_dir={'pudzu': '.'},
      py_modules = ['pudzu.utils', 'pudzu.dates', 'pudzu.pillar', 'pudzu.bamboo', 'pudzu.tureen', 'pudzu.charts' ]
     )
