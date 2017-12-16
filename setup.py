from setuptools import setup
setup(name='quarg',
      version='0.1',
      description='Effortless CLI',
      long_description='Generate a command line interface with no code, ' +
                       'and gradually add annotations for more control.',
      author='Rob Hague',
      author_email='rob.hague@cydar.co.uk',
      url='https://github.com/CydarLtd/quarg',

      py_modules=['quarg'],
      # Use scripts instead of entry_points as the relevant
      # functionality currently relies on using the global namespace
      scripts=['quarg'],

      license='MIT',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 2.7'
      ],
      keywords='command line commandline argument arguments '+
               'option options argv parsing'
)
