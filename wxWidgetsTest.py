import wx
from matplotlib.figure import Figure
import numpy as np
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2Wx

class MplCanvasFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title='Matplotlib in Wx', size=(600, 400))
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        x = np.arange(0, 6, .01)
        y = np.sin(x ** 2) * np.exp(-x)
        self.axes.plot(x, y)
        self.canvas = FigureCanvas(self, wx.ID_ANY, self.figure)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.EXPAND)
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()
        self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.toolbar.Show()
        self.SetSizer(self.sizer)
        self.Fit()

class MplApp(wx.App):
    def OnInit(self):
        frame = MplCanvasFrame()
        self.SetTopWindow(frame)
        frame.Show(True)
        return True

mplapp = MplApp(False)
mplapp.MainLoop()

