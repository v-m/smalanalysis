from setuptools import setup

setup(name='smalanalysis',
      version='0.1a1',
      description='Android Bytecode Analysis Tools',
      long_description='Android Bytecode Analysis Tools',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
      ],
      python_requires='~=3.6',
      keywords='smali android apk baksmali',
      url='https://github.com/v-m/smalanalysis',
      author='Vincenzo Musco',
      author_email='muscovin@gmail.com',
      license='MIT',
      packages=['smalanalysis.smali', 'smalanalysis.tools'],
      install_requires=[],
      scripts=['bin/sa-disassemble', 'bin/sa-including-debug', 'bin/sa-metrics', 'bin/sa-baksmali-2.2.1.jar'],
      include_package_data=True,
      zip_safe=False)