from chaco.api import (ArrayPlotData, Plot, PiYG)
from chaco.tools.api import DragZoom, PanTool, ZoomTool
from enable.api import ComponentEditor
from numpy import linspace, pi, sin, cos
from traits.api import (Array, Event, Float, HasTraits, Instance, Int,
                        Property, cached_property)
from traitsui.api import HGroup, Item, View, VGroup, ButtonEditor, RangeEditor

# Local Imports
from mandel import generate_mandelbrot


class MandelPlot(HasTraits):
    chaco_plot = Instance(Plot)
    draw = Event
    mandel_img = Property(Array, depends_on=["detail", "x_resolution",
                                             "y_resolution", "x_low", "x_high",
                                             "y_low", "y_high"])
    detail = Int(100)
    x_resolution = Int(100)
    y_resolution = Int(100)

    x_low = Float(-2.0)
    x_high = Float(1.0)
    y_low = Float(-1.5)
    y_high = Float(1.5)

    traits_view = View(
        VGroup(
            HGroup(
                Item("detail",
                     style="custom",
                     editor=RangeEditor(low=100, high=10000, mode="xslider"),
                     ),
                Item("draw", editor=ButtonEditor(label="Draw"), show_label=False),
                ),
            HGroup(
                Item("x_resolution"),
                Item("y_resolution"),
                ),
            ),
        Item("chaco_plot",
             editor=ComponentEditor(),
             show_label=False,
             ),
        resizable=True,
        )

    def get_zoom_limits(self):
        renderer = self.chaco_plot.plots['plot0'][0]
        x_range = (renderer.index_range.x_range.low,
                   renderer.index_range.x_range.high)
        y_range = (renderer.index_range.y_range.low,
                   renderer.index_range.y_range.high)
        return x_range, y_range

    def _draw_fired(self):
        x_range, y_range = self.get_zoom_limits()
        self.x_low, self.x_high = x_range
        self.y_low, self.y_high = y_range
        #import ipdb; ipdb.set_trace()

        new_img = self.mandel_img
        self.chaco_plot.data.set_data("img", new_img)
        renderer = self.chaco_plot.plots['plot0'][0]
        renderer.index.set_data(x_range, y_range)

    @cached_property
    def _get_mandel_img(self):
        x = linspace(self.x_low, self.x_high, self.x_resolution)
        y = linspace(self.y_low, self.y_high, self.y_resolution)
        return generate_mandelbrot(x, y, self.detail)

    def _chaco_plot_default(self):
        img = self.mandel_img
        plot_data = ArrayPlotData(img=img)
        my_chaco_plot_instance = Plot(plot_data)
        my_renderer = my_chaco_plot_instance.img_plot(
            "img",
            xbounds=(self.x_low, self.x_high),
            ybounds=(self.y_low, self.y_high),
            colormap=PiYG,
        )

        pan_tool = PanTool(my_chaco_plot_instance)
        zoom_tool = ZoomTool(my_chaco_plot_instance,
                             zoom_factor=1.02)

        my_chaco_plot_instance.tools.append(pan_tool)
        my_chaco_plot_instance.tools.append(zoom_tool)
        return my_chaco_plot_instance

if __name__ == "__main__":
    mp = MandelPlot()
    mp.configure_traits()
