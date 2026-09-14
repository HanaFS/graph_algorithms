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
        self.directed   = tk.BooleanVar(value=False)
        self._pos: dict = {}
        
        # Quản lý trạng thái tương tác chuột
        self._pending_node = None   # Chờ click chuột đặt đỉnh
        self._dragging_node = None  # Đang giữ chuột để kéo đỉnh

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
        self.et.bind("<KeyRelease>", self._check_add_edge_input)
        self.et.bind("<Return>", lambda _: self._add_edge())

        self.btn_add_edge = self._btn(self.sec_edge, "Thêm cạnh", self._add_edge, color="#e2e8f0", fg="#64748b")
        self.btn_add_edge.pack(fill=tk.X)

        # ── action buttons (Đưa phần này lên trước và neo xuống đáy) ────────
        bf = tk.Frame(p, bg=BG)
        bf.pack(side=tk.BOTTOM, fill=tk.X, pady=(4, 0))
        self._btn(bf, "Tạo đồ thị mẫu", self._create_sample, SUCCESS).pack(fill=tk.X, pady=(0, 4))
        self._btn(bf, "Làm mới",        self._refresh,       ACCENT2).pack(fill=tk.X, pady=(0, 4))
        self._btn(bf, "Xóa sạch toàn bộ đồ thị", self._clear, ERROR).pack(fill=tk.X)

        # ── graph info (Phần này sẽ chiếm khoảng trống còn lại ở giữa) ──────
        inf = self._section(p, "Đồ thị hiện tại", expand=True)
        self.info_t = tk.Text(inf, state="disabled",
                              bg="#f8fafc", fg=TEXT, relief="flat",
                              font=("Consolas", 8), wrap="word",
                              borderwidth=1)
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
        
        ttk.Separator(p, orient="horizontal").pack(fill=tk.X, padx=8)

        # matplotlib canvas
        self.fig1 = Figure(figsize=(9, 5.5), facecolor=GRAPH_BG)
        self.ax1 = self.fig1.add_subplot(111)
        self.ax1.set_facecolor(GRAPH_BG)
        self.cv1 = FigureCanvasTkAgg(self.fig1, p)
        self.cv1.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Bắt các sự kiện chuột (click, di chuyển, thả)
        self.cv1.mpl_connect('button_press_event', self._on_mouse_press)
        self.cv1.mpl_connect('motion_notify_event', self._on_mouse_motion)
        self.cv1.mpl_connect('button_release_event', self._on_mouse_release)
        
        self.draw()

    def _on_mouse_press(self, event):
        if event.xdata is None or event.ydata is None: return

        # 1. Nếu đang ở trạng thái chờ ĐẶT ĐỈNH MỚI
        if getattr(self, '_pending_node', None):
            nm = self._pending_node
            self._pending_node = None
            
            self.btn_add_node.config(text="Thêm đỉnh", bg=SUCCESS)
            self.e_node.delete(0, tk.END)

            self.graph[nm] = []
            self._pos[nm] = (event.xdata, event.ydata)

            self._upd_info()
            self.draw()
            self._check_add_node_input()
            return

        # 2. Nếu không phải đặt đỉnh mới, kiểm tra xem có CLICK VÀO ĐỈNH CŨ để kéo không
        closest_node = None
        min_dist = float('inf')
        
        # Tìm đỉnh gần với vị trí click nhất
        for node, (nx, ny) in self._pos.items():
            dist = (nx - event.xdata)**2 + (ny - event.ydata)**2
            if dist < min_dist:
                min_dist = dist
                closest_node = node

        # Tính toán bán kính bắt chuột hợp lý
        xlim = self.ax1.get_xlim()
        threshold = ((xlim[1] - xlim[0]) * 0.04) ** 2

        # Nếu click trúng hoặc đủ gần một đỉnh -> Bắt đầu kéo
        if closest_node and min_dist < threshold:
            self._dragging_node = closest_node

    def _on_mouse_motion(self, event):
        # Nếu đang giữ chuột vào 1 đỉnh và di chuyển
        if getattr(self, '_dragging_node', None):
            if event.xdata is None or event.ydata is None: return
            
            # Cập nhật toạ độ mới cho đỉnh đó
            self._pos[self._dragging_node] = (event.xdata, event.ydata)
            self.draw()

    def _on_mouse_release(self, event):
        # Nhả chuột ra thì kết thúc việc kéo đỉnh
        if getattr(self, '_dragging_node', None):
            self._dragging_node = None
            self.draw()

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
            
            # Setup giới hạn cho trục để click chuột lần đầu có toạ độ
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 10)
            
            if title:
                ax.set_title(title, color="white", fontsize=11, pad=6)
            ax.axis("off"); cv.draw(); return

        G = self._nxg()
        
        # Nếu chưa có đỉnh nào, thiết lập không gian toạ độ
        if not G.nodes():
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 10)
            
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
            nx.draw_networkx_edge_labels(G, pos, wlbl, ax=ax,
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
        s = self.e_ts.get().strip()
        if not self._chk(s): return
        order, edges = self._bfs(s)
        self._settext(self.rb, f"BFS từ '{s}':\n{' → '.join(order)}")
        self.draw(hi_n=set(order), hi_e=set(edges), title=f"BFS từ '{s}'")
        self.nb.select(0)

    def _dfs_run(self):
        s = self.e_ts.get().strip()
        if not self._chk(s): return
        order, edges = self._dfs(s)
        self._settext(self.rd, f"DFS từ '{s}':\n{' → '.join(order)}")
        self.draw(hi_n=set(order), hi_e=set(edges), title=f"DFS từ '{s}'")
        self.nb.select(0)

    def _cmp_trav(self, ra, ma, ca):
        raw = getattr(self, ra).get("1.0", tk.END).strip()
        man = getattr(self, ma).get().strip()
        lbl = getattr(self, ca)
        if not raw: lbl.config(text="Chạy thuật toán trước!", fg=WARNING); return
        if not man: lbl.config(text="Nhập kết quả chạy tay!", fg=WARNING); return
        algo = []
        for line in raw.splitlines():
            if "→" in line:
                algo = [x.strip() for x in line.split("→") if x.strip()]; break
        hand = [x.strip() for x in man.replace("→", ",").split(",") if x.strip()]
        if algo == hand:
            lbl.config(text="Kết quả KHỚP hoàn toàn!", fg=SUCCESS)
        else:
            lbl.config(text=f"Không khớp!\n"
                            f"Thuật toán: {' → '.join(algo)}\n"
                            f"Chạy tay:   {' → '.join(hand)}", fg=ERROR)

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
        if not self.graph: messagebox.showwarning("", "Đồ thị đang trống!"); return
        ok, cmap, why = self._is_bip()
        self.ax4.clear()
        self.ax4.set_facecolor(GRAPH_BG)
        self.fig4.patch.set_facecolor(GRAPH_BG)
        G   = self._nxg()
        pos = nx.spring_layout(G, seed=42, k=2)

        if ok:
            self.bip_r.config(text="Đây LÀ đồ thị hai phía  (Bipartite Graph)!", fg=SUCCESS)
            sa = sorted(n for n, c in cmap.items() if c == 0)
            sb = sorted(n for n, c in cmap.items() if c == 1)
            self.bip_d.config(
                text=f"Tập A (màu xanh lam) : {{ {', '.join(sa)} }}\n"
                     f"Tập B (màu cam)        : {{ {', '.join(sb)} }}\n\n"
                     f"Mọi cạnh đều nối một đỉnh ở tập A với một đỉnh ở tập B.",
                fg=TEXT)
            nc = ["#3b82f6" if cmap.get(n, 0) == 0 else "#f97316" for n in G.nodes()]
            leg = [Patch(facecolor="#3b82f6", label="Tập A"),
                   Patch(facecolor="#f97316", label="Tập B")]
        else:
            self.bip_r.config(text="Đây KHÔNG phải đồ thị hai phía!", fg=ERROR)
            self.bip_d.config(
                text=f"Lý do: {why}\n\n"
                     f"Đồ thị hai phía không được chứa chu trình có độ dài lẻ.",
                fg=TEXT)
            nc = ["#ef4444" for _ in G.nodes()]
            leg = []

        nx.draw_networkx_nodes(G, pos, ax=self.ax4, node_color=nc,
                               node_size=850, edgecolors="white", linewidths=1.5)
        nx.draw_networkx_labels(G, pos, ax=self.ax4,
                                font_color="white", font_size=11, font_weight="bold")
        d = self.directed.get()
        if d:
            nx.draw_networkx_edges(G, pos, ax=self.ax4,
                                   edge_color=EDGE_DEFAULT, width=2,
                                   arrows=True, arrowsize=18)
        else:
            nx.draw_networkx_edges(G, pos, ax=self.ax4,
                                   edge_color=EDGE_DEFAULT, width=2,
                                   arrows=False)
        if leg:
            self.ax4.legend(handles=leg, loc="upper right",
                            facecolor="#334155", labelcolor="white", fontsize=10)
        self.ax4.axis("off"); self.cv4.draw()

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

            tk.Label(cf, text="Đường đi (ví dụ: A,B,C):",
                     bg=PANEL, fg=TEXT2, font=("Segoe UI", 8)).pack(anchor="w", padx=12, pady=(4, 0))
            mp = self._entry(cf); mp.pack(fill=tk.X, padx=12, pady=(2, 4))
            setattr(self, mpa, mp)

            tk.Label(cf, text="Khoảng cách (ví dụ: 7):",
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
        src, tgt = self.e_src.get().strip(), self.e_tgt.get().strip()
        if not self._chk(src) or not self._chk(tgt): return
        dist, prev = self._dijkstra(src)
        path = self._mkpath(prev, src, tgt)
        self._show_sp(self.rdi, src, tgt, dist, path, "Dijkstra")
        if path:
            pe = {(path[i], path[i+1]) for i in range(len(path)-1)}
            self.draw(hi_n=set(path), hi_e=pe, title=f"Dijkstra: {src} → {tgt}")
            self.nb.select(0)

    def _bf_run(self):
        src, tgt = self.e_src.get().strip(), self.e_tgt.get().strip()
        if not self._chk(src) or not self._chk(tgt): return
        res = self._bellman_ford(src)
        if res is None:
            self._settext(self.rbf, "Đồ thị có chu trình trọng số âm!\n"
                                    "    Bellman-Ford không thể giải quyết."); return
        dist, prev = res
        path = self._mkpath(prev, src, tgt)
        self._show_sp(self.rbf, src, tgt, dist, path, "Bellman-Ford")
        if path:
            pe = {(path[i], path[i+1]) for i in range(len(path)-1)}
            self.draw(hi_n=set(path), hi_e=pe, title=f"Bellman-Ford: {src} → {tgt}")
            self.nb.select(0)

    def _show_sp(self, widget, src, tgt, dist, path, algo):
        d = dist.get(tgt, math.inf)
        if d == math.inf:
            self._settext(widget, f"Không tìm thấy đường đi từ '{src}' đến '{tgt}'"); return
        dv = int(d) if d == int(d) else d
        lines = [
            f"Đường đi ngắn nhất  ({src} → {tgt})",
            f"  {'  →  '.join(path)}",
            "",
            f"Tổng khoảng cách: {dv}",
            "",
            f"Bảng khoảng cách từ '{src}'  ({algo}):",
        ]
        for nd in sorted(dist):
            v = dist[nd]
            vs = "∞" if v == math.inf else str(int(v) if v == int(v) else v)
            lines.append(f"  d({nd}) = {vs}")
        self._settext(widget, "\n".join(lines))

    def _cmp_sp(self, ra, mpa, mda, ca):
        raw = getattr(self, ra).get("1.0", tk.END).strip()
        lbl = getattr(self, ca)
        if not raw: lbl.config(text="Chạy thuật toán trước!", fg=WARNING); return
        mpt = getattr(self, mpa).get().strip()
        mdt = getattr(self, mda).get().strip()
        if not mpt or not mdt:
            lbl.config(text="Nhập đủ đường đi và khoảng cách!", fg=WARNING); return
        try: mdist = float(mdt)
        except ValueError:
            lbl.config(text="Khoảng cách phải là số!", fg=WARNING); return
        mpath = [x.strip() for x in mpt.replace("→", ",").split(",") if x.strip()]
        adist, apath = None, []
        for line in raw.splitlines():
            if "Tổng khoảng cách:" in line:
                try: adist = float(line.split(":")[1].strip())
                except: pass
            if "→" in line and "(" not in line and "Đường" not in line:
                apath = [x.strip() for x in line.replace("  →  ", "→").split("→") if x.strip()]
        d_ok = adist == mdist; p_ok = apath == mpath
        if d_ok and p_ok:
            lbl.config(text="Kết quả KHỚP hoàn toàn!", fg=SUCCESS)
        else:
            msg = "✖  Không khớp!\n"
            if not d_ok: msg += f"Khoảng cách – Thuật toán: {adist}  |  Tay: {mdist}\n"
            if not p_ok: msg += (f"Đường đi – TT: {' → '.join(apath)}\n"
                                  f"           Tay: {' → '.join(mpath)}")
            lbl.config(text=msg, fg=ERROR)

    # ═══════════════════════════════════════════════════════════════════════════
    # PURE-PYTHON ALGORITHMS
    # ═══════════════════════════════════════════════════════════════════════════
    def _bfs(self, start):
        visited, queue, order, edges = set(), deque([start]), [], []
        par = {start: None}
        while queue:
            u = queue.popleft()
            if u in visited: continue
            visited.add(u); order.append(u)
            for v, _ in sorted(self.graph.get(u, []), key=lambda x: x[0]):
                if v not in visited:
                    if v not in par: par[v] = u; edges.append((u, v))
                    queue.append(v)
        return order, edges

    def _dfs(self, start):
        visited, order, edges = set(), [], []
        def r(u):
            visited.add(u); order.append(u)
            for v, _ in sorted(self.graph.get(u, []), key=lambda x: x[0]):
                if v not in visited: edges.append((u, v)); r(v)
        r(start)
        return order, edges

    def _dijkstra(self, src):
        dist = {n: math.inf for n in self.graph}; dist[src] = 0
        prev = {src: None}; heap = [(0, src)]
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]: continue
            for v, w in self.graph.get(u, []):
                nd = dist[u] + w
                if nd < dist[v]:
                    dist[v] = nd; prev[v] = u
                    heapq.heappush(heap, (nd, v))
        return dist, prev

    def _bellman_ford(self, src):
        nodes = list(self.graph)
        dist = {n: math.inf for n in nodes}; dist[src] = 0
        prev = {src: None}
        el = []
        for u in self.graph:
            for v, w in self.graph[u]:
                el.append((u, v, w))
                if not self.directed.get(): el.append((v, u, w))
        for _ in range(len(nodes) - 1):
            upd = False
            for u, v, w in el:
                if dist[u] != math.inf and dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w; prev[v] = u; upd = True
            if not upd: break
        for u, v, w in el:
            if dist[u] != math.inf and dist[u] + w < dist[v]:
                return None
        return dist, prev

    def _mkpath(self, prev, src, tgt):
        if tgt not in prev and tgt != src: return []
        path, cur = [], tgt
        while cur is not None: path.append(cur); cur = prev.get(cur)
        path.reverse()
        return path if path and path[0] == src else []

    def _is_bip(self):
        color = {}
        for start in self.graph:
            if start in color: continue
            queue = deque([start]); color[start] = 0
            while queue:
                u = queue.popleft()
                nbs = [v for v, _ in self.graph.get(u, [])]
                if not self.directed.get():
                    for x in self.graph:
                        for v, _ in self.graph[x]:
                            if v == u and x not in nbs: nbs.append(x)
                for nb in nbs:
                    if nb not in color: color[nb] = 1 - color[u]; queue.append(nb)
                    elif color[nb] == color[u]:
                        return False, color, f"Đỉnh '{u}' và '{nb}' cùng màu nhưng có cạnh nối"
        return True, color, ""

    # ═══════════════════════════════════════════════════════════════════════════
    # GRAPH MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    def _nxg(self):
        G = nx.DiGraph() if self.directed.get() else nx.Graph()
        for nd in self.graph: G.add_node(nd)
        seen = set()
        for u in self.graph:
            for v, w in self.graph[u]:
                key = (u, v) if self.directed.get() else tuple(sorted([u, v]))
                if key not in seen: seen.add(key); G.add_edge(u, v, weight=w)
        return G

    def _create_sample(self):
        """Hàm sinh ra một đồ thị mẫu kinh điển có sẵn 6 đỉnh và nhiều cạnh"""
        if self.graph:
            if not messagebox.askyesno("Xác nhận", "Thao tác này sẽ xóa đồ thị hiện tại để tạo đồ thị mẫu. Bạn có muốn tiếp tục?"):
                return
        
        # Mặc định chuyển thành đồ thị vô hướng cho mẫu dễ nhìn
        self.directed.set(False)
        
        # Tạo dữ liệu đồ thị mẫu
        self.graph = {
            'A': [('B', 4.0), ('C', 2.0)],
            'B': [('A', 4.0), ('C', 1.0), ('D', 5.0)],
            'C': [('A', 2.0), ('B', 1.0), ('D', 8.0), ('E', 10.0)],
            'D': [('B', 5.0), ('C', 8.0), ('E', 2.0), ('F', 6.0)],
            'E': [('C', 10.0), ('D', 2.0), ('F', 3.0)],
            'F': [('D', 6.0), ('E', 3.0)]
        }
        
        # Xếp chỗ tọa độ đẹp mắt sẵn
        self._pos = {
            'A': (1.5, 5.0),
            'B': (4.0, 8.0),
            'C': (4.0, 2.0),
            'D': (7.0, 8.0),
            'E': (7.0, 2.0),
            'F': (9.5, 5.0)
        }
        
        self._refresh()

    def _add_node(self):
        # Nếu đang ở chế độ chờ click, bấm nút này lần nữa để Hủy
        if getattr(self, '_pending_node', None):
            self._pending_node = None
            self.btn_add_node.config(text="Thêm đỉnh", bg=SUCCESS)
            self.draw()
            return

        nm = self.e_node.get().strip()
        if not nm: messagebox.showwarning("", "Nhập tên đỉnh!"); return
        if nm in self.graph: messagebox.showwarning("", f"Đỉnh '{nm}' đã tồn tại!"); return
        
        # Bật trạng thái chờ người dùng click đặt đỉnh
        self._pending_node = nm
        self.btn_add_node.config(text="Hủy đặt đỉnh", bg=WARNING)
        self.draw(title=f"Nhấn chuột vào bảng vẽ bên phải để đặt vị trí cho đỉnh '{nm}'")

    def _add_edge(self):
        u, v, ws = self.ef.get().strip(), self.et.get().strip(), self.ew.get().strip()
        if not u or not v: messagebox.showwarning("", "Nhập đỉnh nguồn và đỉnh đích!"); return
        try:
            w = float(ws) if ws else 1.0
            if w == int(w): w = int(w)
        except ValueError:
            messagebox.showerror("", "Trọng số phải là số!"); return
        for nd in (u, v):
            if nd not in self.graph: self.graph[nd] = []
        if any(nb == v for nb, _ in self.graph[u]):
            messagebox.showwarning("", f"Cạnh ({u} → {v}) đã tồn tại!"); return
        self.graph[u].append((v, w))
        if not self.directed.get() and not any(nb == u for nb, _ in self.graph[v]):
            self.graph[v].append((u, w))
        for e in (self.ef, self.et): e.delete(0, tk.END)
        self.ew.delete(0, tk.END); self.ew.insert(0, "1")
        self._upd_info(); self.draw()
        self._check_add_edge_input()

    def _delete_node(self):
        if not hasattr(self, 'e_del_node'): return
        nm = self.e_del_node.get().strip()
        if not self._chk(nm): return
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
        found = False
        if u in self.graph:
            orig_len = len(self.graph[u])
            self.graph[u] = [(nb, w) for nb, w in self.graph[u] if nb != v]
            if len(self.graph[u]) < orig_len: found = True
        if not self.directed.get() and v in self.graph:
            self.graph[v] = [(nb, w) for nb, w in self.graph[v] if nb != u]
        if found:
            self.e_del_ef.delete(0, tk.END)
            self.e_del_et.delete(0, tk.END)
            self._upd_info(); self.draw()
            self._check_del_edge_input()
            messagebox.showinfo("Đã xóa", f"Đã xóa cạnh ({u} → {v}).")
        else:
            messagebox.showerror("Lỗi", f"Không tìm thấy cạnh ({u} → {v})!")

    def _clear(self):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa sạch toàn bộ đồ thị?"):
            self.graph = {}
            self._pos = {}
            self._refresh()

    def _type_changed(self): self.draw()

    def _refresh(self):
        self.draw(); self._show_repr(); self._upd_info()
        self._check_add_node_input()
        self._check_add_edge_input()
        self._check_del_node_input()
        self._check_del_edge_input()
        self._update_action_buttons()

    def _check_add_node_input(self, event=None):
        if not hasattr(self, 'btn_add_node') or not hasattr(self, 'e_node'): return
        
        # Tránh lỗi đè màu của nút lúc đang bật chế độ chờ click 
        if getattr(self, '_pending_node', None): return 
        
        val = self.e_node.get().strip()
        if val:
            if hasattr(self, 'sec_node'): self.sec_node.config(fg=SUCCESS)
            self.btn_add_node.config(bg=SUCCESS, fg="white", text="Thêm đỉnh", highlightbackground="#86efac", highlightthickness=2)
        else:
            if hasattr(self, 'sec_node'): self.sec_node.config(fg=ACCENT)
            self.btn_add_node.config(bg="#e2e8f0", fg="#64748b", text="Thêm đỉnh", highlightthickness=0)

    def _check_add_edge_input(self, event=None):
        if not hasattr(self, 'btn_add_edge') or not hasattr(self, 'ef') or not hasattr(self, 'et'): return
        u = self.ef.get().strip()
        v = self.et.get().strip()
        if u and v:
            if hasattr(self, 'sec_edge'): self.sec_edge.config(fg=SUCCESS)
            self.btn_add_edge.config(bg=SUCCESS, fg="white", text="Thêm cạnh", highlightbackground="#86efac", highlightthickness=2)
        else:
            if hasattr(self, 'sec_edge'): self.sec_edge.config(fg=ACCENT)
            self.btn_add_edge.config(bg="#e2e8f0", fg="#64748b", text="Thêm cạnh", highlightthickness=0)

    def _check_del_node_input(self, event=None):
        if not hasattr(self, 'btn_del_node') or not hasattr(self, 'e_del_node'): return
        val = self.e_del_node.get().strip()
        if val:
            if hasattr(self, 'sec_del'): self.sec_del.config(fg=ERROR)
            self.btn_del_node.config(bg=ERROR, fg="white", text="Xoá đỉnh", highlightbackground="#fca5a5", highlightthickness=2)
        else:
            self.btn_del_node.config(bg="#e2e8f0", fg="#64748b", text="Xoá đỉnh", highlightthickness=0)
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
            self.btn_del_edge.config(bg="#e2e8f0", fg="#64748b", text="Xoá cạnh", highlightthickness=0)
            val = self.e_del_node.get().strip() if hasattr(self, 'e_del_node') else ""
            if not val and hasattr(self, 'sec_del'):
                self.sec_del.config(fg=ACCENT)

    def _update_action_buttons(self):
        has_nodes = len(self.graph) > 0
        if hasattr(self, 'btn_redraw'):
            if has_nodes:
                self.btn_redraw.config(bg=ACCENT2, fg="white", text="Vẽ lại", highlightthickness=2)
            else:
                self.btn_redraw.config(bg="#e2e8f0", fg="#94a3b8", text="Vẽ lại", highlightthickness=0)
        if hasattr(self, 'btn_save_img'):
            if has_nodes:
                self.btn_save_img.config(bg=SUCCESS, fg="white", text="Lưu hình", highlightthickness=2)
            else:
                self.btn_save_img.config(bg="#e2e8f0", fg="#94a3b8", text="Lưu hình", highlightthickness=0)

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
                     padx=10, pady=6)
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
        r = max(0, int(int(hx[1:3], 16) * 0.78))
        g = max(0, int(int(hx[3:5], 16) * 0.78))
        b = max(0, int(int(hx[5:7], 16) * 0.78))
        return f"#{r:02x}{g:02x}{b:02x}"


# ═══════════════════════════════════════════════════════════════════════════════
def main():
    root = tk.Tk()
    GraphApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()