"""Schematic figures for the tutorial `03-Understanding_MOM5_MOM6_grids.ipynb`.

The plotting code lives here so that the notebook only shows the figures.
Each public function draws one figure.

Index convention (MOM5 and MOM6): the velocity and corner points that share
the index (i, j) with a tracer point lie to its east and/or north:

- MOM5 B-grid: U(i, j) is the north-east corner of T-cell (i, j).
- MOM6 C-grid: u(i, j) is on the east face, v(i, j) on the north face and
  q(i, j) on the north-east corner of h-cell (i, j).
"""

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerTuple

# Colours used consistently in every figure
T_COLOR = "#2E5C8A"     # tracer points (T in MOM5, h in MOM6)
U_COLOR = "#C0392B"     # u-velocity (C-grid u-point; red half of the B-grid U-point)
V_COLOR = "#1E8449"     # v-velocity (C-grid v-point; green half of the B-grid U-point)
Q_COLOR = "#7D3C98"     # corner / vorticity point (q in MOM6)
GRID_COLOR = "#888888"
CELL_FILL = "#EAF0F7"

# MOM5's U-point carries both u and v, so we draw it as the C-grid u marker
# (red, pointing right) and v marker (green, pointing up) on top of each other.
U_ALPHA = 0.7
FAINT = 0.2             # alpha for points that belong to neighbouring cells

TRACER_LABEL = "Tracer point (e.g. T, S, ...)"
HANDLER_MAP = {tuple: HandlerTuple(ndivide=1)}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _setup_axes(ax, xlim, ylim, title=None):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    if title:
        ax.set_title(title, fontsize=13, fontweight="bold", pad=10)


def _cell(ax, x0, y0, filled=False):
    ax.add_patch(mpatches.Rectangle((x0, y0), 1, 1, fill=filled, facecolor=CELL_FILL,
                                    edgecolor=GRID_COLOR, linewidth=1.3, zorder=1))


def _T(ax, x, y, ms=11, alpha=1):
    ax.plot(x, y, "o", color=T_COLOR, markersize=ms, alpha=alpha, zorder=5)


def _U(ax, x, y, ms=10, alpha=U_ALPHA):
    """MOM5 B-grid U-point: u and v co-located."""
    ax.plot(x, y, ">", color=U_COLOR, markersize=ms, alpha=alpha, zorder=5)
    ax.plot(x, y, "^", color=V_COLOR, markersize=ms, alpha=alpha, zorder=5)


def _u(ax, x, y, ms=10, alpha=1):
    ax.plot(x, y, ">", color=U_COLOR, markersize=ms, alpha=alpha, zorder=5)


def _v(ax, x, y, ms=10, alpha=1):
    ax.plot(x, y, "^", color=V_COLOR, markersize=ms, alpha=alpha, zorder=5)


def _q(ax, x, y, ms=7, alpha=1):
    ax.plot(x, y, "D", color=Q_COLOR, markersize=ms, alpha=alpha, zorder=5)


def _label(ax, text, xy, color, dx=0.06, dy=0.06, ha="left", va="bottom", fontsize=9.5):
    ax.text(xy[0] + dx, xy[1] + dy, text, color=color, ha=ha, va=va, fontsize=fontsize, zorder=6)


def _arrow(ax, start, end, color, text, text_xy, rotation=0, ha="center", va="center"):
    ax.annotate("", xy=end, xytext=start,
                arrowprops=dict(arrowstyle="<->", color=color, lw=1.4, shrinkA=0, shrinkB=0))
    ax.text(*text_xy, text, color=color, fontsize=9.5, rotation=rotation, ha=ha, va=va)


def _handle(marker, color, ms=8):
    return plt.Line2D([], [], marker=marker, color=color, linestyle="", markersize=ms)


def U_handle(ms=8):
    """Legend handle for the MOM5 U-point (use with ``handler_map=HANDLER_MAP``)."""
    return (plt.Line2D([], [], marker=">", color=U_COLOR, alpha=U_ALPHA, linestyle="", markersize=ms),
            plt.Line2D([], [], marker="^", color=V_COLOR, alpha=U_ALPHA, linestyle="", markersize=ms))


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

def bgrid_vs_cgrid():
    """Four neighbouring cells on the MOM5 B-grid and on the MOM6 C-grid."""
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.8))

    ax = axes[0]
    _setup_axes(ax, (-0.3, 2.3), (-0.3, 2.3), "MOM5: B-grid")
    for i in range(2):
        for j in range(2):
            _cell(ax, i, j)
            _T(ax, i + 0.5, j + 0.5)
            _U(ax, i + 1, j + 1)                  # north-east corner
    ax.text(1.0, -0.2, "u and v share one point per cell\n(north-east corner)",
            ha="center", va="top", fontsize=9.5, style="italic")

    ax = axes[1]
    _setup_axes(ax, (-0.3, 2.3), (-0.3, 2.3), "MOM6: C-grid")
    for i in range(2):
        for j in range(2):
            _cell(ax, i, j)
            _T(ax, i + 0.5, j + 0.5)
            _u(ax, i + 1, j + 0.5)                # east face
            _v(ax, i + 0.5, j + 1)                # north face
            _q(ax, i + 1, j + 1)                  # north-east corner
    ax.text(1.0, -0.2, "u on the east face, v on the north face,\nq on the north-east corner",
            ha="center", va="top", fontsize=9.5, style="italic")

    handles = [_handle("o", T_COLOR), U_handle(), _handle(">", U_COLOR),
               _handle("^", V_COLOR), _handle("D", Q_COLOR, ms=7)]
    labels = [TRACER_LABEL, "U-point (B-grid: u & v together)", "u-point (C-grid)",
              "v-point (C-grid)", "q-point (C-grid: vorticity)"]
    fig.legend(handles, labels, handler_map=HANDLER_MAP, loc="lower center", ncol=3,
               bbox_to_anchor=(0.5, -0.12), frameon=False, fontsize=9.5)
    fig.suptitle("Same patch of ocean: B-grid vs. C-grid point placement",
                 fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    plt.show()


def bgrid_cells():
    """A single MOM5 T-cell, and four neighbouring T-cells with (i, j) indices."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.2))

    # --- Left: a single T-cell -------------------------------------------
    ax = axes[0]
    _setup_axes(ax, (-0.3, 1.6), (-0.4, 1.4), "A single MOM5 T-cell")
    _cell(ax, 0, 0, filled=True)
    _T(ax, 0.5, 0.5, ms=12)
    _label(ax, "T(i,j)\ntracers, thickness,\ndensity, ...", (0.5, 0.5), T_COLOR,
           dx=0, dy=-0.08, ha="center", va="top")
    for (x, y) in [(0, 0), (1, 0), (0, 1)]:
        _U(ax, x, y, ms=11, alpha=FAINT)          # belong to neighbouring cells
    _U(ax, 1, 1, ms=11)
    _label(ax, "U(i,j)\nu and v", (1, 1), U_COLOR, dx=0.07, dy=0.03)
    ax.text(0.5, -0.12, "U(i,j) is the north-east corner of T-cell (i,j).\n"
                        "The faded corners belong to neighbouring cells.",
            ha="center", va="top", fontsize=9.5, style="italic")

    # --- Right: four neighbouring T-cells ----------------------------------
    ax = axes[1]
    _setup_axes(ax, (-0.2, 2.5), (-0.2, 2.4), "Four neighbouring MOM5 T-cells")
    names = {0: "i", 1: "i+1"}, {0: "j", 1: "j+1"}
    for i in range(2):
        for j in range(2):
            _cell(ax, i, j)
            _T(ax, i + 0.5, j + 0.5, ms=10)
            _label(ax, f"T({names[0][i]},{names[1][j]})", (i + 0.5, j + 0.5), T_COLOR,
                   dx=0, dy=-0.09, ha="center", va="top", fontsize=9)
            _U(ax, i + 1, j + 1, ms=9)
    _label(ax, "U(i,j)", (1, 1), U_COLOR, dx=0.06, dy=0.04, fontsize=9)

    ax.legend([_handle("o", T_COLOR, 10), U_handle(9)], ["T-point", "U-point (u & v co-located)"],
              handler_map=HANDLER_MAP, loc="upper center", bbox_to_anchor=(0.5, 0.0),
              ncol=2, frameon=False, fontsize=9.5)

    fig.suptitle("MOM5 Arakawa B-grid", fontsize=15, fontweight="bold", y=1.02)
    fig.tight_layout()
    plt.show()


def bgrid_metrics():
    """MOM5 grid metrics: T-cell widths dxt/dyt and U-cell widths dxu/dyu."""
    fig, ax = plt.subplots(figsize=(7.0, 6.6))
    _setup_axes(ax, (-0.35, 1.8), (-0.45, 1.75), "MOM5 grid-cell metrics (grid file)")

    _cell(ax, 0, 0, filled=True)                  # T-cell
    ax.add_patch(mpatches.Rectangle((0.5, 0.5), 1, 1, fill=False, edgecolor=U_COLOR,
                                    linewidth=1.3, linestyle="--", zorder=2))   # U-cell

    _T(ax, 0.5, 0.5, ms=12)
    _label(ax, "T(i,j)", (0.5, 0.5), T_COLOR, dx=-0.06, dy=-0.06, ha="right", va="top", fontsize=10)
    _arrow(ax, (0, 0.15), (1, 0.15), T_COLOR, "dxt", (0.5, 0.2), va="bottom")
    _arrow(ax, (0.15, 0), (0.15, 1), T_COLOR, "dyt", (0.2, 0.35), rotation=90, ha="left")

    _U(ax, 1, 1, ms=13)
    _label(ax, "U(i,j)\n(u & v)", (1, 1), U_COLOR, dx=-0.06, dy=0.06, ha="right", fontsize=10)
    _arrow(ax, (0.5, 1.35), (1.5, 1.35), U_COLOR, "dxu", (1.0, 1.4), va="bottom")
    _arrow(ax, (1.35, 0.5), (1.35, 1.5), U_COLOR, "dyu", (1.4, 0.75), rotation=90, ha="left")

    ax.text(0.7, -0.15,
            "dxt, dyt: width/height of the T-cell (solid)\n"
            "dxu, dyu: width/height of the U-cell (dashed), offset half a cell north-east",
            ha="center", va="top", fontsize=9, style="italic")
    fig.tight_layout()
    plt.show()


def cgrid_cells():
    """A single MOM6 h-cell, and four neighbouring h-cells with (i, j) indices."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.2))

    # --- Left: a single h-cell -------------------------------------------
    ax = axes[0]
    _setup_axes(ax, (-0.3, 1.7), (-0.4, 1.45), "A single MOM6 h-cell")
    _cell(ax, 0, 0, filled=True)
    _T(ax, 0.5, 0.5, ms=12)
    _label(ax, "h(i,j)\ntracers, thickness", (0.5, 0.5), T_COLOR,
           dx=0, dy=-0.08, ha="center", va="top")
    _u(ax, 0, 0.5, ms=11, alpha=FAINT)            # faded: neighbouring cells
    _v(ax, 0.5, 0, ms=11, alpha=FAINT)
    for (x, y) in [(0, 0), (1, 0), (0, 1)]:
        _q(ax, x, y, ms=8, alpha=FAINT)
    _u(ax, 1, 0.5, ms=11)
    _label(ax, "u(i,j)\nx-velocity", (1, 0.5), U_COLOR, dx=0.07, dy=0, va="center")
    _v(ax, 0.5, 1, ms=11)
    _label(ax, "v(i,j)\ny-velocity", (0.5, 1), V_COLOR, dx=0.07, dy=0.03)
    _q(ax, 1, 1, ms=8)
    _label(ax, "q(i,j)\nvorticity", (1, 1), Q_COLOR, dx=0.07, dy=0.03)
    ax.text(0.5, -0.12, "u, v and q with index (i,j) lie on the east face, north face\n"
                        "and north-east corner. Faded points belong to neighbouring cells.",
            ha="center", va="top", fontsize=9.5, style="italic")

    # --- Right: four neighbouring h-cells ----------------------------------
    ax = axes[1]
    _setup_axes(ax, (-0.2, 2.5), (-0.2, 2.4), "Four neighbouring MOM6 h-cells")
    names = {0: "i", 1: "i+1"}, {0: "j", 1: "j+1"}
    for i in range(2):
        for j in range(2):
            _cell(ax, i, j)
            _T(ax, i + 0.5, j + 0.5, ms=10)
            _label(ax, f"h({names[0][i]},{names[1][j]})", (i + 0.5, j + 0.5), T_COLOR,
                   dx=0, dy=-0.09, ha="center", va="top", fontsize=9)
            _u(ax, i + 1, j + 0.5, ms=9)
            _v(ax, i + 0.5, j + 1, ms=9)
            _q(ax, i + 1, j + 1, ms=6.5)
    _label(ax, "u(i,j)", (1, 0.5), U_COLOR, dx=0.06, dy=0.04, fontsize=9)
    _label(ax, "v(i,j)", (0.5, 1), V_COLOR, dx=0.06, dy=0.04, fontsize=9)
    _label(ax, "q(i,j)", (1, 1), Q_COLOR, dx=0.06, dy=0.04, fontsize=9)

    ax.legend([_handle("o", T_COLOR, 9), _handle(">", U_COLOR, 9), _handle("^", V_COLOR, 9),
               _handle("D", Q_COLOR, 6.5)],
              ["h-point", "u-point", "v-point", "q-point"],
              loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=4, frameon=False, fontsize=9.5)

    fig.suptitle("MOM6 Arakawa C-grid", fontsize=15, fontweight="bold", y=1.02)
    fig.tight_layout()
    plt.show()


def cgrid_metrics():
    """MOM6 grid metrics: dxt/dyt at h-points, dyCu at u-points, dxCv at v-points."""
    fig, ax = plt.subplots(figsize=(6.4, 6.0))
    _setup_axes(ax, (-0.25, 1.45), (-0.4, 1.35), "MOM6 grid-cell metrics (static file)")

    _cell(ax, 0, 0, filled=True)
    _T(ax, 0.5, 0.5, ms=12)
    _label(ax, "h(i,j)", (0.5, 0.5), T_COLOR, dx=0.05, dy=0.05, fontsize=10)
    _arrow(ax, (0, 0.25), (1, 0.25), T_COLOR, "dxt", (0.5, 0.3), va="bottom")
    _arrow(ax, (0.25, 0), (0.25, 1), T_COLOR, "dyt", (0.3, 0.7), rotation=90, ha="left")

    _u(ax, 1, 0.5, ms=12)
    _label(ax, "u(i,j)", (1, 0.5), U_COLOR, dx=0.06, dy=0, va="center", fontsize=10)
    _arrow(ax, (0.88, 0), (0.88, 1), U_COLOR, "dyCu", (0.83, 0.25), rotation=90, ha="right")

    _v(ax, 0.5, 1, ms=12)
    _label(ax, "v(i,j)", (0.5, 1), V_COLOR, dx=0, dy=0.06, ha="center", fontsize=10)
    _arrow(ax, (0, 0.88), (1, 0.88), V_COLOR, "dxCv", (0.75, 0.83), va="top")

    _q(ax, 1, 1, ms=9)
    _label(ax, "q(i,j)", (1, 1), Q_COLOR, dx=0.05, dy=0.04, fontsize=10)

    ax.text(0.6, -0.12,
            "dxt, dyt: width/height of the h-cell\n"
            "dyCu: length of the east face (at u)   |   dxCv: length of the north face (at v)\n"
            "areacello, areacello_cu, areacello_cv, areacello_bu: cell areas",
            ha="center", va="top", fontsize=9, style="italic")
    fig.tight_layout()
    plt.show()
