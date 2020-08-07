"""Graph a heatmap of NFL-scores.

usage: python3 graph.py
"""
from typing import Dict

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import requests
from bs4 import BeautifulSoup
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LogNorm
from mpl_toolkits.mplot3d import Axes3D


def setup_plt():
    """Format the plot before rendering."""
    plt.style.use("ggplot")


def fmt_plt():
    """Format the plot after rendering."""
    plt.tight_layout()


def gen_ticks(bound: int):
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


def fmt_chart(chart: Axes3D, bounds: Dict[str, int]):
    """Format the 3D Axes after rendering.

    Parameters
    ----------
    chart : `Axes3D`
        The object describing the heatmap

    bounds : `Dict[str, int]`
        The max-value for x/y axes
    """
    chart.set_xticks(gen_ticks(bounds["x"]))
    chart.set_yticks(gen_ticks(bounds["y"]))

    chart.set_yticklabels(np.arange(0, bounds["y"], 7))
    chart.set_xticklabels(np.arange(0, bounds["x"], 7))

    chart.set_xlabel("Win/Tie Score")
    chart.set_ylabel("Lose/Tie Score")
    chart.set_zlabel("Freq")


def rotate_chart(chart: Axes3D):
    """Set the rotation of the camera to view to plot.

    Parameters
    ----------
    chart : `Axes3D`
        Object describing the graph
    """
    chart.view_init(60, 30)
    plt.show()


def main():
    """Run all executable code."""
    fig = plt.figure(dpi=120, figsize=(16, 9))

    chart: Axes3D = fig.add_subplot(111, projection="3d")

    url = "https://www.pro-football-reference.com/boxscores/game-scores.htm"

    res = requests.get(url)

    page = BeautifulSoup(res.text, "html.parser")

    games = page.find(id="games").find("tbody").find_all("tr")

    scores = [{"win": int(game.find("td", {"data-stat": "pts_win"}).text),
               "lose": int(game.find("td", {"data-stat": "pts_lose"}).text),
               "freq": int(game.find("td", {"data-stat": "counter"}).text)}
              for game in games]

    win_bound = max(scores, key=lambda obj: obj["win"])["win"]
    freq_bound = max(scores, key=lambda obj: obj["freq"])["freq"]
    bounds = {"x": win_bound, "y": win_bound, "z": freq_bound}

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

    norms = LogNorm(vmin=1, vmax=freq_bound)
    ramp = ScalarMappable(norm=norms, cmap=cm.get_cmap("Reds"))
    colors = [ramp.to_rgba(freq) if freq > 0 else (0, 0, 0, 0)
              for freq in bar_heights]

    chart.bar3d(
        anchor_x,
        anchor_y,
        anchor_z,
        bar_widths,
        bar_depths,
        bar_heights,
        color=colors,
        shade=True)

    fmt_plt()
    fmt_chart(chart, bounds)

    rotate_chart(chart)


if __name__ == "__main__":
    main()
