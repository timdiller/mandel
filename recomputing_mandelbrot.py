from math import sqrt
import numpy as np

from chaco.api import ArrayPlotData, Plot, hot
from chaco.tools.api import PanTool, ZoomTool
from enable.api import ComponentEditor
from traits.api import (
    Array, Event, HasTraits, Instance, Int, Property, Tuple,
    cached_property, on_trait_change
)
from traitsui.api import Item, View

from mandel import generate_mandelbrot

class NotifyingZoom(ZoomTool):
    zoomed = Event
    def normal_mouse_wheel(self, event):
        super(NotifyingZoom, self).normal_mouse_wheel(event)
        self.zoomed = True


class NotifyingPan(PanTool):
    panned = Event
    def panning_mouse_move(self, event):
        super(NotifyingPan, self).panning_mouse_move(event)
        self.panned = True


class MandelView(HasTraits):
    my_plot = Instance(Plot)
    zoom_tool = Instance(NotifyingZoom)
    pan_tool = Instance(NotifyingPan)
    img = Property(Array, depends_on=["xs", "ys", "resolution"])
    x_limits = Tuple(-3., 1.)
    y_limits = Tuple(-2., 2.)
    xs = Property(Array, depends_on=["resolution", "x_limits", "y_limits"])
    ys = Property(Array, depends_on=["resolution", "x_limits", "y_limits"])
    renderer = Property(depends_on="my_plot")
    resolution = Int(500)
    lod = Int(150)

    def _get_img(self):
        return generate_mandelbrot(self.xs, self.ys, self.lod)

    @cached_property
    def _get_renderer(self):
        return self.my_plot.plots['plot0'][0]

    def _get_xs(self):
        low, high = self.x_limits
        return np.linspace(low, high, self.resolution)

    def _get_ys(self):
        low, high = self.y_limits
        return np.linspace(low, high, self.resolution)

    def _my_plot_default(self):

        plot_data = ArrayPlotData(mandelbrot_img=self.img)
        plot = Plot(plot_data)
        plot.img_plot("mandelbrot_img",
                      xbounds=self.x_limits,
                      ybounds=self.y_limits,
                      colormap=hot,
                      )

        plot.x_axis.title = "Imaginary"
        plot.y_axis.title = "Real"
        self.pan_tool = NotifyingPan(plot)
        plot.tools.append(self.pan_tool)
        self.zoom_tool = NotifyingZoom(plot, zoom_factor=1.02)
        plot.tools.append(self.zoom_tool)
        self.on_trait_change(self.zoom_recompute,
                             "zoom_tool.zoomed, pan_tool.panned")
        return plot

    @on_trait_change("resolution, lod")
    def update_data(self):
        self.my_plot.data.set_data("mandelbrot_img", self.img)
        self.renderer.index.set_data(self.x_limits, self.y_limits)

    def zoom_recompute(self):
        """Recompute the image if zoom has sufficiently changed the view area.
        """
        change_threshold = 0.2
        x0, x1 = self.x_limits
        y0, y1 = self.y_limits
        old_area = (x1 - x0) * (y1 - y0)
        old_ctr = ((x0 + x1) / 2., (y0 + y1) / 2.)
        (x0, x1), (y0, y1) = self.get_zoom_limits()
        new_area = (x1 - x0) * (y1 - y0)
        new_ctr = ((x0 + x1) / 2., (y0 + y1) / 2.)

        area_relative_change = abs((new_area - old_area) / old_area)
        ctr_normed_change = abs(
            sqrt((new_ctr[0] - old_ctr[0]) ** 2 +
                 (new_ctr[1] - old_ctr[1]) ** 2) / sqrt(new_area))
        should_update = (
             area_relative_change >= change_threshold or
             ctr_normed_change >= change_threshold
            )
        if should_update:
            self.x_limits = (x0, x1)
            self.y_limits = (y0, y1)
            self.lod = 150 + int(new_area ** (-1./3))
            self.update_data()


    def get_zoom_limits(self):
        x_range = (self.renderer.index_range.x_range.low,
                   self.renderer.index_range.x_range.high)
        y_range = (self.renderer.index_range.y_range.low,
                   self.renderer.index_range.y_range.high)
        return x_range, y_range

view = View(
    Item("my_plot", editor=ComponentEditor(), show_label=False),
    Item("lod", style='readonly', show_label=False),
)


if __name__ == "__main__":
    mv = MandelView()
    mv.configure_traits(view=view)
