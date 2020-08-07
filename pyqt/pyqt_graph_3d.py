"""Module for creating bar_chart animation."""
# TODO
# Add time-range option


from typing import Dict, List

import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import requests
from bs4 import BeautifulSoup
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from PyQt5.QtCore import QCoreApplication, QRect, pyqtSlot
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (QAction, QDesktopWidget, QFileDialog, QMainWindow,
                             QPushButton, QShortcut, QVBoxLayout, QWidget)


class App(QMainWindow):
    """Manage everything present in the PyQt window.

    The position of the toolbar and canvas are instantiated here.

    Methods
    -------
    ```python
    initUI(self) -> None:
    on_quit_key(self) -> None:
    plot_chart(self) -> None:
    ```

    Properties
    ----------
    ```python
    title: str
    chart: Plot
    widget: QWidget
    shortcut_q: QShortcut
    shortcut_w: QShortcut
    ```
    """

    def __init__(self):
        super().__init__()

        self.title = "NFL Score Heatmap"

        self.chart: Chart

        # The central widget
        self.widget: QWidget

        self.init_ui()

        self.plot_chart()

    def init_ui(self) -> None:
        """Create the initial window and register event handlers."""
        self.setWindowTitle(self.title)

        self.shortcut_q = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.shortcut_w = QShortcut(QKeySequence("Ctrl+W"), self)

        self.shortcut_q.activated.connect(self.on_quit_key)
        self.shortcut_w.activated.connect(self.on_quit_key)

    @pyqtSlot()
    def on_quit_key(self):
        """Quit the application."""
        QCoreApplication.instance().quit()

    def plot_chart(self) -> None:
        """Create the Plot."""
        self.showMaximized()

        chart = Chart(parent=self, title=self.title)

        toolbar = NavigationToolbar(chart, self)

        self.widget = QWidget()
        vlayout = QVBoxLayout()

        vlayout.addWidget(toolbar)
        vlayout.addWidget(chart)

        # Create a placeholder widget to hold our toolbar and canvas.
        self.widget.setLayout(vlayout)
        self.setCentralWidget(self.widget)

        self.showMaximized()


class Chart(FigureCanvas):
    """Manage the plotting of all four subplots.

    Methods
    -------
    ```python
    setup_plt(self) -> None:
    format_plt(self) -> None:
    # formatting/init
    fmt_chart(self) -> None:
    ```

    Properties
    ----------
    ```python
    title: str
    bounds: Dict[str, int]
    fig: Figure
    chart: Axes3D
    ```
    """

    def __init__(self, parent: App = None, title: str = ""):
        self.title = title

        self.bounds: Dict[str, int]

        self.fig = Figure(dpi=120)

        super().__init__(self.fig)

        self.setParent(parent)

        self.setup_plt()

        self.chart: Axes3D = self.fig.add_subplot(111, projection="3d",
                                                  elev=60, azim=30)

        self.show_heatmap()

        self.fmt_chart()

        self.format_plt()

    def setup_plt(self) -> None:
        """Format the plot before rendering."""
        plt.style.use("ggplot")

    def format_plt(self) -> None:
        """Format the plot after rendering."""
        self.fig.tight_layout()

    def show_heatmap(self) -> None:
        """Fetch NFl data then show on chart."""
        url = "https://www.pro-football-reference.com/boxscores/game-scores.htm"

        res = requests.get(url)

        page = BeautifulSoup(res.text, "html.parser")

        games = page.find(id="games").find("tbody").find_all("tr")

        scores: List[Dict[str, int]]

        scores = [{"win": int(game.find("td",
                                        {"data-stat": "pts_win"}).text),
                   "lose": int(game.find("td",
                                         {"data-stat": "pts_lose"}).text),
                   "freq": int(game.find("td",
                                         {"data-stat": "counter"}).text)}
                  for game in games]

        win_bound = max(scores, key=lambda obj: obj["win"])["win"]
        freq_bound = max(scores, key=lambda obj: obj["freq"])["freq"]

        self.bounds = {"x": win_bound, "y": win_bound, "z": freq_bound}

        matrix = np.zeros((win_bound + 1, win_bound + 1))

        for score in scores:
            matrix[score["win"]][score["lose"]] = score["freq"]

        # Reverse each axis in order to have a (0,0) point
        _x = np.arange(win_bound + 1)
        _x = _x[::-1]
        _y = np.arange(win_bound + 1)
        _y = _y[::-1]
        _xx, _yy = np.meshgrid(_x, _y)
        anchor_x, anchor_y = _xx.ravel(), _yy.ravel()

        bar_heights = np.ravel(matrix)
        anchor_z = np.zeros_like(bar_heights)
        bar_widths = bar_depths = 1

        norms = colors.LogNorm(vmin=1, vmax=freq_bound)
        ramp = cm.ScalarMappable(norm=norms, cmap=cm.get_cmap("Reds"))
        bar_colors = [ramp.to_rgba(freq) if freq > 0 else (0, 0, 0, 0)
                      for freq in bar_heights]

        self.chart.bar3d(
            anchor_x,
            anchor_y,
            anchor_z,
            bar_widths,
            bar_depths,
            bar_heights,
            color=bar_colors,
            shade=True)

    @ staticmethod
    def gen_ticks(bound: int) -> List[int]:
        """Generate increasing ticks from a reversed axis.

        Parameters
        ----------
        bound : `int`
            The highest value, tick for this is 0

        Returns
        -------
        `List[int]`
            Array of tick positions
        """
        res = [bound]
        while bound >= 0:
            bound -= 7
            if bound > 0:
                res.append(bound)
        return res

    def fmt_chart(self) -> None:
        """Format the 3D Axes after rendering."""
        self.chart.set_title(self.title,
                             fontdict={"fontsize": 18, "family": "Poppins"})

        self.chart.set_xticks(self.gen_ticks(self.bounds["x"]))
        self.chart.set_yticks(self.gen_ticks(self.bounds["y"]))

        self.chart.set_xticklabels(np.arange(0, self.bounds["x"], 7))
        self.chart.set_yticklabels(np.arange(0, self.bounds["y"], 7))

        self.chart.set_xlabel("Win/Tie Score")
        self.chart.set_ylabel("Lose/Tie Score")
        self.chart.set_zlabel("Freq")
