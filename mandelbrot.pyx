#cython: boundscheck=False

from numpy import empty
cimport numpy as np


cdef int mandelbrot_escape(double complex c, int n):
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


cdef int julia_escape(x0, y0, double complex c, int n):
    cdef int i
    z_x = x0
    z_y = y0
    x = c.real
    y = c.imag
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
    for j in range(M):
        for i in range(N):
            z = xs[i] + ys[j]*1j
            d[j, i] = mandelbrot_escape(z, n)
    return d


def generate_julia(np.ndarray[double, ndim=1] xs,
                   np.ndarray[double, ndim=1] ys,
                   double complex c, int n):
    """ Generate a julia set image """
    cdef unsigned int i, j
    cdef unsigned int N = len(xs)
    cdef unsigned int M = len(ys)

    cdef np.ndarray[int, ndim=2] d = empty(dtype='i', shape=(M, N))
    for j in range(len(ys)):
        for i in range(len(xs)):
            d[j, i] = julia_escape(xs[i], ys[j], c, n)
    return d
