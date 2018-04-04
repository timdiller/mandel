Example Mandelbrot Fract Viewers Built with TraitsUI
----------------------------------------------------

Use `setup.py` to compile `madelbrot.pyx` into the `mandel.so` or `mandel.pyd`
extension.

    python setup.py build_ext --inplace

`mandel_view.py` and `recomputing_mandelbrot.py` both make use of the
extension library, which provides fast vectorized computation of Mandelbrot
and Julia fractal images.  `recomputing_mandelbrot` provides and interface that
recomputes the image once the zoom level changes by 10%.  The resolution is
lower, but it provides a nice "infinite zoom" effect.  `mandel_view.py`
allows specification of resolution and level of detail but requires a button
click to recompute the image.  It also will use a right-click to seed the
computation of a Julia fractal.