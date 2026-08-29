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
except ImportError as _e:
    _ALGO_AVAILABLE = False
    _ALGO_ERROR = str(_e)

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

GRAPH_BG    = "#1e293b"
NODE_DEFAULT= "#3b82f6"
NODE_HI     = "#f59e0b"
EDGE_DEFAULT= "#94a3b8"
EDGE_HI     = "#f97316"


# ═══════════════════════════════════════════════════════════════════════════════
class GraphApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Graph Algorithms Visualizer")
        self.root.geometry("1300x820")
        self.root.minsize(1100, 700)
        self.root.configure(bg=BG)

        self.graph: dict[str, list[tuple[str, float]]] = {}
        self.history = []
        self.directed   = tk.BooleanVar(value=False)
        self._pos: dict = {}

        self._build_styles()
        self._build_ui()

    # ── ttk styles ────────────────────────────────────────────────────────────
    def _build_styles(self):
        s = ttk.Style()
        s.theme_use("clam")

        s.configure("TNotebook", background=BG, borderwidth=0, tabmargins=0)
        s.configure("TNotebook.Tab",
                    background=PANEL, foreground=TEXT2,
                    padding=[18, 8], font=("Segoe UI", 10),
                    borderwidth=1, relief="flat")
        s.map("TNotebook.Tab",
              background=[("selected", ACCENT)],
              foreground=[("selected", "white")])

        s.configure("TFrame",  background=PANEL)
        s.configure("TLabel",  background=PANEL, foreground=TEXT)
        s.configure("TRadiobutton", background=PANEL, foreground=TEXT, font=("Segoe UI", 9))
        s.configure("TCheckbutton", background=PANEL, foreground=TEXT, font=("Segoe UI", 9))
        s.configure("Vertical.TScrollbar",
                    background=PANEL, troughcolor=BG, arrowcolor=TEXT2, borderwidth=0)

    # ── root layout ──────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── title bar ──────────────────────────────────────────────────────
        title_bar = tk.Frame(self.root, bg=ACCENT, height=50)
        title_bar.pack(fill=tk.X)
        tk.Label(title_bar,
                 text="  GRAPH ALGORITHMS VISUALIZER",
                 font=("Segoe UI", 14, "bold"),
                 bg=ACCENT, fg="white").pack(side=tk.LEFT, pady=10, padx=8)

        # ── main area ──────────────────────────────────────────────────────
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # left sidebar
        sidebar = tk.Frame(main, bg=BG, width=260)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        sidebar.pack_propagate(False)
        self._build_sidebar(sidebar)

        # right notebook
        right = tk.Frame(main, bg=BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._build_notebook(right)

    # ═══════════════════════════════════════════════════════════════════════════
    # SIDEBAR
    # ═══════════════════════════════════════════════════════════════════════════
    def _build_sidebar(self, p):
        # ── graph type ─────────────────────────────────────────────────────
        gf = self._section(p, "Loại đồ thị")
        ttk.Radiobutton(gf, text="Vô hướng (Undirected)",
                        variable=self.directed, value=False,
                        command=self._type_changed).pack(anchor="w", pady=2)
        ttk.Radiobutton(gf, text="Có hướng (Directed)",
                        variable=self.directed, value=True,
                        command=self._type_changed).pack(anchor="w", pady=2)

        # ── add node ───────────────────────────────────────────────────────
        self.sec_node = self._section(p, "Thêm đỉnh (Node)")
        tk.Label(self.sec_node, text="Tên đỉnh:", bg=PANEL, fg=TEXT2,
                 font=("Segoe UI", 9)).pack(anchor="w")
        self.e_node = self._entry(self.sec_node)
        self.e_node.pack(fill=tk.X, pady=(3, 6))
        self.e_node.bind("<Return>", lambda _: self._add_node())
        self.e_node.bind("<KeyRelease>", self._check_add_node_input)
        self.e_node.bind("<FocusIn>", self._check_add_node_input)
        self.e_node.bind("<FocusOut>", self._check_add_node_input)

        self.btn_add_node = self._btn(self.sec_node, "Thêm đỉnh", self._add_node, color="#e2e8f0", fg="#64748b")
        self.btn_add_node.pack(fill=tk.X)

        # ── add edge ───────────────────────────────────────────────────────
        self.sec_edge = self._section(p, "Thêm cạnh (Edge)")
        for lbl, attr in [("Từ:", "ef"),
                           ("Đến:",  "et"),
                           ("Trọng số:",  "ew")]:
            tk.Label(self.sec_edge, text=lbl, bg=PANEL, fg=TEXT2,
                     font=("Segoe UI", 9)).pack(anchor="w")
            e = self._entry(self.sec_edge)
            e.pack(fill=tk.X, pady=(3, 6))
            setattr(self, attr, e)
        self.ew.insert(0, "1")
        self.ef.bind("<KeyRelease>", self._check_add_edge_input)
        self.ef.bind("<Return>", lambda _: self.et.focus_set())
        self.et.bind("<KeyRelease>", self._check_add_edge_input)
        self.et.bind("<Return>", lambda _: self.ew.focus_set())
        self.ew.bind("<KeyRelease>", self._check_add_edge_input)  # Lỗi 1: thiếu bind ew
        self.ew.bind("<Return>", lambda _: self._add_edge())       # Lỗi 2: Return phải ở ew

        self.btn_add_edge = self._btn(self.sec_edge, "Thêm cạnh", self._add_edge, color="#e2e8f0", fg="#64748b")
        self.btn_add_edge.pack(fill=tk.X)

        # ── action buttons ─────────────────────────────────────────────────
        bf = tk.Frame(p, bg=BG)
        bf.pack(side=tk.BOTTOM, fill=tk.X, pady=(4, 0))
        self._btn(bf, "Làm mới",    self._refresh,  ACCENT2).pack(fill=tk.X, pady=(0, 4))
        self._btn(bf, "Xóa sạch toàn bộ đồ thị", self._clear, ERROR).pack(fill=tk.X)

        # ── graph info ─────────────────────────────────────────────────────
        inf = self._section(p, "Đồ thị hiện tại", expand=True)
        self.info_t = tk.Text(inf, state="disabled",
                              bg="#f8fafc", fg=TEXT, relief="flat",
                              font=("Consolas", 8), wrap="word",
                              borderwidth=1, height=2)
        self.info_t.pack(fill=tk.BOTH, expand=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # NOTEBOOK – 5 TABS
    # ═══════════════════════════════════════════════════════════════════════════
    def _build_notebook(self, p):
        self.nb = ttk.Notebook(p)
        self.nb.pack(fill=tk.BOTH, expand=True)
        for name, fn in [
            ("1. Đồ thị",              self._tab1),
            ("2. Biểu diễn",           self._tab2),
            ("3. Duyệt BFS/DFS",       self._tab3),
            ("4. Hai phía",            self._tab4),
            ("5. Đường ngắn nhất",     self._tab5),
            ("6. Thuật toán nâng cao", self._tab6),
            ("7. Bài toán thực tế",    self._tab7),
        ]:
            fr = tk.Frame(self.nb, bg=BG)
            self.nb.add(fr, text=name)
            fn(fr)

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 1 – GRAPH VISUALIZATION
    # ═══════════════════════════════════════════════════════════════════════════
    def _tab1(self, p):
        # toolbar
        tb = tk.Frame(p, bg=PANEL, relief="flat", bd=0)
        tb.pack(fill=tk.X, padx=8, pady=(8, 4))
        
        tk.Label(tb, text="Trực quan hóa",
                 font=("Segoe UI", 12, "bold"),
                 bg=PANEL, fg=TEXT).pack(side=tk.LEFT, padx=(10, 15), pady=8)

        # Xóa tools area
        del_tb = tk.Frame(tb, bg=PANEL)
        del_tb.pack(side=tk.LEFT, fill=tk.Y, pady=4)
        
        self.sec_del = tk.Label(del_tb, text="Thao tác xóa:", bg=PANEL, fg=ACCENT, font=("Segoe UI", 9, "bold"))
        self.sec_del.pack(side=tk.LEFT, padx=(0, 5))

        # Delete Node
        self.e_del_node = self._entry(del_tb, width=6)
        self.e_del_node.pack(side=tk.LEFT, padx=(0, 4))
        self.e_del_node.bind("<Return>", lambda _: self._delete_node())
        self.e_del_node.bind("<KeyRelease>", self._check_del_node_input)
        self.e_del_node.bind("<FocusIn>", self._check_del_node_input)
        self.e_del_node.bind("<FocusOut>", self._check_del_node_input)
        
        self.btn_del_node = self._btn(del_tb, "Xoá đỉnh", self._delete_node, color="#e2e8f0", fg="#64748b")
        self.btn_del_node.pack(side=tk.LEFT, padx=(0, 10))

        # Delete Edge
        tk.Label(del_tb, text="Cạnh:", bg=PANEL, fg=TEXT2, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 2))
        
        self.e_del_ef = self._entry(del_tb, width=4)
        self.e_del_ef.pack(side=tk.LEFT, padx=(0, 2))
        self.e_del_ef.bind("<KeyRelease>", self._check_del_edge_input)

        tk.Label(del_tb, text="→", bg=PANEL, fg=TEXT2).pack(side=tk.LEFT)

        self.e_del_et = self._entry(del_tb, width=4)
        self.e_del_et.pack(side=tk.LEFT, padx=(2, 4))
        self.e_del_et.bind("<KeyRelease>", self._check_del_edge_input)
        self.e_del_et.bind("<Return>", lambda _: self._delete_edge())

        self.btn_del_edge = self._btn(del_tb, "Xoá cạnh", self._delete_edge, color="#e2e8f0", fg="#64748b")
        self.btn_del_edge.pack(side=tk.LEFT)

        self.btn_save_img = self._btn(tb, "Lưu hình", self._save_img, SUCCESS)
        self.btn_save_img.pack(side=tk.RIGHT, padx=6, pady=6)
        
        self.btn_redraw = self._btn(tb, "Vẽ lại",   self.draw,      ACCENT2)
        self.btn_redraw.pack(side=tk.RIGHT, padx=(0, 4), pady=6)

        self.btn_undo = self._btn(tb, "Quay lại", self._undo, WARNING)
        self.btn_undo.pack(side=tk.RIGHT, padx=(0, 4), pady=6)
        
        ttk.Separator(p, orient="horizontal").pack(fill=tk.X, padx=8)

        # matplotlib canvas
        self.fig1 = Figure(figsize=(9, 5.5), facecolor=GRAPH_BG)
        self.ax1 = self.fig1.add_subplot(111)
        self.ax1.set_facecolor(GRAPH_BG)
        self.cv1 = FigureCanvasTkAgg(self.fig1, p)
        self.cv1.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.draw()

    @staticmethod
    def _hide_6(text):
        """Thay thế số 6 thành 6 có dấu chấm trên đầu (6̇) để dễ phân biệt với 9."""
        return str(text).replace("6", "6\u0307")

    def draw(self, ax=None, cv=None, hi_n=None, hi_e=None,
             node_colors: dict = None, title=""):
        if ax is None: ax = self.ax1
        if cv is None: cv = self.cv1
        ax.clear()
        ax.set_facecolor(GRAPH_BG)
        ax.figure.patch.set_facecolor(GRAPH_BG)

        if not self.graph:
            ax.text(0.5, 0.5,
                    "Chưa có đồ thị\nThêm đỉnh và cạnh ở bảng bên trái",
                    ha="center", va="center", fontsize=12,
                    color="#94a3b8", transform=ax.transAxes)
            self._update_action_buttons()
            cv.draw(); return

        G = self._nxg()
        if set(G.nodes()) != set(self._pos.keys()):
            n = len(G.nodes())
            if n <= 10:
                self._pos = nx.circular_layout(G)
            else:
                self._pos = nx.spring_layout(G, seed=42, k=2)
        pos = self._pos

        nc = [node_colors.get(n, NODE_DEFAULT) if node_colors
              else (NODE_HI if hi_n and n in hi_n else NODE_DEFAULT)
              for n in G.nodes()]
        ec = [EDGE_HI if hi_e and (e in hi_e or (e[1], e[0]) in hi_e)
              else EDGE_DEFAULT for e in G.edges()]

        d = self.directed.get()
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=nc,
                               node_size=900, edgecolors="white", linewidths=1.5)
        nx.draw_networkx_labels(G, pos, ax=ax,
                                font_color="white", font_size=11, font_weight="bold")
        if d:
            nx.draw_networkx_edges(G, pos, ax=ax, edge_color=ec, width=2,
                                   arrows=True, arrowsize=20,
                                   connectionstyle="arc3,rad=0.08")
        else:
            nx.draw_networkx_edges(G, pos, ax=ax, edge_color=ec, width=2,
                                   arrows=False)

        wlbl = {(u, v): str(int(w) if w == int(w) else w)
                for u, v, dat in G.edges(data=True)
                if (w := dat.get("weight", 1)) != 1}
        if wlbl:
            lpos = 0.3 if d else 0.5
            nx.draw_networkx_edge_labels(G, pos, wlbl, ax=ax,
                                         label_pos=lpos,
                                         font_color="#fbbf24", font_size=9,
                                         bbox=dict(boxstyle="round,pad=0.2",
                                                   fc="#334155", alpha=0.9))
        if title:
            ax.set_title(title, color="white", fontsize=11, pad=6)
        ax.axis("off"); cv.draw()
        self._update_action_buttons()

    def _save_img(self):
        fp = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("PDF", "*.pdf"), ("SVG", "*.svg")])
        if fp:
            self.fig1.savefig(fp, dpi=160, bbox_inches="tight", facecolor=GRAPH_BG)
            messagebox.showinfo("Đã lưu", f"Hình đồ thị đã lưu tại:\n{fp}")

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 2 – REPRESENTATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    def _tab2(self, p):
        tb = self._tab_toolbar(p, "Biểu diễn đồ thị")
        self._btn(tb, "Cập nhật", self._show_repr, ACCENT2).pack(
            side=tk.RIGHT, padx=8, pady=6)

        cols = tk.Frame(p, bg=BG)
        cols.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        for i, (ttl, attr) in enumerate([
            ("Ma trận kề\n(Adjacency Matrix)", "rm"),
            ("Danh sách kề\n(Adjacency List)",  "rl"),
            ("Danh sách cạnh\n(Edge List)",      "re"),
        ]):
            cols.columnconfigure(i, weight=1)
            cols.rowconfigure(0, weight=1)
            cf = tk.Frame(cols, bg=PANEL, relief="solid", bd=1)
            cf.grid(row=0, column=i, sticky="nsew", padx=4, pady=2)
            tk.Label(cf, text=ttl, font=("Segoe UI", 10, "bold"),
                     bg=PANEL, fg=ACCENT, justify="center").pack(pady=(10, 6))
            ttk.Separator(cf, orient="horizontal").pack(fill=tk.X, padx=8)
            t = tk.Text(cf, bg="#f8fafc", fg=TEXT,
                        font=("Consolas", 10), relief="flat",
                        state="disabled", wrap="none", padx=8, pady=6)
            t.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
            sb = ttk.Scrollbar(cf, orient="vertical", command=t.yview)
            t.configure(yscrollcommand=sb.set)
            setattr(self, attr, t)
        self._show_repr()

    def _show_repr(self):
        nodes = sorted(self.graph)

        # Adjacency Matrix
        if not nodes:
            self._settext(self.rm, "(Đồ thị trống)")
        else:
            idx = {n: i for i, n in enumerate(nodes)}
            sz  = len(nodes)
            mat = [[0]*sz for _ in range(sz)]
            for u in self.graph:
                for v, w in self.graph[u]:
                    mat[idx[u]][idx[v]] = w
                    if not self.directed.get():
                        mat[idx[v]][idx[u]] = w
            W   = max(len(str(n)) for n in nodes) + 2
            hdr = " "*W + "".join(f"{n:>{W}}" for n in nodes)
            sep = " "*W + "─"*(W*sz)
            rows = [f"{nodes[i]:>{W-1}} │" +
                    "".join(f"{mat[i][j]:>{W}}" for j in range(sz))
                    for i in range(sz)]
            self._settext(self.rm, "\n".join([hdr, sep] + rows))

        # Adjacency List
        if not self.graph:
            self._settext(self.rl, "(Đồ thị trống)")
        else:
            lines = []
            for u in nodes:
                nbs = sorted(self.graph[u], key=lambda x: x[0])
                if nbs:
                    pts = [f"{v}({int(w) if w==int(w) else w})" if w != 1 else v
                           for v, w in nbs]
                    lines.append(f"{u} :  " + "  →  ".join(pts))
                else:
                    lines.append(f"{u} :  ∅")
            self._settext(self.rl, "\n\n".join(lines))

        # Edge List
        if not self.graph:
            self._settext(self.re, "(Đồ thị trống)")
        else:
            seen, edges = set(), []
            for u in sorted(self.graph):
                for v, w in sorted(self.graph[u], key=lambda x: x[0]):
                    key = tuple(sorted([u, v])) if not self.directed.get() else (u, v)
                    if key not in seen:
                        seen.add(key)
                        edges.append((u, v, w))
            arr = "→" if self.directed.get() else "—"
            lines = ["(Từ, Đến, Trọng số)\n"]
            lines += [f"  ({u})  {arr}  ({v})    w = {int(w) if w==int(w) else w}"
                      for u, v, w in edges]
            self._settext(self.re, "\n".join(lines))

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 3 – TRAVERSAL
    # ═══════════════════════════════════════════════════════════════════════════
    def _tab3(self, p):
        tb = self._tab_toolbar(p, "Duyệt đồ thị: BFS & DFS")

        ctrl = tk.Frame(p, bg=PANEL, relief="solid", bd=1)
        ctrl.pack(fill=tk.X, padx=8, pady=(0, 6))
        tk.Label(ctrl, text="Đỉnh xuất phát:", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 10)).grid(row=0, column=0, padx=12, pady=10, sticky="w")
        self.e_ts = self._entry(ctrl, width=12)
        self.e_ts.grid(row=0, column=1, padx=6, pady=10, sticky="ew")
        ctrl.columnconfigure(1, weight=1)
        self._btn(ctrl, "▶ BFS", self._bfs_run).grid(row=0, column=2, padx=6, pady=10)
        self._btn(ctrl, "▶ DFS", self._dfs_run, ACCENT2).grid(row=0, column=3, padx=6, pady=10)

        # two result columns
        cols = tk.Frame(p, bg=BG)
        cols.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        for col, (lbl, clr, ra, ma, ca) in enumerate([
            ("BFS – Breadth First Search", ACCENT,  "rb", "mb", "cb"),
            ("DFS – Depth First Search",   ACCENT2, "rd", "md", "cd"),
        ]):
            cols.columnconfigure(col, weight=1)
            cols.rowconfigure(0, weight=1)
            cf = tk.Frame(cols, bg=PANEL, relief="solid", bd=1)
            cf.grid(row=0, column=col, sticky="nsew", padx=4, pady=2)

            tk.Label(cf, text=lbl, font=("Segoe UI", 10, "bold"),
                     bg=PANEL, fg=clr).pack(pady=(10, 6))
            ttk.Separator(cf, orient="horizontal").pack(fill=tk.X, padx=8)

            tk.Label(cf, text="Kết quả thuật toán:",
                     bg=PANEL, fg=TEXT2, font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(8, 2))
            rt = tk.Text(cf, height=3, bg="#f0fdf4", fg=SUCCESS,
                         font=("Consolas", 11), relief="flat", state="disabled", padx=6, pady=4)
            rt.pack(fill=tk.X, padx=12, pady=(0, 10))
            setattr(self, ra, rt)

            ttk.Separator(cf, orient="horizontal").pack(fill=tk.X, padx=8)
            tk.Label(cf, text="Nhập kết quả chạy tay (A, B, C hoặc A→B→C):",
                     bg=PANEL, fg=TEXT2, font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(8, 2))
            me = self._entry(cf); me.pack(fill=tk.X, padx=12, pady=(0, 6))
            setattr(self, ma, me)

            cl = tk.Label(cf, text="─  Nhập rồi bấm So sánh  ─",
                          bg=PANEL, fg=TEXT2, font=("Segoe UI", 9),
                          justify="left", wraplength=320)
            cl.pack(anchor="w", padx=12, pady=(0, 6))
            setattr(self, ca, cl)

            def _mk(r, m, c):
                self._btn(cf, "So sánh",
                          lambda r=r, m=m, c=c: self._cmp_trav(r, m, c)
                          ).pack(fill=tk.X, padx=12, pady=(0, 12))
            _mk(ra, ma, ca)

    def _bfs_run(self):
        """Chạy BFS từ đỉnh do người dùng nhập và hiển thị thứ tự duyệt."""
        start = self.e_ts.get().strip()
        if not self.graph:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng tạo đồ thị trước.")
            return
        if not self._chk(start):
            return

        # BFS: dùng queue, duyệt các đỉnh kề theo thứ tự tên để kết quả ổn định.
        visited = {start}
        q = deque([start])
        order = []

        while q:
            u = q.popleft()
            order.append(u)
            for v, _w in sorted(self.graph.get(u, []), key=lambda x: str(x[0])):
                if v not in visited:
                    visited.add(v)
                    q.append(v)

        # Đồ thị có thể không liên thông: ghi rõ các đỉnh chưa được duyệt.
        unreachable = sorted(set(self.graph) - set(order), key=str)
        result = " → ".join(order)
        if unreachable:
            result += "\n\nChưa duyệt (không liên thông): " + ", ".join(unreachable)

        self._settext(self.rb, result)
        self._last_bfs_order = order
        self._last_traversal_algo = "BFS"

        # Trực quan hóa trên tab 1: tô sáng các đỉnh BFS đã thăm.
        self.draw(hi_n=set(order), title=f"BFS từ '{start}': " + " → ".join(order))

    def _dfs_run(self):
        """Chạy DFS từ đỉnh do người dùng nhập và hiển thị thứ tự duyệt."""
        start = self.e_ts.get().strip()
        if not self.graph:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng tạo đồ thị trước.")
            return
        if not self._chk(start):
            return

        # DFS dùng stack. Đẩy hàng xóm theo thứ tự ngược để khi pop
        # sẽ thăm theo thứ tự tăng dần, tạo kết quả ổn định và dễ đối chiếu.
        visited = set()
        stack = [start]
        order = []

        while stack:
            u = stack.pop()
            if u in visited:
                continue
            visited.add(u)
            order.append(u)

            neighbors = sorted(self.graph.get(u, []),
                               key=lambda x: str(x[0]), reverse=True)
            for v, _w in neighbors:
                if v not in visited:
                    stack.append(v)

        unreachable = sorted(set(self.graph) - set(order), key=str)
        result = " → ".join(order)
        if unreachable:
            result += "\n\nChưa duyệt (không liên thông): " + ", ".join(unreachable)

        self._settext(self.rd, result)
        self._last_dfs_order = order
        self._last_traversal_algo = "DFS"

        self.draw(hi_n=set(order), title=f"DFS từ '{start}': " + " → ".join(order))

    @staticmethod
    def _parse_traversal_input(value):
        """Chuẩn hóa kết quả chạy tay: A,B,C / A → B → C / A->B->C."""
        import re
        value = value.strip()
        if not value:
            return []
        value = value.replace("→", ",").replace("->", ",").replace("—", ",")
        parts = [x.strip() for x in re.split(r"[,;\\s]+", value) if x.strip()]
        return parts

    def _cmp_trav(self, ra, ma, ca):
        """So sánh kết quả chạy tay với kết quả BFS/DFS vừa chạy."""
        manual = self._parse_traversal_input(ma.get())
        if not manual:
            ca.config(text="⚠ Vui lòng nhập kết quả chạy tay.",
                      fg=WARNING)
            return

        if ra is self.rb:
            algorithm = "BFS"
            actual = getattr(self, "_last_bfs_order", [])
        else:
            algorithm = "DFS"
            actual = getattr(self, "_last_dfs_order", [])

        if not actual:
            ca.config(text=f"⚠ Hãy chạy {algorithm} trước rồi mới so sánh.",
                      fg=WARNING)
            return

        if manual == actual:
            ca.config(
                text=f"✓ ĐÚNG – Kết quả chạy tay trùng với {algorithm}.",
                fg=SUCCESS)
        else:
            ca.config(
                text=(
                    f"✗ SAI – Kết quả không trùng {algorithm}.\\n"
                    f"Thuật toán: {' → '.join(actual)}"
                ),
                fg=ERROR)

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 4 – BIPARTITE
    # ═══════════════════════════════════════════════════════════════════════════
    def _tab4(self, p):
        tb = self._tab_toolbar(p, "Kiểm tra đồ thị hai phía (Bipartite Graph)")
        self._btn(tb, "Kiểm tra", self._bip_check).pack(side=tk.RIGHT, padx=8, pady=6)

        # result panel
        rf = tk.Frame(p, bg=PANEL, relief="solid", bd=1)
        rf.pack(fill=tk.X, padx=8, pady=(0, 6))
        self.bip_r = tk.Label(rf,
                              text="Nhấn  ▶ Kiểm tra  để phân tích",
                              font=("Segoe UI", 12, "bold"),
                              bg=PANEL, fg=TEXT2, pady=14)
        self.bip_r.pack()
        self.bip_d = tk.Label(rf, text="",
                              font=("Segoe UI", 10), bg=PANEL, fg=TEXT,
                              justify="left", wraplength=980)
        self.bip_d.pack(pady=(0, 10))

        # graph canvas
        self.fig4 = Figure(figsize=(9, 4.5), facecolor=GRAPH_BG)
        self.ax4 = self.fig4.add_subplot(111)
        self.ax4.set_facecolor(GRAPH_BG)
        self.cv4 = FigureCanvasTkAgg(self.fig4, p)
        self.cv4.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    def _bip_check(self):
        messagebox.showinfo("Thông báo", "Chức năng thuật toán đã được tách riêng. Vui lòng import từ src/.")


    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 5 – SHORTEST PATH
    # ═══════════════════════════════════════════════════════════════════════════
    def _tab5(self, p):
        self._tab_toolbar(p, "Tìm đường đi ngắn nhất (Dijkstra & Bellman-Ford)")

        ctrl = tk.Frame(p, bg=PANEL, relief="solid", bd=1)
        ctrl.pack(fill=tk.X, padx=8, pady=(0, 6))
        for col, (lbl, attr) in enumerate([("Đỉnh nguồn (Source):", "e_src"),
                                           ("Đỉnh đích   (Target):", "e_tgt")]):
            ctrl.columnconfigure(col*2+1, weight=1)
            tk.Label(ctrl, text=lbl, bg=PANEL, fg=TEXT,
                     font=("Segoe UI", 10)).grid(row=0, column=col*2, padx=12, pady=10)
            e = self._entry(ctrl, width=10)
            e.grid(row=0, column=col*2+1, sticky="ew", padx=6, pady=10)
            setattr(self, attr, e)
        self._btn(ctrl, "Dijkstra",     self._dijk_run).grid(row=0, column=4, padx=6, pady=10)
        self._btn(ctrl, "Bellman-Ford", self._bf_run, ACCENT2).grid(row=0, column=5, padx=6, pady=10)

        cols = tk.Frame(p, bg=BG)
        cols.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        for col, (lbl, clr, ra, mpa, mda, ca) in enumerate([
            ("Dijkstra",     ACCENT,  "rdi", "mpdi", "mddi", "cdi"),
            ("Bellman-Ford", ACCENT2, "rbf", "mpbf", "mdbf", "cbf"),
        ]):
            cols.columnconfigure(col, weight=1); cols.rowconfigure(0, weight=1)
            cf = tk.Frame(cols, bg=PANEL, relief="solid", bd=1)
            cf.grid(row=0, column=col, sticky="nsew", padx=4, pady=2)

            tk.Label(cf, text=lbl, font=("Segoe UI", 11, "bold"),
                     bg=PANEL, fg=clr).pack(pady=(10, 6))
            ttk.Separator(cf, orient="horizontal").pack(fill=tk.X, padx=8)

            tk.Label(cf, text="Kết quả thuật toán:",
                     bg=PANEL, fg=TEXT2, font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(8, 2))
            rt = tk.Text(cf, height=8, bg="#f0fdf4", fg=SUCCESS,
                         font=("Consolas", 10), relief="flat", state="disabled", padx=6, pady=4)
            rt.pack(fill=tk.X, padx=12, pady=(0, 10))
            setattr(self, ra, rt)

            ttk.Separator(cf, orient="horizontal").pack(fill=tk.X, padx=8)
            tk.Label(cf, text="So sánh kết quả chạy tay:",
                     bg=PANEL, fg=TEXT2, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(8, 0))

            tk.Label(cf, text="Đường đi:",
                     bg=PANEL, fg=TEXT2, font=("Segoe UI", 8)).pack(anchor="w", padx=12, pady=(4, 0))
            mp = self._entry(cf); mp.pack(fill=tk.X, padx=12, pady=(2, 4))
            setattr(self, mpa, mp)

            tk.Label(cf, text="Khoảng cách:",
                     bg=PANEL, fg=TEXT2, font=("Segoe UI", 8)).pack(anchor="w", padx=12)
            md = self._entry(cf); md.pack(fill=tk.X, padx=12, pady=(2, 6))
            setattr(self, mda, md)

            cl = tk.Label(cf, text="─  Nhập rồi bấm So sánh  ─",
                          bg=PANEL, fg=TEXT2, font=("Segoe UI", 9),
                          justify="left", wraplength=320)
            cl.pack(anchor="w", padx=12, pady=(0, 4))
            setattr(self, ca, cl)

            def _mk(r, mp_, md_, c):
                self._btn(cf, "So sánh",
                          lambda r=r, mp_=mp_, md_=md_, c=c: self._cmp_sp(r, mp_, md_, c)
                          ).pack(fill=tk.X, padx=12, pady=(0, 12))
            _mk(ra, mpa, mda, ca)

    def _dijk_run(self):
        messagebox.showinfo("Thông báo", "Chức năng thuật toán đã được tách riêng. Vui lòng import từ src/.")

    def _bf_run(self):
        messagebox.showinfo("Thông báo", "Chức năng thuật toán đã được tách riêng. Vui lòng import từ src/.")

    def _show_sp(self, widget, src, tgt, dist, path, algo):
        pass

    def _cmp_sp(self, ra, mpa, mda, ca):
        pass



    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 6 – ADVANCED ALGORITHMS (Fleury, Hierholzer, Prim, Kruskal, Ford-Fulkerson)
    # ═══════════════════════════════════════════════════════════════════════════
    def _tab6(self, p):
        self._tab_toolbar(p, "Chạy & Trực quan hóa các thuật toán nâng cao")

        # ── Sub-tab notebook ──────────────────────────────────────────────────
        s = ttk.Style()
        s.configure("Sub.TNotebook", background=BG, borderwidth=0)
        s.configure("Sub.TNotebook.Tab",
                    background="#e2e8f0", foreground=TEXT2,
                    padding=[14, 6], font=("Segoe UI", 9))
        s.map("Sub.TNotebook.Tab",
              background=[("selected", ACCENT)],
              foreground=[("selected", "white")])

        sub_nb = ttk.Notebook(p, style="Sub.TNotebook")
        sub_nb.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 8))

        for algo_name, builder in [
            ("6.1 Fleury",        self._sub_fleury),
            ("6.2 Hierholzer",    self._sub_hierholzer),
            ("6.3 Prim",          self._sub_prim),
            ("6.4 Kruskal",       self._sub_kruskal),
            ("6.5 Ford-Fulkerson",self._sub_ford_fulkerson),
        ]:
            fr = tk.Frame(sub_nb, bg=BG)
            sub_nb.add(fr, text=algo_name)
            builder(fr)

    # ── Shared helper for algo sub-tabs ──────────────────────────────────────
    def _algo_layout(self, p, title, description, badge_text):
        """Build standard 2-column layout: left=controls, right=canvas."""
        # ── header strip (Clean white panel style) ───────────────────────────
        hdr = tk.Frame(p, bg=PANEL, height=40)
        hdr.pack(fill=tk.X, pady=(0, 4))
        tk.Label(hdr, text=title,
                 font=("Segoe UI", 11, "bold"),
                 bg=PANEL, fg=TEXT).pack(side=tk.LEFT, padx=14, pady=8)
        tk.Label(hdr, text=badge_text,
                 font=("Segoe UI", 8, "bold"),
                 bg=BG, fg=TEXT2,
                 padx=8, pady=3).pack(side=tk.RIGHT, padx=14, pady=8)

        # ── body (left panel + right canvas) ─────────────────────────────────
        body = tk.Frame(p, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # left control panel
        left = tk.Frame(body, bg=PANEL, width=260, relief="solid", bd=1)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))
        left.pack_propagate(False)

        # description card
        desc_f = tk.Frame(left, bg="#eff6ff", bd=0)
        desc_f.pack(fill=tk.X, padx=10, pady=(10, 6))
        tk.Label(desc_f, text="Mô tả thuật toán",
                 font=("Segoe UI", 8, "bold"),
                 bg="#eff6ff", fg=ACCENT).pack(anchor="w", padx=8, pady=(6, 2))
        tk.Label(desc_f, text=description,
                 font=("Segoe UI", 8),
                 bg="#eff6ff", fg=TEXT2,
                 wraplength=220, justify="left").pack(anchor="w", padx=8, pady=(0, 8))

        # right canvas area
        right = tk.Frame(body, bg=PANEL, relief="solid", bd=1)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        return left, right

    def _algo_canvas(self, right_frame, fig_attr, ax_attr, cv_attr):
        """Embed a matplotlib figure in the right panel, return (fig, ax, cv)."""
        fig = Figure(figsize=(7, 4.2), facecolor=GRAPH_BG)
        ax  = fig.add_subplot(111)
        ax.set_facecolor(GRAPH_BG)
        cv  = FigureCanvasTkAgg(fig, right_frame)
        cv.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        setattr(self, fig_attr, fig)
        setattr(self, ax_attr, ax)
        setattr(self, cv_attr, cv)
        # initial blank draw
        self.draw(ax=ax, cv=cv)
        return fig, ax, cv

    def _result_box(self, parent, label="Kết quả:", height=5, bg="#f0fdf4", fg=None):
        """Return a read-only Text widget for showing algo results."""
        fg = fg or SUCCESS
        tk.Label(parent, text=label,
                 font=("Segoe UI", 8, "bold"),
                 bg=PANEL, fg=TEXT2).pack(anchor="w", padx=10, pady=(8, 2))
        t = tk.Text(parent, height=height, bg=bg, fg=fg,
                    font=("Consolas", 9), relief="flat",
                    state="disabled", padx=6, pady=4, wrap="word")
        t.pack(fill=tk.X, padx=10, pady=(0, 6))
        return t

    def _run_placeholder(self, result_widget, algo_name):
        """Fallback khi module thuật toán chưa load được."""
        self._settext(result_widget,
            f"[{algo_name}] – Module chưa load được.\n"
            f"Lỗi: {_ALGO_ERROR if not _ALGO_AVAILABLE else 'N/A'}")

    # ─── Helpers vẽ kết quả thuật toán ───────────────────────────────────────
    def _draw_mst_result(self, ax, cv, mst_edges, added_edge=None, visited=None):
        """Vẽ đồ thị hiện tại và tô màu các cạnh MST."""
        if not self.graph:
            self.draw(ax=ax, cv=cv); return
        G   = self._nxg()
        pos = self._pos if set(G.nodes()) == set(self._pos.keys()) else None
        if pos is None:
            pos = nx.circular_layout(G) if len(G) <= 10 else nx.spring_layout(G, seed=42)
        mst_set = {(u, v) for u, v, _ in mst_edges} | {(v, u) for u, v, _ in mst_edges}
        ec = []
        for e in G.edges():
            if (e[0], e[1]) in mst_set:
                ec.append(EDGE_HI)
            elif added_edge and ((e[0], e[1]) == (added_edge[0], added_edge[1]) or (e[0], e[1]) == (added_edge[1], added_edge[0])):
                ec.append(WARNING)
            else:
                ec.append(EDGE_DEFAULT)
        ax.clear(); ax.set_facecolor(GRAPH_BG); ax.figure.patch.set_facecolor(GRAPH_BG)
        nc = []
        for n in G.nodes():
            if visited and n in visited:
                nc.append(NODE_HI)
            else:
                nc.append(NODE_DEFAULT)
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=nc,
                               node_size=900, edgecolors="white", linewidths=1.5)
        nx.draw_networkx_labels(G, pos, ax=ax, font_color="white",
                                font_size=11, font_weight="bold")
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color=ec, width=2, arrows=False)
        wlbl = {(u, v): str(int(w) if w == int(w) else round(w, 2))
                for u, v, dat in G.edges(data=True)
                if (w := dat.get("weight", 1)) != 1}
        if wlbl:
            nx.draw_networkx_edge_labels(G, pos, wlbl, ax=ax,
                                         font_color="#fbbf24", font_size=9,
                                         bbox=dict(boxstyle="round,pad=0.2",
                                                   fc="#334155", alpha=0.9))
        legend = [Patch(facecolor=EDGE_HI,      label="Cạnh MST"),
                  Patch(facecolor=WARNING,      label="Cạnh đang xét"),
                  Patch(facecolor=NODE_HI,      label="Đỉnh đã xét"),
                  Patch(facecolor=EDGE_DEFAULT,  label="Cạnh còn lại")]
        ax.legend(handles=legend, loc="upper right",
                  facecolor="#1e293b", edgecolor="none",
                  labelcolor="white", fontsize=8)
        ax.axis("off"); cv.draw()

    def _draw_euler_result(self, ax, cv, path, current_node=None):
        """Vẽ đồ thị và tô màu các cạnh trong đường/chu trình Euler."""
        if not self.graph:
            self.draw(ax=ax, cv=cv); return
        G   = self._nxg()
        pos = self._pos if set(G.nodes()) == set(self._pos.keys()) else None
        if pos is None:
            pos = nx.circular_layout(G) if len(G) <= 10 else nx.spring_layout(G, seed=42)
        euler_edges = set()
        for i in range(len(path) - 1):
            euler_edges.add((path[i], path[i+1]))
            euler_edges.add((path[i+1], path[i]))
        ec = [EDGE_HI if (e[0], e[1]) in euler_edges else EDGE_DEFAULT for e in G.edges()]
        # Node color: highlight start/end
        nc = []
        for n in G.nodes():
            if current_node and n == current_node:
                nc.append(WARNING)
            elif path and n == path[0]:
                nc.append(NODE_HI)
            else:
                nc.append(NODE_DEFAULT)
        ax.clear(); ax.set_facecolor(GRAPH_BG); ax.figure.patch.set_facecolor(GRAPH_BG)
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=nc,
                               node_size=900, edgecolors="white", linewidths=1.5)
        nx.draw_networkx_labels(G, pos, ax=ax,
                                labels={n: self._hide_6(n) for n in G.nodes()},
                                font_color="white", font_size=11, font_weight="bold")
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color=ec, width=2.5, arrows=False)
        legend = [Patch(facecolor=EDGE_HI,     label="Cạnh Euler"),
                  Patch(facecolor=NODE_HI,      label="Đỉnh xuất phát"),
                  Patch(facecolor=WARNING,      label="Đỉnh hiện tại")]
        ax.legend(handles=legend, loc="upper right",
                  facecolor="#1e293b", edgecolor="none",
                  labelcolor="white", fontsize=8)
        ax.axis("off"); cv.draw()

    def _draw_flow_result(self, ax, cv, flow_on_edge, max_flow, source, sink, augmenting_path=None):
        """Vẽ đồ thị luồng có hướng với nhãn flow/capacity trên mỗi cạnh."""
        if not self.graph:
            self.draw(ax=ax, cv=cv); return
        G   = nx.DiGraph()
        for u in self.graph:
            G.add_node(u)
        for u in self.graph:
            for v, cap in self.graph[u]:
                G.add_edge(u, v, capacity=cap)
        pos = nx.circular_layout(G) if len(G) <= 10 else nx.spring_layout(G, seed=42)
        # Màu cạnh theo luồng
        ec, ew = [], []
        aug_edges = set()
        if augmenting_path:
            aug_edges = set(zip(augmenting_path, augmenting_path[1:]))

        for u, v in G.edges():
            f = flow_on_edge.get((u, v), 0)
            cap = G[u][v]["capacity"]
            if (u, v) in aug_edges:
                ec.append(WARNING)     # Đường tăng luồng
                ew.append(3.0)
            elif f >= cap:
                ec.append(ERROR)       # bão hoà
                ew.append(3.0)
            elif f > 0:
                ec.append(EDGE_HI)     # có luồng
                ew.append(2.5)
            else:
                ec.append(EDGE_DEFAULT)
                ew.append(1.5)
        # Nhãn: flow/capacity
        elabels = {}
        for u, v in G.edges():
            f   = flow_on_edge.get((u, v), 0)
            cap = G[u][v]["capacity"]
            fv  = int(f) if f == int(f) else round(f, 1)
            cv_ = int(cap) if cap == int(cap) else round(cap, 1)
            elabels[(u, v)] = self._hide_6(f"{fv}/{cv_}")
        nc = []
        for n in G.nodes():
            if n == source: nc.append(SUCCESS)
            elif n == sink: nc.append(ERROR)
            else:           nc.append(NODE_DEFAULT)
        ax.clear(); ax.set_facecolor(GRAPH_BG); ax.figure.patch.set_facecolor(GRAPH_BG)
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=nc,
                               node_size=900, edgecolors="white", linewidths=1.5)
        nx.draw_networkx_labels(G, pos, ax=ax,
                                labels={n: self._hide_6(n) for n in G.nodes()},
                                font_color="white", font_size=11, font_weight="bold")
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color=ec, width=ew,
                               arrows=True, arrowsize=18,
                               connectionstyle="arc3,rad=0.08")
        nx.draw_networkx_edge_labels(G, pos, elabels, ax=ax,
                                     label_pos=0.3,
                                     font_color="#fbbf24", font_size=8,
                                     bbox=dict(boxstyle="round,pad=0.2",
                                               fc="#334155", alpha=0.9))
        ax.set_title(f"Max Flow = {int(max_flow) if max_flow == int(max_flow) else round(max_flow,2)}",
                     color="white", fontsize=11, pad=6)
        legend = [Patch(facecolor=SUCCESS,      label=f"Nguồn ({source})"),
                  Patch(facecolor=ERROR,        label=f"Đích ({sink})"),
                  Patch(facecolor=EDGE_HI,      label="Cạnh có luồng"),
                  Patch(facecolor=ERROR,        label="Cạnh bão hoà")]
        ax.legend(handles=legend, loc="upper right",
                  facecolor="#1e293b", edgecolor="none",
                  labelcolor="white", fontsize=8)
        ax.axis("off"); cv.draw()

    def _step_algo(self, algo_name, action):
        """Xử lý điều hướng các bước (Bắt đầu, Lùi, Tiến, Kết thúc)."""
        from tkinter import messagebox
        steps_attr = f"_{algo_name}_steps"
        idx_attr = f"_{algo_name}_idx"
        
        if not hasattr(self, steps_attr):
            messagebox.showwarning("Cảnh báo", "Vui lòng chạy thuật toán trước!")
            return
            
        steps = getattr(self, steps_attr)
        if not steps: return
        
        current_idx = getattr(self, idx_attr)
        
        if action == "start":
            current_idx = 0
        elif action == "prev":
            current_idx = max(0, current_idx - 1)
        elif action == "next":
            current_idx = min(len(steps) - 1, current_idx + 1)
        elif action == "end":
            current_idx = len(steps) - 1
            
        setattr(self, idx_attr, current_idx)
        step = steps[current_idx]
        
        if algo_name == "fleury":
            self._settext(self.r_fleury, f"Bước {current_idx + 1}/{len(steps)}:\n" + step["description"])
            self._draw_euler_result(self.ax_fleury, self.cv_fleury, step["path"], step.get("current"))
        elif algo_name == "hier":
            self._settext(self.r_hier, f"Bước {current_idx + 1}/{len(steps)}:\n" + step["description"])
            self._draw_euler_result(self.ax_hier, self.cv_hier, step["circuit"], step.get("current"))
        elif algo_name == "prim":
            self._settext(self.r_prim, f"Bước {current_idx + 1}/{len(steps)}:\n" + step["description"])
            self._draw_mst_result(self.ax_prim, self.cv_prim, step["mst_edges"], step.get("added_edge"), step.get("visited"))
        elif algo_name == "kruskal":
            self._settext(self.r_kruskal, f"Bước {current_idx + 1}/{len(steps)}:\n" + step["description"])
            self._draw_mst_result(self.ax_kruskal, self.cv_kruskal, step["mst_edges"], step.get("edge"))
        elif algo_name == "ff":
            self._settext(self.r_ff, f"Bước {current_idx + 1}/{len(steps)}:\n" + step["description"])
            src = self.e_ff_src.get().strip()
            snk = self.e_ff_snk.get().strip()
            self._draw_flow_result(self.ax_ff, self.cv_ff, step.get("flow_on_edge", {}), step["total_flow"], src, snk, step.get("path"))

    # ─── Runner methods – gọi thuật toán thật ─────────────────────────────────

    def _run_fleury(self):
        """Chạy thuật toán Fleury và hiển thị kết quả."""
        if not _ALGO_AVAILABLE:
            messagebox.showerror("Lỗi import", _ALGO_ERROR); return
        if not self.graph:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng tạo đồ thị trước."); return

        # Kiểm tra điều kiện
        ok, msg, suggested = check_euler_condition(self.graph)
        if not ok:
            self._settext(self.r_fleury, f"{msg}"); return

        start = self.e_fleury_start.get().strip() or suggested
        if start not in self.graph:
            self._settext(self.r_fleury, f"Đỉnh '{start}' không hợp lệ."); return

        try:
            path, steps = fleury(self.graph, start)
        except ValueError as err:
            self._settext(self.r_fleury, f"{err}"); return

        # Lưu steps để nút Tiến/Lùi dùng sau
        self._fleury_steps = steps
        self._fleury_idx   = len(steps) - 1

        # Hiển thị kết quả
        is_circuit = path[0] == path[-1]
        lines = [
            ("Chu trình Euler tìm được:" if is_circuit else "Đường đi Euler tìm được:"),
            "   " + " → ".join(path),
            "",
            f"Số cạnh đã đi: {len(path) - 1}",
            "",
            "Các bước cuối cùng:",
        ]
        for s in steps[-4:]:
            lines.append("  • " + s["description"])
        self._settext(self.r_fleury, "\n".join(lines))

        # Vẽ
        self._draw_euler_result(self.ax_fleury, self.cv_fleury, path)

    def _run_hierholzer(self):
        """Chạy thuật toán Hierholzer và hiển thị kết quả."""
        if not _ALGO_AVAILABLE:
            messagebox.showerror("Lỗi import", _ALGO_ERROR); return
        if not self.graph:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng tạo đồ thị trước."); return

        ok, msg, suggested = check_euler_condition(self.graph)
        if not ok:
            self._settext(self.r_hier, f"{msg}"); return

        start = self.e_hier_start.get().strip() or suggested
        if start not in self.graph:
            self._settext(self.r_hier, f"Đỉnh '{start}' không hợp lệ."); return

        try:
            circuit, steps = hierholzer(self.graph, start)
        except ValueError as err:
            self._settext(self.r_hier, f"{err}"); return

        self._hier_steps = steps
        self._hier_idx   = len(steps) - 1

        is_circuit = circuit[0] == circuit[-1]
        lines = [
            ("Chu trình Euler (Hierholzer):" if is_circuit else "Đường đi Euler (Hierholzer):"),
            "   " + " → ".join(circuit),
            "",
            f"Số đỉnh: {len(circuit)}   |   Số cạnh: {len(circuit) - 1}",
            "",
            "Bước cuối – stack và circuit:",
        ]
        for s in steps[-3:]:
            lines.append("  • " + s["description"])
        self._settext(self.r_hier, "\n".join(lines))

        self._draw_euler_result(self.ax_hier, self.cv_hier, circuit)

    def _run_prim(self):
        """Chạy thuật toán Prim và hiển thị kết quả."""
        if not _ALGO_AVAILABLE:
            messagebox.showerror("Lỗi import", _ALGO_ERROR); return
        if not self.graph:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng tạo đồ thị trước."); return

        root = self.e_prim_root.get().strip()
        if not root:
            root = next(iter(self.graph))
        if root not in self.graph:
            self._settext(self.r_prim, f"Đỉnh '{root}' không hợp lệ."); return

        try:
            mst_edges, total_cost, steps = prim(self.graph, root)
        except ValueError as err:
            self._settext(self.r_prim, f"{err}"); return

        self._prim_steps = steps
        self._prim_idx   = len(steps) - 1

        cost_str = str(int(total_cost)) if total_cost == int(total_cost) else f"{total_cost:.4g}"
        self.lbl_prim_cost.config(text=cost_str)

        lines = [f"MST từ đỉnh '{root}':"]
        for u, v, w in mst_edges:
            wstr = str(int(w)) if w == int(w) else f"{w:.4g}"
            lines.append(f"  ({u} — {v})  w = {wstr}")
        lines += ["", f"Tổng trọng số: {cost_str}"]
        self._settext(self.r_prim, "\n".join(lines))

        self._draw_mst_result(self.ax_prim, self.cv_prim, mst_edges)

    def _run_kruskal(self):
        """Chạy thuật toán Kruskal và hiển thị kết quả."""
        if not _ALGO_AVAILABLE:
            messagebox.showerror("Lỗi import", _ALGO_ERROR); return
        if not self.graph:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng tạo đồ thị trước."); return

        try:
            mst_edges, total_cost, steps = kruskal(self.graph)
        except ValueError as err:
            self._settext(self.r_kruskal, f"{err}"); return

        self._kruskal_steps = steps
        self._kruskal_idx   = len(steps) - 1

        cost_str = str(int(total_cost)) if total_cost == int(total_cost) else f"{total_cost:.4g}"
        self.lbl_kruskal_cost.config(text=cost_str)

        lines = ["Kruskal MST:"]
        for u, v, w in mst_edges:
            wstr = str(int(w)) if w == int(w) else f"{w:.4g}"
            lines.append(f"  ({u} — {v})  w = {wstr}")
        lines += ["", f"Tổng trọng số: {cost_str}"]
        self._settext(self.r_kruskal, "\n".join(lines))

        self._draw_mst_result(self.ax_kruskal, self.cv_kruskal, mst_edges)

    def _run_ford_fulkerson(self):
        """Chạy thuật toán Ford-Fulkerson và hiển thị kết quả."""
        if not _ALGO_AVAILABLE:
            messagebox.showerror("Lỗi import", _ALGO_ERROR); return
        if not self.graph:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng tạo đồ thị trước."); return

        src = self.e_ff_src.get().strip()
        snk = self.e_ff_snk.get().strip()
        if not src or not snk:
            messagebox.showwarning("Thiếu thông tin",
                "Vui lòng nhập đỉnh nguồn (Source) và đỉnh đích (Sink)."); return
        if src not in self.graph:
            self._settext(self.r_ff, f" Đỉnh nguồn '{src}' không tồn tại."); return
        if snk not in self.graph:
            self._settext(self.r_ff, f"Đỉnh đích '{snk}' không tồn tại."); return

        try:
            max_flow, flow_on_edge, steps = ford_fulkerson(self.graph, src, snk)
        except ValueError as err:
            self._settext(self.r_ff, f"{err}"); return

        self._ff_steps = steps
        self._ff_idx   = len(steps) - 1

        flow_str = str(int(max_flow)) if max_flow == int(max_flow) else f"{max_flow:.4g}"
        self.lbl_ff_flow.config(text=flow_str)

        augment_steps = [s for s in steps if s.get("action") == "augment"]
        lines = [f"Max Flow = {flow_str}  (Nguồn: {src} → Đích: {snk})", ""]
        if augment_steps:
            lines.append(f"Số đường tăng luồng: {len(augment_steps)}")
            lines.append("")
            for s in augment_steps:
                lines.append("  • " + s["description"].split("\n")[0])
        self._settext(self.r_ff, "\n".join(lines))

        self._draw_flow_result(
            self.ax_ff, self.cv_ff,
            flow_on_edge, max_flow, src, snk
        )

    def _load_sample_for_algo(self, algo_type):
        """
        Nạp đồ thị mẫu được cấu hình sẵn cho các bài test tương ứng.
        Sử dụng trực tiếp các ví dụ ở hướng dẫn test để kiểm tra nhanh.
        """
        # Làm sạch đồ thị hiện có mà không hiện hộp thoại hỏi xác nhận
        self.graph = {}
        self._pos = {}

        if algo_type in ["prim", "kruskal"]:
            # Cây khung nhỏ nhất (MST) cần đồ thị vô hướng
            self.directed.set(False)
            self._pos = {}
            
            # Cạnh mẫu: (u, v, weight)
            edges = [
                ("A", "B", 4.0),
                ("A", "C", 2.0),
                ("B", "C", 1.0),
                ("B", "D", 5.0),
                ("C", "D", 8.0)
            ]
            for u, v, w in edges:
                self.graph.setdefault(u, []).append((v, w))
                self.graph.setdefault(v, []).append((u, w))
            
            # Điền đầu vào mặc định
            if algo_type == "prim" and hasattr(self, 'e_prim_root'):
                self.e_prim_root.delete(0, tk.END)
                self.e_prim_root.insert(0, "A")
                
            self._upd_info()
            if algo_type == "prim":
                self.draw(ax=self.ax_prim, cv=self.cv_prim)
            else:
                self.draw(ax=self.ax_kruskal, cv=self.cv_kruskal)
                
        elif algo_type in ["fleury", "hierholzer"]:
            # Euler Path/Circuit cần đồ thị vô hướng bậc lẻ hợp lệ
            self.directed.set(False)
            self._pos = {}
            
            edges = [
                ("A", "B", 1.0),
                ("A", "C", 1.0),
                ("B", "C", 1.0),
                ("B", "D", 1.0),
                ("C", "D", 1.0)
            ]
            for u, v, w in edges:
                self.graph.setdefault(u, []).append((v, w))
                self.graph.setdefault(v, []).append((u, w))
                
            self._upd_info()
            if algo_type == "fleury":
                if hasattr(self, 'e_fleury_start'):
                    self.e_fleury_start.delete(0, tk.END)
                    self.e_fleury_start.insert(0, "B")
                self.draw(ax=self.ax_fleury, cv=self.cv_fleury)
            else:
                if hasattr(self, 'e_hier_start'):
                    self.e_hier_start.delete(0, tk.END)
                    self.e_hier_start.insert(0, "B")
                self.draw(ax=self.ax_hier, cv=self.cv_hier)
                
        elif algo_type == "ford_fulkerson":
            # Ford-Fulkerson (Max Flow) yêu cầu đồ thị có hướng và sức chứa
            self.directed.set(True)
            self._pos = {}
            
            edges = [
                ("S", "A", 10.0),
                ("S", "B", 10.0),
                ("A", "T", 8.0),
                ("B", "T", 9.0),
                ("A", "B", 2.0)
            ]
            for u, v, w in edges:
                self.graph.setdefault(u, []).append((v, w))
                if v not in self.graph:
                    self.graph[v] = []
                    
            if hasattr(self, 'e_ff_src'):
                self.e_ff_src.delete(0, tk.END)
                self.e_ff_src.insert(0, "S")
            if hasattr(self, 'e_ff_snk'):
                self.e_ff_snk.delete(0, tk.END)
                self.e_ff_snk.insert(0, "T")
                
            self._upd_info()
            self.draw(ax=self.ax_ff, cv=self.cv_ff)

        # Cập nhật cả khung vẽ chung của Tab 1
        if hasattr(self, 'ax') and hasattr(self, 'canvas'):
            self.draw()

    # ── 6.1 Fleury ───────────────────────────────────────────────────────────


    def _sub_fleury(self, p):
        desc = (
            "Tìm đường đi Euler / chu trình Euler bằng cách "
            "chọn cạnh an toàn (không cầu) mỗi bước.\n\n"
            "Yêu cầu: đồ thị liên thông, đúng 0 hoặc 2 đỉnh "
            "có bậc lẻ."
        )
        left, right = self._algo_layout(
            p,
            title="Thuật toán Fleury – Euler Path/Circuit",
            description=desc,
            badge_text="Euler"
        )

        # controls
        tk.Label(left, text="Đỉnh xuất phát:",
                 bg=PANEL, fg=TEXT2, font=("Segoe UI", 9)).pack(anchor="w", padx=10, pady=(6, 2))
        self.e_fleury_start = self._entry(left)
        self.e_fleury_start.pack(fill=tk.X, padx=10, pady=(0, 8))

        self._btn(left, "Nạp đồ thị mẫu",
                  lambda: self._load_sample_for_algo("fleury")).pack(fill=tk.X, padx=10, pady=(0, 6))

        self._btn(left, "Chạy Fleury",
                  lambda: self._run_fleury(),
                  color=ACCENT).pack(fill=tk.X, padx=10, pady=(0, 6))

        ttk.Separator(left, orient="horizontal").pack(fill=tk.X, padx=10, pady=4)
        self.r_fleury = self._result_box(left, height=7, bg="#f0fdf4", fg=SUCCESS)

        # legend note
        tk.Label(left,
                 text="Cạnh đang xét | đã duyệt",
                 bg=PANEL, fg=TEXT2, font=("Segoe UI", 8),
                 wraplength=220, justify="left").pack(padx=10, pady=(4, 0))

        self._algo_canvas(right, "fig_fleury", "ax_fleury", "cv_fleury")

        # step controls (bottom of right)
        bot = tk.Frame(right, bg=PANEL)
        bot.pack(fill=tk.X, padx=6, pady=(0, 6))
        self._btn(bot, "Bắt đầu", lambda: self._step_algo("fleury", "start"), "#64748b").pack(side=tk.LEFT, padx=4)
        self._btn(bot, "Lùi", lambda: self._step_algo("fleury", "prev"), WARNING).pack(side=tk.LEFT, padx=4)
        self._btn(bot, "Tiến", lambda: self._step_algo("fleury", "next"), SUCCESS).pack(side=tk.LEFT, padx=4)
        self._btn(bot, "Kết thúc", lambda: self._step_algo("fleury", "end"), ACCENT).pack(side=tk.LEFT, padx=4)

    # ── 6.2 Hierholzer ───────────────────────────────────────────────────────
    def _sub_hierholzer(self, p):
        desc = (
            "Tìm chu trình Euler hiệu quả O(E) bằng cách "
            "dùng stack và backtrack.\n\n"
            "Yêu cầu: đồ thị liên thông, mọi đỉnh đều có "
            "bậc chẵn."
        )
        left, right = self._algo_layout(
            p,
            title="Thuật toán Hierholzer – Euler Circuit",
            description=desc,
            badge_text="Euler Circuit"
        )

        tk.Label(left, text="Đỉnh bắt đầu:",
                 bg=PANEL, fg=TEXT2, font=("Segoe UI", 9)).pack(anchor="w", padx=10, pady=(6, 2))
        self.e_hier_start = self._entry(left)
        self.e_hier_start.pack(fill=tk.X, padx=10, pady=(0, 8))

        self._btn(left, "Nạp đồ thị mẫu",
                  lambda: self._load_sample_for_algo("hierholzer")).pack(fill=tk.X, padx=10, pady=(0, 6))

        self._btn(left, "Chạy Hierholzer",
                  lambda: self._run_hierholzer(),
                  color=ACCENT).pack(fill=tk.X, padx=10, pady=(0, 6))

        ttk.Separator(left, orient="horizontal").pack(fill=tk.X, padx=10, pady=4)
        self.r_hier = self._result_box(left, height=7, bg="#f0fdf4", fg=SUCCESS)

        tk.Label(left,
                 text="Stack trạng thái sẽ được hiển thị theo từng bước.",
                 bg=PANEL, fg=TEXT2, font=("Segoe UI", 8),
                 wraplength=220, justify="left").pack(padx=10, pady=(4, 0))

        self._algo_canvas(right, "fig_hier", "ax_hier", "cv_hier")

        bot = tk.Frame(right, bg=PANEL)
        bot.pack(fill=tk.X, padx=6, pady=(0, 6))
        self._btn(bot, "Bắt đầu", lambda: self._step_algo("hier", "start"), "#64748b").pack(side=tk.LEFT, padx=4)
        self._btn(bot, "Lùi", lambda: self._step_algo("hier", "prev"), WARNING).pack(side=tk.LEFT, padx=4)
        self._btn(bot, "Tiến", lambda: self._step_algo("hier", "next"), SUCCESS).pack(side=tk.LEFT, padx=4)
        self._btn(bot, "Kết thúc", lambda: self._step_algo("hier", "end"), ACCENT).pack(side=tk.LEFT, padx=4)

    # ── 6.3 Prim ─────────────────────────────────────────────────────────────
    def _sub_prim(self, p):
        desc = (
            "Xây dựng cây khung nhỏ nhất (MST) bằng cách "
            "tham lam mở rộng cạnh nhẹ nhất từ tập đỉnh đã chọn.\n\n"
            "Độ phức tạp: O(E log V) với heap."
        )
        left, right = self._algo_layout(
            p,
            title="Thuật toán Prim – Minimum Spanning Tree",
            description=desc,
            badge_text="MST"
        )

        tk.Label(left, text="Đỉnh nguồn (root):",
                 bg=PANEL, fg=TEXT2, font=("Segoe UI", 9)).pack(anchor="w", padx=10, pady=(6, 2))
        self.e_prim_root = self._entry(left)
        self.e_prim_root.pack(fill=tk.X, padx=10, pady=(0, 8))

        self._btn(left, "Nạp đồ thị mẫu",
                  lambda: self._load_sample_for_algo("prim")).pack(fill=tk.X, padx=10, pady=(0, 6))

        self._btn(left, "Chạy Prim",
                  lambda: self._run_prim(),
                  color=ACCENT).pack(fill=tk.X, padx=10, pady=(0, 6))

        ttk.Separator(left, orient="horizontal").pack(fill=tk.X, padx=10, pady=4)

        tk.Label(left, text="Tổng trọng số MST:",
                 bg=PANEL, fg=TEXT2, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=10, pady=(6, 0))
        self.lbl_prim_cost = tk.Label(left, text="─",
                                      font=("Segoe UI", 18, "bold"),
                                      bg=PANEL, fg=ACCENT)
        self.lbl_prim_cost.pack(pady=(2, 6))

        self.r_prim = self._result_box(left, label="Các cạnh MST:", height=6, bg="#f0fdf4", fg=SUCCESS)

        self._algo_canvas(right, "fig_prim", "ax_prim", "cv_prim")

        bot = tk.Frame(right, bg=PANEL)
        bot.pack(fill=tk.X, padx=6, pady=(0, 6))
        self._btn(bot, "Bắt đầu", lambda: self._step_algo("prim", "start"), "#64748b").pack(side=tk.LEFT, padx=4)
        self._btn(bot, "Lùi", lambda: self._step_algo("prim", "prev"), WARNING).pack(side=tk.LEFT, padx=4)
        self._btn(bot, "Tiến", lambda: self._step_algo("prim", "next"), SUCCESS).pack(side=tk.LEFT, padx=4)
        self._btn(bot, "Kết thúc", lambda: self._step_algo("prim", "end"), ACCENT).pack(side=tk.LEFT, padx=4)

    # ── 6.4 Kruskal ──────────────────────────────────────────────────────────
    def _sub_kruskal(self, p):
        desc = (
            "Xây dựng MST bằng cách sắp xếp cạnh theo trọng số "
            "và thêm cạnh không tạo chu trình (Union-Find).\n\n"
            "Độ phức tạp: O(E log E)."
        )
        left, right = self._algo_layout(
            p,
            title="Thuật toán Kruskal – Minimum Spanning Tree",
            description=desc,
            badge_text="MST · Union-Find"
        )

        self._btn(left, "Nạp đồ thị mẫu",
                  lambda: self._load_sample_for_algo("kruskal")).pack(fill=tk.X, padx=10, pady=(0, 6))

        self._btn(left, "Chạy Kruskal",
                  lambda: self._run_kruskal(),
                  color=ACCENT).pack(fill=tk.X, padx=10, pady=(10, 6))

        ttk.Separator(left, orient="horizontal").pack(fill=tk.X, padx=10, pady=4)

        tk.Label(left, text="Tổng trọng số MST:",
                 bg=PANEL, fg=TEXT2, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=10, pady=(6, 0))
        self.lbl_kruskal_cost = tk.Label(left, text="─",
                                         font=("Segoe UI", 18, "bold"),
                                         bg=PANEL, fg=ACCENT)
        self.lbl_kruskal_cost.pack(pady=(2, 6))

        self.r_kruskal = self._result_box(left, label="Các cạnh được chọn:", height=6, bg="#f0fdf4", fg=SUCCESS)

        tk.Label(left,
                 text="Cạnh thêm vào MST | Cạnh bị loại (chu trình)",
                 bg=PANEL, fg=TEXT2, font=("Segoe UI", 8),
                 wraplength=220, justify="left").pack(padx=10, pady=(4, 0))

        self._algo_canvas(right, "fig_kruskal", "ax_kruskal", "cv_kruskal")

        bot = tk.Frame(right, bg=PANEL)
        bot.pack(fill=tk.X, padx=6, pady=(0, 6))
        self._btn(bot, "Bắt đầu", lambda: self._step_algo("kruskal", "start"), "#64748b").pack(side=tk.LEFT, padx=4)
        self._btn(bot, "Lùi", lambda: self._step_algo("kruskal", "prev"), WARNING).pack(side=tk.LEFT, padx=4)
        self._btn(bot, "Tiến", lambda: self._step_algo("kruskal", "next"), SUCCESS).pack(side=tk.LEFT, padx=4)
        self._btn(bot, "Kết thúc", lambda: self._step_algo("kruskal", "end"), ACCENT).pack(side=tk.LEFT, padx=4)

    # ── 6.5 Ford-Fulkerson ───────────────────────────────────────────────────
    def _sub_ford_fulkerson(self, p):
        desc = (
            "Tìm luồng cực đại (max-flow) trong mạng luồng "
            "bằng cách lặp tìm đường tăng luồng (augmenting path).\n\n"
            "Cạnh phải có hướng. Trọng số = sức chứa (capacity)."
        )
        left, right = self._algo_layout(
            p,
            title="Ford-Fulkerson – Max Flow",
            description=desc,
            badge_text="Max Flow"
        )

        # Source / Sink inputs
        for lbl, attr in [("Đỉnh nguồn (Source):", "e_ff_src"),
                          ("Đỉnh đích   (Sink):",  "e_ff_snk")]:
            tk.Label(left, text=lbl,
                     bg=PANEL, fg=TEXT2, font=("Segoe UI", 9)).pack(anchor="w", padx=10, pady=(6, 2))
            e = self._entry(left)
            e.pack(fill=tk.X, padx=10, pady=(0, 4))
            setattr(self, attr, e)

        self._btn(left, "Nạp đồ thị mẫu",
                  lambda: self._load_sample_for_algo("ford_fulkerson")).pack(fill=tk.X, padx=10, pady=(6, 6))

        self._btn(left, "Chạy Ford-Fulkerson",
                  lambda: self._run_ford_fulkerson(),
                  color=ACCENT).pack(fill=tk.X, padx=10, pady=(6, 6))

        ttk.Separator(left, orient="horizontal").pack(fill=tk.X, padx=10, pady=4)

        tk.Label(left, text="Luồng cực đại (Max Flow):",
                 bg=PANEL, fg=TEXT2, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=10, pady=(6, 0))
        self.lbl_ff_flow = tk.Label(left, text="─",
                                    font=("Segoe UI", 20, "bold"),
                                    bg=PANEL, fg=ACCENT)
        self.lbl_ff_flow.pack(pady=(2, 6))

        self.r_ff = self._result_box(left, label="Các đường tăng luồng:", height=5, bg="#f0fdf4", fg=SUCCESS)

        tk.Label(right,
                 text="Cạnh bão hòa   |   Cạnh dư   |   Đường tăng luồng",
                 bg=PANEL, fg=TEXT2, font=("Segoe UI", 8)).pack(pady=4)

        self._algo_canvas(right, "fig_ff", "ax_ff", "cv_ff")

        bot = tk.Frame(right, bg=PANEL)
        bot.pack(fill=tk.X, padx=6, pady=(0, 6))
        self._btn(bot, "Bắt đầu", lambda: self._step_algo("ff", "start"), "#64748b").pack(side=tk.LEFT, padx=4)
        self._btn(bot, "Lùi", lambda: self._step_algo("ff", "prev"), WARNING).pack(side=tk.LEFT, padx=4)
        self._btn(bot, "Tiến", lambda: self._step_algo("ff", "next"), SUCCESS).pack(side=tk.LEFT, padx=4)
        self._btn(bot, "Kết thúc", lambda: self._step_algo("ff", "end"), ACCENT).pack(side=tk.LEFT, padx=4)

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 7 – REAL-WORLD PROBLEM APPLICATION
    # ═══════════════════════════════════════════════════════════════════════════
    def _tab7(self, p):
        tb = self._tab_toolbar(p, "Bài toán thực tế – Ứng dụng thuật toán đồ thị")

        body = tk.Frame(p, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        # ── Left: problem selector + description ─────────────────────────────
        left = tk.Frame(body, bg=PANEL, width=320, relief="solid", bd=1)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))
        left.pack_propagate(False)

        tk.Label(left, text="Chọn bài toán thực tế:",
                 font=("Segoe UI", 9, "bold"),
                 bg=PANEL, fg=ACCENT).pack(anchor="w", padx=14, pady=(14, 4))

        # Problem selector
        PROBLEMS = [
            "Mạng phân phối điện (Kruskal – MST)",
            "Cấp nước thành phố (Prim – MST)",
            "Hệ thống ống dẫn dầu (Ford-Fulkerson – Max Flow)",
            "Lịch trình thu rác (Fleury – Euler Path)",
            "Dò mạng cáp quang (Hierholzer – Euler Circuit)",
        ]
        self.prob_var = tk.StringVar(value=PROBLEMS[0])
        prob_menu = ttk.Combobox(left, textvariable=self.prob_var,
                                 values=PROBLEMS, state="readonly",
                                 font=("Segoe UI", 9))
        prob_menu.pack(fill=tk.X, padx=14, pady=(0, 10))
        prob_menu.bind("<<ComboboxSelected>>", self._on_problem_select)

        ttk.Separator(left, orient="horizontal").pack(fill=tk.X, padx=10, pady=2)

        # Problem description area
        tk.Label(left, text="Mô tả bài toán:",
                 font=("Segoe UI", 9, "bold"),
                 bg=PANEL, fg=TEXT).pack(anchor="w", padx=14, pady=(10, 4))
        self.prob_desc_t = tk.Text(left,
                                   bg="#f8fafc", fg=TEXT,
                                   font=("Segoe UI", 9), relief="flat",
                                   state="disabled", wrap="word",
                                   padx=10, pady=8, borderwidth=0)
        self.prob_desc_t.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 4))

        ttk.Separator(left, orient="horizontal").pack(fill=tk.X, padx=10, pady=4)

        # Run button
        self.btn_prob_run = self._btn(
            left, "Chạy bài toán",
            lambda: self._run_real_problem(),
            color=ACCENT)
        self.btn_prob_run.pack(fill=tk.X, padx=14, pady=(4, 14))

        # ── Right: graph canvas + result ──────────────────────────────────────
        right = tk.Frame(body, bg=BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Graph canvas
        graph_frame = tk.Frame(right, bg=PANEL, relief="solid", bd=1)
        graph_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        tk.Label(graph_frame, text="Đồ thị bài toán thực tế",
                 font=("Segoe UI", 10, "bold"),
                 bg=PANEL, fg=TEXT).pack(anchor="w", padx=12, pady=(8, 2))
        ttk.Separator(graph_frame, orient="horizontal").pack(fill=tk.X, padx=8)

        self.fig_prob = Figure(figsize=(7, 3.8), facecolor=GRAPH_BG)
        self.ax_prob  = self.fig_prob.add_subplot(111)
        self.ax_prob.set_facecolor(GRAPH_BG)
        self.cv_prob  = FigureCanvasTkAgg(self.fig_prob, graph_frame)
        self.cv_prob.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self._prob_draw_placeholder()

        # Result box
        result_frame = tk.Frame(right, bg=PANEL, relief="solid", bd=1)
        result_frame.pack(fill=tk.X)

        res_hdr = tk.Frame(result_frame, bg=ACCENT, height=32)
        res_hdr.pack(fill=tk.X)
        tk.Label(res_hdr, text="Kết quả thực thi",
                 font=("Segoe UI", 9, "bold"),
                 bg=ACCENT, fg="white").pack(side=tk.LEFT, padx=10, pady=6)

        self.r_prob = tk.Text(result_frame, height=5,
                              bg="#f0fdf4", fg=SUCCESS,
                              font=("Consolas", 9), relief="flat",
                              state="disabled", padx=8, pady=6, wrap="word")
        self.r_prob.pack(fill=tk.X, padx=6, pady=6)

        # Init first problem
        self._on_problem_select()

    # Problem data ──────────────────────────────────────────────────────────
    _PROBLEM_DATA = {
        "Mạng phân phối điện (Kruskal – MST)": {
            "desc": (
                "Bài toán:\n"
                "Một công ty điện lực cần lắp đặt đường dây điện "
                "kết nối 6 trạm biến áp với chi phí tối thiểu.\n\n"
                "Ánh xạ đồ thị:\n"
                "  • Node = Trạm biến áp (A–F)\n"
                "  • Edge = Tuyến cáp có thể lắp\n"
                "  • Weight = Chi phí lắp (triệu đồng)\n\n"
                "Cần tìm: Cây khung nhỏ nhất (MST) để "
                "kết nối toàn bộ trạm với chi phí thấp nhất.\n\n"
                "🔧 Thuật toán: Kruskal (sắp xếp cạnh + Union-Find)"
            ),
            "algo": "Kruskal",
            "nodes": ["A", "B", "C", "D", "E", "F"],
            "edges": [
                ("A", "B", 4), ("A", "C", 2), ("B", "C", 5),
                ("B", "D", 10),("C", "E", 3), ("E", "D", 4),
                ("D", "F", 11),("E", "F", 8),
            ],
        },
        "Cấp nước thành phố (Prim – MST)": {
            "desc": (
                "Bài toán:\n"
                "Thành phố cần xây dựng hệ thống đường ống dẫn "
                "nước từ nhà máy đến 5 khu dân cư.\n\n"
                "Ánh xạ đồ thị:\n"
                "  • Node = Nhà máy / Khu dân cư (1–6)\n"
                "  • Edge = Tuyến ống có thể xây\n"
                "  • Weight = Chi phí xây dựng (tỷ đồng)\n\n"
                "Cần tìm: MST đảm bảo nước tới mọi khu "
                "với tổng chi phí xây dựng thấp nhất.\n\n"
                "🔧 Thuật toán: Prim (mở rộng từ đỉnh gốc)"
            ),
            "algo": "Prim",
            "nodes": ["NM", "K1", "K2", "K3", "K4", "K5"],
            "edges": [
                ("NM", "K1", 3), ("NM", "K2", 5), ("K1", "K2", 2),
                ("K1", "K3", 6), ("K2", "K4", 4), ("K3", "K4", 1),
                ("K3", "K5", 7), ("K4", "K5", 3),
            ],
        },
        "Hệ thống ống dẫn dầu (Ford-Fulkerson – Max Flow)": {
            "desc": (
                "Bài toán:\n"
                "Một hệ thống ống dẫn dầu có nguồn (S) và đích (T). "
                "Mỗi ống có sức chứa giới hạn. "
                "Cần tối đa hóa lượng dầu vận chuyển từ S đến T.\n\n"
                "Ánh xạ đồ thị:\n"
                "  • Node = Điểm giao ống / Trạm bơm\n"
                "  • Edge (có hướng) = Ống dẫn dầu\n"
                "  • Weight = Sức chứa (capacity) của ống\n\n"
                "Cần tìm: Luồng cực đại (Max Flow) từ S đến T.\n\n"
                "Thuật toán: Ford-Fulkerson (BFS – Edmonds-Karp)"
            ),
            "algo": "Ford-Fulkerson",
            "nodes": ["S", "A", "B", "C", "D", "T"],
            "edges": [
                ("S", "A", 10), ("S", "B", 8),
                ("A", "C", 5),  ("A", "B", 3),
                ("B", "D", 9),  ("C", "T", 7),
                ("D", "T", 6),  ("C", "D", 4),
            ],
        },
        "Lịch trình thu rác (Fleury – Euler Path)": {
            "desc": (
                "Bài toán:\n"
                "Xe thu rác cần đi qua mỗi con phố đúng một lần "
                "(mỗi cạnh = một đoạn đường) mà không lặp lại, "
                "xuất phát và kết thúc tại kho.\n\n"
                "Ánh xạ đồ thị:\n"
                "  • Node = Ngã tư / Điểm dừng\n"
                "  • Edge = Đoạn đường giữa 2 ngã tư\n"
                "  • Weight = Chiều dài đoạn (km)\n\n"
                "Cần tìm: Đường đi Euler (qua mỗi cạnh đúng 1 lần).\n\n"
                "Thuật toán: Fleury (kiểm tra cầu trước khi chọn cạnh)"
            ),
            "algo": "Fleury",
            "nodes": ["Kho", "N1", "N2", "N3", "N4"],
            "edges": [
                ("Kho", "N1", 1.2), ("Kho", "N2", 0.8),
                ("N1", "N2", 1.0), ("N1", "N3", 1.5),
                ("N2", "N3", 0.9), ("N3", "N4", 1.1),
                ("N4", "Kho", 1.3),
            ],
        },
        "Dò mạng cáp quang (Hierholzer – Euler Circuit)": {
            "desc": (
                "Bài toán:\n"
                "Kỹ thuật viên cần kiểm tra mọi sợi cáp quang trong "
                "mạng vòng của tòa nhà, đi qua mỗi sợi đúng 1 lần "
                "và quay về điểm xuất phát.\n\n"
                "Ánh xạ đồ thị:\n"
                "  • Node = Hộp kết nối (patch panel)\n"
                "  • Edge = Sợi cáp quang\n"
                "  • Weight = Chiều dài sợi (m)\n\n"
                "Cần tìm: Chu trình Euler (qua mỗi cạnh 1 lần, quay đầu).\n\n"
                "Thuật toán: Hierholzer (O(E) – dùng stack)"
            ),
            "algo": "Hierholzer",
            "nodes": ["Hub", "P1", "P2", "P3", "P4", "P5"],
            "edges": [
                ("Hub", "P1", 50), ("P1", "P2", 30), ("P2", "P3", 40),
                ("P3", "P4", 25), ("P4", "P5", 35), ("P5", "Hub", 45),
                ("Hub", "P3", 60), ("P1", "P4", 55),
            ],
        },
    }

    def _on_problem_select(self, event=None):
        key = self.prob_var.get()
        data = self._PROBLEM_DATA.get(key, {})
        desc = data.get("desc", "")
        self._settext(self.prob_desc_t, desc)
        # draw sample graph for the problem
        self._prob_draw_sample(data)
        self._settext(self.r_prob,
            f"Bài toán: {key}\n"
            "Nhấn Chạy bài toán để xem kết quả thuật toán.")

    def _prob_draw_placeholder(self):
        self.ax_prob.clear()
        self.ax_prob.set_facecolor(GRAPH_BG)
        self.ax_prob.text(0.5, 0.5,
                          "Chọn bài toán để xem đồ thị minh họa",
                          ha="center", va="center", fontsize=11,
                          color="#94a3b8", transform=self.ax_prob.transAxes)
        self.ax_prob.axis("off")
        self.cv_prob.draw()

    def _prob_draw_sample(self, data):
        self.ax_prob.clear()
        self.ax_prob.set_facecolor(GRAPH_BG)
        self.fig_prob.patch.set_facecolor(GRAPH_BG)

        nodes = data.get("nodes", [])
        edges = data.get("edges", [])
        algo  = data.get("algo", "")

        if not nodes:
            self._prob_draw_placeholder(); return

        # Build a networkx graph for display
        directed = algo == "Ford-Fulkerson"
        G = nx.DiGraph() if directed else nx.Graph()
        G.add_nodes_from(nodes)
        for u, v, w in edges:
            G.add_edge(u, v, weight=w)

        pos = nx.circular_layout(G) if len(nodes) <= 8 else nx.spring_layout(G, seed=42)

        # Standard theme node color instead of colorful palette
        node_c = NODE_DEFAULT

        nx.draw_networkx_nodes(G, pos, ax=self.ax_prob,
                               node_color=node_c, node_size=900,
                               edgecolors="white", linewidths=1.5)
        nx.draw_networkx_labels(G, pos, ax=self.ax_prob,
                                labels={n: self._hide_6(n) for n in G.nodes()},
                                font_color="white", font_size=10, font_weight="bold")
        nx.draw_networkx_edges(G, pos, ax=self.ax_prob,
                               edge_color=EDGE_DEFAULT, width=2,
                               arrows=directed, arrowsize=18,
                               connectionstyle="arc3,rad=0.08" if directed else "arc3,rad=0")
        wlbl = {(u, v): str(int(w) if w == int(w) else round(w, 1))
                for u, v, w in edges}
        nx.draw_networkx_edge_labels(G, pos, wlbl, ax=self.ax_prob,
                                     font_color="#fbbf24", font_size=8,
                                     bbox=dict(boxstyle="round,pad=0.2",
                                               fc="#334155", alpha=0.9))
        self.ax_prob.set_title(
            f"Đồ thị minh họa – {algo}",
            color="white", fontsize=10, pad=6)
        self.ax_prob.axis("off")
        self.cv_prob.draw()

    def _run_real_problem(self):
        key  = self.prob_var.get()
        data = self._PROBLEM_DATA.get(key, {})
        algo = data.get("algo", "?")
        self._settext(
            self.r_prob,
            f"[{algo}] đang chạy trên bài toán: {key}\n\n"
            "Chức năng thực thi sẽ được tích hợp từ\n"
            "   src/graph_algorithms/algorithms/ trong bước tiếp theo.\n\n"
            "Đồ thị minh họa đã hiển thị ở trên."
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # GRAPH MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    def _save_state(self):
        import copy
        self.history.append(copy.deepcopy(self.graph))
        if len(self.history) > 50:
            self.history.pop(0)

    def _undo(self):
        if not self.history:
            messagebox.showinfo("Thông báo", "Không có thao tác nào để quay lại!")
            return
        self.graph = self.history.pop()
        self._pos = {}
        self._upd_info()
        self.draw()
        self._update_action_buttons()
        self._show_repr()

    def _nxg(self):
        G = nx.DiGraph() if self.directed.get() else nx.Graph()
        for nd in self.graph: G.add_node(nd)
        seen = set()
        for u in self.graph:
            for v, w in self.graph[u]:
                key = (u, v) if self.directed.get() else tuple(sorted([u, v]))
                if key not in seen: seen.add(key); G.add_edge(u, v, weight=w)
        return G

    def _add_node(self):
        nm = self.e_node.get().strip()
        if not nm: messagebox.showwarning("", "Nhập tên đỉnh!"); return
        if nm in self.graph: messagebox.showwarning("", f"Đỉnh '{nm}' đã tồn tại!"); return
        self._save_state()
        self.graph[nm] = []; self.e_node.delete(0, tk.END)
        self._pos = {}; self._upd_info(); self.draw()
        self._check_add_node_input()

    def _add_edge(self):
        u, v, ws = self.ef.get().strip(), self.et.get().strip(), self.ew.get().strip()
        if not u or not v: messagebox.showwarning("", "Nhập đỉnh nguồn và đỉnh đích!"); return
        try:
            w = float(ws) if ws else 1.0
            if w == int(w): w = int(w)
        except ValueError:
            messagebox.showerror("", "Trọng số phải là số!"); return
        # Lỗi 4: gọi _save_state() TRƯỚC khi thêm node mới
        self._save_state()
        for nd in (u, v):
            if nd not in self.graph: self.graph[nd] = []
        if any(nb == v for nb, _ in self.graph[u]):
            messagebox.showwarning("", f"Cạnh ({u} → {v}) đã tồn tại!"); return
        self.graph[u].append((v, w))
        if not self.directed.get() and not any(nb == u for nb, _ in self.graph[v]):
            self.graph[v].append((u, w))
        self.ef.delete(0, tk.END)
        self.et.delete(0, tk.END)
        self.ew.delete(0, tk.END)
        # Dùng after(0) để defer insert "1" vào ew sau khi tkinter hoàn tất redraw,
        # tránh conflict layout gây nhảy dữ liệu hiển thị ở các ô khác.
        def _restore_ew():
            self.ew.insert(0, "1")
            self._check_add_edge_input()
            self.ef.focus_set()
        self.root.after(0, _restore_ew)
        self._pos = {}; self._upd_info(); self.draw()

    def _delete_node(self):
        if not hasattr(self, 'e_del_node'): return
        nm = self.e_del_node.get().strip()
        if not self._chk(nm): return
        self._save_state()
        del self.graph[nm]
        for u in self.graph:
            self.graph[u] = [(v, w) for v, w in self.graph[u] if v != nm]
        self.e_del_node.delete(0, tk.END)
        self._pos.pop(nm, None)
        self._upd_info(); self.draw()
        self._check_del_node_input()
        messagebox.showinfo("Đã xóa", f"Đã xóa đỉnh '{nm}' và toàn bộ các cạnh liên quan.")

    def _delete_edge(self):
        if not hasattr(self, 'e_del_ef') or not hasattr(self, 'e_del_et'): return
        u = self.e_del_ef.get().strip()
        v = self.e_del_et.get().strip()
        if not u or not v:
            messagebox.showwarning("", "Nhập cả đỉnh nguồn và đỉnh đích cần xóa!"); return
        if u not in self.graph or not any(nb == v for nb, _ in self.graph[u]):
            messagebox.showerror("Lỗi", f"Không tìm thấy cạnh ({u} → {v})!"); return
        # Lỗi 5: dùng _save_state() nhất quán thay vì tự copy
        self._save_state()
        self.graph[u] = [(nb, w) for nb, w in self.graph[u] if nb != v]
        if not self.directed.get() and v in self.graph:
            self.graph[v] = [(nb, w) for nb, w in self.graph[v] if nb != u]
        self.e_del_ef.delete(0, tk.END)
        self.e_del_et.delete(0, tk.END)
        self._pos = {}; self._upd_info(); self.draw()
        self._check_del_edge_input()
        messagebox.showinfo("Đã xóa", f"Đã xóa cạnh ({u} → {v}).")

    def _clear(self):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa sạch toàn bộ đồ thị?"):
            self._save_state()
            self.graph = {}; self._pos = {}; self._upd_info(); self.draw()

    def _type_changed(self): self._pos = {}; self.draw()

    def _refresh(self):
        self._pos = {}; self.draw(); self._show_repr(); self._upd_info()
        self._check_add_node_input()
        self._check_add_edge_input()
        self._check_del_node_input()
        self._check_del_edge_input()
        self._update_action_buttons()

    def _check_add_node_input(self, event=None):
        if not hasattr(self, 'btn_add_node') or not hasattr(self, 'e_node'): return
        val = self.e_node.get().strip()
        if val:
            if hasattr(self, 'sec_node'): self.sec_node.config(fg=SUCCESS)
            self.btn_add_node.config(bg=SUCCESS, fg="white", text="Thêm đỉnh", highlightbackground="#86efac", highlightthickness=2)
        else:
            if hasattr(self, 'sec_node'): self.sec_node.config(fg=ACCENT)
            self.btn_add_node.config(bg="#e2e8f0", fg="#64748b", text="Thêm đỉnh", highlightbackground="#ffffff", highlightthickness=2)

    def _check_add_edge_input(self, event=None):
        if not hasattr(self, 'btn_add_edge') or not hasattr(self, 'ef') or not hasattr(self, 'et'): return
        u = self.ef.get().strip()
        v = self.et.get().strip()
        if u and v:
            if hasattr(self, 'sec_edge'): self.sec_edge.config(fg=SUCCESS)
            self.btn_add_edge.config(bg=SUCCESS, fg="white", text="Thêm cạnh", highlightbackground="#86efac", highlightthickness=2)
        else:
            if hasattr(self, 'sec_edge'): self.sec_edge.config(fg=ACCENT)
            self.btn_add_edge.config(bg="#e2e8f0", fg="#64748b", text="Thêm cạnh", highlightbackground="#ffffff", highlightthickness=2)

    def _check_del_node_input(self, event=None):
        if not hasattr(self, 'btn_del_node') or not hasattr(self, 'e_del_node'): return
        val = self.e_del_node.get().strip()
        if val:
            if hasattr(self, 'sec_del'): self.sec_del.config(fg=ERROR)
            self.btn_del_node.config(bg=ERROR, fg="white", text="Xoá đỉnh", highlightbackground="#fca5a5", highlightthickness=2)
        else:
            self.btn_del_node.config(bg="#e2e8f0", fg="#64748b", text="Xoá đỉnh", highlightbackground="#ffffff", highlightthickness=2)
            u = self.e_del_ef.get().strip() if hasattr(self, 'e_del_ef') else ""
            v = self.e_del_et.get().strip() if hasattr(self, 'e_del_et') else ""
            if not (u and v) and hasattr(self, 'sec_del'):
                self.sec_del.config(fg=ACCENT)

    def _check_del_edge_input(self, event=None):
        if not hasattr(self, 'btn_del_edge') or not hasattr(self, 'e_del_ef') or not hasattr(self, 'e_del_et'): return
        u = self.e_del_ef.get().strip()
        v = self.e_del_et.get().strip()
        if u and v:
            if hasattr(self, 'sec_del'): self.sec_del.config(fg=ERROR)
            self.btn_del_edge.config(bg=ERROR, fg="white", text="Xoá cạnh", highlightbackground="#fca5a5", highlightthickness=2)
        else:
            self.btn_del_edge.config(bg="#e2e8f0", fg="#64748b", text="Xoá cạnh", highlightbackground="#ffffff", highlightthickness=2)
            val = self.e_del_node.get().strip() if hasattr(self, 'e_del_node') else ""
            if not val and hasattr(self, 'sec_del'):
                self.sec_del.config(fg=ACCENT)

    def _update_action_buttons(self):
        has_nodes = len(self.graph) > 0
        if hasattr(self, 'btn_redraw'):
            if has_nodes:
                self.btn_redraw.config(bg=ACCENT2, fg="white", text="Vẽ lại", highlightbackground="#86efac", highlightthickness=2)
            else:
                self.btn_redraw.config(bg="#e2e8f0", fg="#94a3b8", text="Vẽ lại", highlightbackground="#ffffff", highlightthickness=2)
        if hasattr(self, 'btn_save_img'):
            if has_nodes:
                self.btn_save_img.config(bg=SUCCESS, fg="white", text="Lưu hình", highlightbackground="#86efac", highlightthickness=2)
            else:
                self.btn_save_img.config(bg="#e2e8f0", fg="#94a3b8", text="Lưu hình", highlightbackground="#ffffff", highlightthickness=2)

    def _upd_info(self):
        nodes = sorted(self.graph)
        seen, edges = set(), []
        for u in sorted(self.graph):
            for v, w in self.graph[u]:
                key = (u, v) if self.directed.get() else tuple(sorted([u, v]))
                if key not in seen:
                    seen.add(key)
                    arr = "→" if self.directed.get() else "—"
                    wv = int(w) if w == int(w) else w
                    edges.append(f"  {u} {arr} {v}  (w={wv})")
        info = (f"Đỉnh [{len(nodes)}]: {', '.join(nodes) or '(trống)'}\n"
                f"Cạnh [{len(edges)}]:\n" +
                ("\n".join(edges) if edges else "  (trống)"))
        self.info_t.config(state="normal")
        self.info_t.delete("1.0", tk.END)
        self.info_t.insert("1.0", info)
        self.info_t.config(state="disabled")

    def _chk(self, name):
        if not name: messagebox.showwarning("", "Nhập tên đỉnh!"); return False
        if name not in self.graph:
            messagebox.showerror("", f"Đỉnh '{name}' không tồn tại!"); return False
        return True

    # ═══════════════════════════════════════════════════════════════════════════
    # UI HELPERS
    # ═══════════════════════════════════════════════════════════════════════════
    def _section(self, p, title, expand=False):
        outer = tk.Frame(p, bg=BG)
        if expand:
            outer.pack(fill=tk.BOTH, expand=True, pady=(0, 6))
        else:
            outer.pack(fill=tk.X, pady=(0, 6))
        lf = tk.LabelFrame(outer, text=f"  {title}  ",
                           bg=PANEL, fg=ACCENT,
                           font=("Segoe UI", 9, "bold"),
                           relief="solid", bd=1,
                           padx=10, pady=8)
        lf.pack(fill=tk.BOTH, expand=expand)
        return lf

    def _tab_toolbar(self, parent, title):
        tb = tk.Frame(parent, bg=PANEL, relief="flat")
        tb.pack(fill=tk.X, padx=8, pady=(8, 0))
        tk.Label(tb, text=title,
                 font=("Segoe UI", 12, "bold"),
                 bg=PANEL, fg=TEXT).pack(side=tk.LEFT, padx=10, pady=8)
        ttk.Separator(parent, orient="horizontal").pack(fill=tk.X, padx=8, pady=(0, 6))
        return tb

    def _entry(self, parent, width=None):
        kw = dict(bg="white", fg=TEXT, relief="solid", bd=1,
                  font=("Segoe UI", 10), insertbackground=TEXT)
        if width: kw["width"] = width
        return tk.Entry(parent, **kw)

    def _btn(self, parent, text, cmd, color=None, fg="white"):
        color = color or ACCENT
        b = tk.Label(parent, text=text, bg=color, fg=fg,
                     font=("Segoe UI", 9, "bold"), cursor="hand2",
                     padx=10, pady=6, highlightthickness=2, highlightbackground="#ffffff")
        b.bind("<Button-1>", lambda _: cmd())
        b._base_bg = color
        
        def on_enter(e):
            b._base_bg = b.cget("bg")
            _orig_config(bg=self._dk(b._base_bg))
            
        def on_leave(e):
            _orig_config(bg=b._base_bg)
            
        b.bind("<Enter>", on_enter)
        b.bind("<Leave>", on_leave)
        
        _orig_config = b.config
        def _new_config(**kwargs):
            if 'bg' in kwargs:
                b._base_bg = kwargs['bg']
            _orig_config(**kwargs)
        b.config = _new_config
        return b

    def _settext(self, w, text):
        w.config(state="normal"); w.delete("1.0", tk.END)
        w.insert("1.0", text);   w.config(state="disabled")

    @staticmethod
    def _dk(hx):
        """Lỗi 3: bảo vệ crash khi bg không phải mã hex (VD: tên màu hệ thống)."""
        try:
            if not isinstance(hx, str) or len(hx) != 7 or hx[0] != '#':
                return hx  # trả nguyên giá trị nếu không phải hex hợp lệ
            r = max(0, int(int(hx[1:3], 16) * 0.78))
            g = max(0, int(int(hx[3:5], 16) * 0.78))
            b = max(0, int(int(hx[5:7], 16) * 0.78))
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, TypeError):
            return hx  # fallback an toàn


# ═══════════════════════════════════════════════════════════════════════════════
def main():
    root = tk.Tk()
    GraphApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()