#cython: boundscheck=False

from cython.parallel import prange
cimport numpy as np
from numpy import empty


cdef int mandelbrot_escape(double complex c, int n) nogil:
    """ Mandelbrot set escape time algorithm in real and complex components
    """
    cdef double complex z
    cdef int i
    z = c
    for i in range(n):
        z = z*z + c
        if z.real*z.real + z.imag*z.imag >= 4.0:
           break
    else:
        i = -1
    return i


cdef int julia_escape(double complex z0, double complex c, int n) nogil:
    cdef int i
    cdef double z_x = z0.real
    cdef double z_y = z0.imag
    cdef double x = c.real
    cdef double y = c.imag
    for i in range(n):
        z_x, z_y = z_x ** 2 - z_y ** 2 + x, 2 * z_x * z_y + y
        if z_x ** 2 + z_y ** 2 >= 4.0:
            break
    else:
        i = -1
    return i


def generate_mandelbrot(np.ndarray[double, ndim=1] xs,
                        np.ndarray[double, ndim=1] ys, int n):
    """ Generate a mandelbrot set """
    cdef unsigned int i, j
    cdef unsigned int N = len(xs)
    cdef unsigned int M = len(ys)
    cdef double complex z

    cdef np.ndarray[int, ndim=2] d = empty(dtype='i', shape=(M, N))
    with nogil:
        for j in prange(M):
            for i in prange(N):
                z = xs[i] + ys[j] * 1j
                d[j, i] = mandelbrot_escape(z, n)
    return d


def generate_julia(np.ndarray[double, ndim=1] xs,
                   np.ndarray[double, ndim=1] ys,
                   double complex c, int n):
    """ Generate a julia set image """
    cdef unsigned int i, j
    cdef unsigned int N = len(xs)
    cdef unsigned int M = len(ys)
    cdef double complex z0

    cdef np.ndarray[int, ndim=2] d = empty(dtype='i', shape=(M, N))
    with nogil:
        for j in prange(M):
            for i in prange(N):
                z0 = xs[i] + ys[j] * 1j
                d[j, i] = julia_escape(z0, c, n)
    return d
