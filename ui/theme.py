# ui/theme.py
"""
Shared imports, colour tokens, and algorithm imports.
All Mixin modules import from here with:
    from .theme import *
"""
import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Patch
import networkx as nx
from collections import deque
import heapq
import math

# ─── Import thuật toán từ src ─────────────────────────────────────────────────
_SRC = os.path.join(os.path.dirname(__file__), "..", "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
try:
    from graph_algorithms.algorithms.minimum_spanning_tree import prim, kruskal
    from graph_algorithms.algorithms.advanced import (
        fleury, hierholzer, ford_fulkerson, check_euler_condition
    )
    _ALGO_AVAILABLE = True
    _ALGO_ERROR = ""
except ImportError as _e:
    _ALGO_AVAILABLE = False
    _ALGO_ERROR = str(_e)
    prim = kruskal = fleury = hierholzer = ford_fulkerson = check_euler_condition = None

# ─── Colour tokens (light professional theme) ─────────────────────────────────
BG      = "#f0f2f5"
PANEL   = "#ffffff"
BORDER  = "#d0d7de"
ACCENT  = "#2563eb"
ACCENT2 = "#0891b2"
SUCCESS = "#16a34a"
ERROR   = "#dc2626"
WARNING = "#d97706"
TEXT    = "#1e293b"
TEXT2   = "#475569"

GRAPH_BG     = "#1e293b"
NODE_DEFAULT = "#3b82f6"
NODE_HI      = "#f59e0b"
EDGE_DEFAULT = "#94a3b8"
EDGE_HI      = "#f97316"
