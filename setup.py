# core imports
import sys

# 3rd party imports
from setuptools import setup


# dependencies
install_requires=[
    #  'lxml,'
    'beautifulsoup4', 
    'flask'
]

if '--no-flask' in sys.argv:
    install_requires.pop('flask')

def readme():
    #  with open('README.rst') as f:
    with open('README.md') as f:  # only rst is supported :(
        return f.read()

setup(name='webook',
      packages=['webook'],
      # Update the version number for new releases
      version='0.0.1',
      # The name of your scipt, and also the command you'll be using for calling it
      
      install_requires=install_requires,
      # scripts
      #scripts=['scrape_ebook.py'],
      entry_points = {
          'console_scripts': ['webook=webook.command_line:run']
      },
      # meta data
      url='http://github.com/jancr/webook',
      author='Jan Christian Refsgaard',
      author_email='jancrefsgaard@gmail.com',
      license='MIT',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
      ],
      include_package_data=True,
      zip_safe=False
)
