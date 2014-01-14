from distutils.core import setup
import os.path

setup(name='dateinfer',
      version='0.1.0',
      description='Infers date format from examples',
      long_description="""Uses a series of pattern matching and rewriting rules to compute a "best guess" datetime.strptime format string give a list of example date strings.""",
      author='Jeffrey Starr',
      author_email='jeffrey.starr@ztoztechnologies.com',
      url='https://github.com/jeffreystarr/dateinfer',
      packages=['dateinfer'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      data_files=[('', [os.path.join('dateinfer', 'examples.yaml')])]
      )
