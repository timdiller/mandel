#from distutils.core import setup
#from distutils.extension import Extension
from setuptools import setup, find_packages, Extension
from Cython.Distutils import build_ext

import numpy

ext = Extension("mandel",
                ["mandelbrot.pyx"],
                include_dirs=[numpy.get_include()])

setup(
    name="mandel",
    version="1.0",
    packages=find_packages(),
    ext_modules=[ext],
    cmdclass={'build_ext': build_ext},
)
