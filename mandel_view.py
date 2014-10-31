import numpy as np
from numpy import linspace

from chaco.api import (ArrayPlotData, OverlayPlotContainer, Plot)
from chaco.default_colormaps import color_map_dict
from chaco.tools.api import PanTool, ZoomTool
from enable.api import BaseTool, ComponentEditor
from traits.api import (Any, Array, Event, Float, HasTraits, Instance, Int,
                        Property, Tuple, cached_property)
from traitsui.api import (HGroup, Item, CheckListEditor, ButtonEditor,
                          RangeEditor, View, VGroup)

# Local Imports
from mandel import generate_mandelbrot, generate_julia


class CrossHairs(BaseTool):
    selected_x = Float
    selected_y = Float

    def normal_right_down(self, event):
        plot = self.component
        self.selected_x, self.selected_y = plot.map_data((event.x, event.y))
        print "Screen point - {}, {}".format(self.selected_x, self.selected_y)


class MandelPlot(HasTraits):
    plot = Instance(OverlayPlotContainer)
    img_plot = Instance(Plot)
    ch_plot = Instance(Plot)

    # julia_data = Array
    julia_plot = Instance(Plot)
    julia_img = Property(Array, depends_on=["detail", "resolution",
                                            "julia_bounds_x",
                                            "julia_bounds_y"])
    julia_bounds_x = Tuple(-1.5, 1.5)
    julia_bounds_y = Tuple(-1.5, 1.5)
    crosshair = Instance(CrossHairs)

    draw = Event
    mandel_img = Property(Array, depends_on=["detail", "resolution",
                                             "x_low", "x_high",
                                             "y_low", "y_high"])
    detail = Int(500)
    resolution = Int(500)
    colormap = Any

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
                Item("draw", editor=ButtonEditor(label="Draw"),
                     show_label=False),
                ),
            HGroup(
                Item("resolution"),
                Item(
                    "colormap",
                    editor=CheckListEditor(
                        values=color_map_dict.items()
                    ),
                ),
            ),
            HGroup(
                Item(
                    "plot",
                    editor=ComponentEditor(),
                    show_label=False,
                ),
                Item(
                    "julia_plot",
                    editor=ComponentEditor(),
                    show_label=False,
                ),

            ),
        ),
        resizable=True,
    )

    # Properties
    @cached_property
    def _get_mandel_img(self):
        x = linspace(self.x_low, self.x_high, self.resolution)
        y = linspace(self.y_low, self.y_high, self.resolution)
        return generate_mandelbrot(x, y, self.detail)

    def _get_julia_img(self):
        c = self.crosshair.selected_x + self.crosshair.selected_y * 1j
        x = linspace(-self.julia_bounds_x[1], self.julia_bounds_x[1],
                     self.resolution)
        y = linspace(-self.julia_bounds_y[1], self.julia_bounds_y[1],
                     self.resolution)
        return generate_julia(x, y, c, self.detail)

    # Defaults
    def _julia_data_default(self):
        return np.zeros((self.resolution, self.resolution),
                        dtype=np.uint16)

    def _ch_plot_default(self):
        x = (self.x_low + self.x_high) / 2
        y = (self.y_low + self.y_high) / 2
        h_cross_x = np.array([self.x_low, self.x_high])
        h_cross_y = np.array([y, y])
        v_cross_x = np.array([x, x])
        v_cross_y = np.array([self.y_low, self.y_high])

        cross_hair_data = ArrayPlotData(h_cross_x=h_cross_x,
                                        h_cross_y=h_cross_y,
                                        v_cross_x=v_cross_x,
                                        v_cross_y=v_cross_y)
        ch_plot = Plot(cross_hair_data)
        ch_plot.plot(("h_cross_x", "h_cross_y"), type="line", color="green",)
        ch_plot.plot(("v_cross_x", "v_cross_y"), type="line", color="green",)
        while len(ch_plot.underlays) > 0:
            ch_plot.underlays.pop(0)
        ch_plot.range2d = self.img_plot.range2d
        cross_hair_tool = CrossHairs(ch_plot)
        ch_plot.tools.append(cross_hair_tool)
        self.crosshair = cross_hair_tool
        self.on_trait_change(self.draw_cross_hairs,
                             "crosshair.selected_x, crosshair.selected_y")
        return ch_plot

    def _img_plot_default(self):
        img = self.mandel_img
        plot_data = ArrayPlotData(img=img)
        my_img_plot_instance = Plot(plot_data)
        my_img_plot_instance.img_plot(
            "img",
            xbounds=(self.x_low, self.x_high),
            ybounds=(self.y_low, self.y_high),
            colormap=self.colormap,
        )

        pan_tool = PanTool(my_img_plot_instance)
        zoom_tool = ZoomTool(my_img_plot_instance,
                             zoom_factor=1.02)

        my_img_plot_instance.tools.append(pan_tool)
        my_img_plot_instance.tools.append(zoom_tool)
        return my_img_plot_instance

    def _julia_plot_default(self):
        img = self.julia_img
        plot_data = ArrayPlotData(img=img)
        julia_plot = Plot(plot_data)
        julia_plot.img_plot(
            "img",
            xbounds=self.julia_bounds_x,
            ybounds=self.julia_bounds_y,
            colormap=self.colormap,
        )
        return julia_plot

    def _plot_default(self):
        opc = OverlayPlotContainer(self.img_plot, self.ch_plot)
        return opc

    def _colormap_changed(self):
        # p = self.img_plot.plots[0]
        value_range = self.img_plot.color_mapper.range
        self.img_plot.color_mapper = self.colormap[0](value_range)
        self.julia_plot.color_mapper = self.colormap[0](value_range)
        self.plot.request_redraw()

    def _draw_fired(self):
        x_range, y_range = self.get_zoom_limits()
        self.x_low, self.x_high = x_range
        self.y_low, self.y_high = y_range

        new_img = self.mandel_img
        self.img_plot.data.set_data("img", new_img)
        renderer = self.img_plot.plots['plot0'][0]
        renderer.index.set_data(x_range, y_range)
        self.draw_cross_hairs()

        self.render_julia()

    def draw_cross_hairs(self):
        x = self.crosshair.selected_x
        y = self.crosshair.selected_y
        #if x is not None:
        h_cross_x = np.array([self.x_low, self.x_high])
        h_cross_y = np.array([y, y])
        v_cross_x = np.array([x, x])
        v_cross_y = np.array([self.y_low, self.y_high])
        self.ch_plot.data.set_data("h_cross_x", h_cross_x)
        self.ch_plot.data.set_data("h_cross_y", h_cross_y)
        self.ch_plot.data.set_data("v_cross_x", v_cross_x)
        self.ch_plot.data.set_data("v_cross_y", v_cross_y)

    def get_zoom_limits(self):
        renderer = self.img_plot.plots['plot0'][0]
        x_range = (renderer.index_range.x_range.low,
                   renderer.index_range.x_range.high)
        y_range = (renderer.index_range.y_range.low,
                   renderer.index_range.y_range.high)
        return x_range, y_range

    def render_julia(self):
        # x = self.crosshair.selected_x
        # y = self.crosshair.selected_y
        # c = x + y * 1j
        # z_x = x
        # z_y = y
        # xmin, xmax = self.julia_bounds_x
        # ymin, ymax = self.julia_bounds_y
        # # import ipdb
        # # ipdb.set_trace()
        # # self.julia_data = generate_julia(x, y, c, self.detail)
        # for i in xrange(self.detail * 5):
        #     z = z_x + z_y * 1j
        #     new_z = np.sqrt(z ** 2 - c) * random.choice([-1, 1])
        #     # z_x = z_x ** 2 - z_y ** 2 + x
        #     # z_y = 2 * z_x * z_y + y
        #     z_x = new_z.real
        #     z_y = new_z.imag
        #     idx_x = np.clip(int(self.resolution * min(max(
        #         (z_x - xmin) / (xmax - xmin), xmin), xmax)),
        #         0, self.julia_data.shape[0] - 1)
        #     idx_y = np.clip(int(self.resolution * min(max(
        #         (z_y - ymin) / (ymax - ymin), ymin), xmax)),
        #         0, self.julia_data.shape[1] - 1)
        #     self.julia_data[idx_y, idx_x] += 1
        #     print "({:.4f}, {:.4f}) -> ({}, {})".format(
        #         z_x, z_y, idx_x, idx_y)
        # print np.where(self.julia_data > 0)
        self.julia_plot.data.set_data("img", self.julia_img)

if __name__ == "__main__":
    mp = MandelPlot()
    mp.configure_traits()
