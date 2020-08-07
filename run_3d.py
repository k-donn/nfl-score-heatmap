"""
Show a heatmap of all NFL scores.

usage: python3.8 run.py [-h]

optional arguments:
  -h, --help  show this help message and exit
"""

import sys

from PyQt5.QtWidgets import QApplication

from pyqt import pyqt_graph_3d


def main():
    """Execute all code."""
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__)
        sys.exit()

    app = QApplication(sys.argv)

    ex = pyqt_graph_3d.App()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
