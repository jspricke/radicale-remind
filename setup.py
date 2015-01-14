from setuptools import setup

setup(name='radicale-storage',
      version='0.1.0',
      description='''
       Radicale Remind and Abook storage backend
       ''',
      author='Jochen Sprickerhof',
      author_email='radicale@jochen.sprickerhof.de',
      license='GPLv3+',
      url='https://github.com/jspricke/radicale-storage',
      keywords=['Radicale'],
      classifiers=['Programming Language :: Python'],

      install_requires=['abook', 'python-dateutil', 'Radicale', 'remind'],
      py_modules=['remind', 'abook', 'remind_abook'],
     )
