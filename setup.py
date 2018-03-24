from setuptools import setup

setup(name='radicale-remind',
      version='0.2.3',
      description='Radicale Remind, Abook and Taskwarrior storage backend',
      long_description=open('README.rst').read(),
      author='Jochen Sprickerhof',
      author_email='radicale@jochen.sprickerhof.de',
      license='GPLv3+',
      url='https://github.com/jspricke/radicale-remind',
      keywords=['Radicale'],
      classifiers=[
          'Programming Language :: Python',
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "Environment :: Web Environment",
          "Intended Audience :: End Users/Desktop",
          "Intended Audience :: Information Technology",
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          "Operating System :: OS Independent",
          "Topic :: Office/Business :: Groupware"
      ],

      install_requires=['abook', 'icstask', 'Radicale', 'remind'],
      py_modules=['radicale_remind'],)
