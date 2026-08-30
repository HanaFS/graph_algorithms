# ui/tab_graph.py
"""
Tab1Mixin – Tab "1. Đồ thị": trực quan hoá đồ thị với matplotlib.

Bao gồm:
  _tab1()      : xây dựng toolbar + canvas matplotlib
  draw()       : vẽ đồ thị lên bất kỳ ax/cv nào
  _save_img()  : lưu hình ảnh đồ thị
  _hide_6()    : hàm tiện ích hiển thị số 6 dễ phân biệt
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import networkx as nx
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .theme import (
    BG, PANEL, ACCENT, ACCENT2, SUCCESS, WARNING, ERROR, TEXT, TEXT2,
    GRAPH_BG, NODE_DEFAULT, NODE_HI, EDGE_DEFAULT, EDGE_HI,
)


class Tab1Mixin:
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

        self.sec_del = tk.Label(del_tb, text="Thao tác xóa:", bg=PANEL, fg=ACCENT,
                                font=("Segoe UI", 9, "bold"))
        self.sec_del.pack(side=tk.LEFT, padx=(0, 5))

        # Delete Node
        self.e_del_node = self._entry(del_tb, width=6)
        self.e_del_node.pack(side=tk.LEFT, padx=(0, 4))
        self.e_del_node.bind("<Return>",    lambda _: self._delete_node())
        self.e_del_node.bind("<KeyRelease>", self._check_del_node_input)
        self.e_del_node.bind("<FocusIn>",   self._check_del_node_input)
        self.e_del_node.bind("<FocusOut>",  self._check_del_node_input)

        self.btn_del_node = self._btn(del_tb, "Xoá đỉnh", self._delete_node,
                                      color="#e2e8f0", fg="#64748b")
        self.btn_del_node.pack(side=tk.LEFT, padx=(0, 10))

        # Delete Edge
        tk.Label(del_tb, text="Cạnh:", bg=PANEL, fg=TEXT2,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 2))

        self.e_del_ef = self._entry(del_tb, width=4)
        self.e_del_ef.pack(side=tk.LEFT, padx=(0, 2))
        self.e_del_ef.bind("<KeyRelease>", self._check_del_edge_input)

        tk.Label(del_tb, text="→", bg=PANEL, fg=TEXT2).pack(side=tk.LEFT)

        self.e_del_et = self._entry(del_tb, width=4)
        self.e_del_et.pack(side=tk.LEFT, padx=(2, 4))
        self.e_del_et.bind("<KeyRelease>", self._check_del_edge_input)
        self.e_del_et.bind("<Return>",     lambda _: self._delete_edge())

        self.btn_del_edge = self._btn(del_tb, "Xoá cạnh", self._delete_edge,
                                      color="#e2e8f0", fg="#64748b")
        self.btn_del_edge.pack(side=tk.LEFT)

        self.btn_save_graph = self._btn(tb, "Lưu đồ thị", self._save_graph, ACCENT)
        self.btn_save_graph.pack(side=tk.RIGHT, padx=6, pady=6)

        self.btn_load_graph = self._btn(tb, "Chọn đồ thị", self._load_graph_main, color="#64748b", fg="white")
        self.btn_load_graph.pack(side=tk.RIGHT, padx=2, pady=6)
        self.btn_save_graph.pack(side=tk.RIGHT, padx=6, pady=6)

        self.btn_save_img = self._btn(tb, "Lưu hình", self._save_img, SUCCESS)
        self.btn_save_img.pack(side=tk.RIGHT, padx=(0, 2), pady=6)



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
            if not any(fp.lower().endswith(ext) for ext in [".png", ".pdf", ".svg"]):
                fp += ".png"
            try:
                self.fig1.savefig(fp, dpi=160, bbox_inches="tight", facecolor=GRAPH_BG)
                messagebox.showinfo("Đã lưu", f"Hình đồ thị đã lưu tại:\n{fp}")
            except Exception as e:
                messagebox.showerror("Lỗi khi lưu", f"Không thể lưu hình:\n{e}")

    def _save_graph(self):
        """Lưu cấu trúc dữ liệu đồ thị dưới dạng JSON hoặc TXT."""
        if not self.graph:
            messagebox.showwarning("Thông báo", "Đồ thị đang trống, không có dữ liệu để lưu!")
            return
        fp = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[
                ("JSON Graph (*.json)", "*.json"),
                ("Text File (*.txt)", "*.txt"),
                ("Tất cả tệp (*.*)", "*.*")
            ],
            title="Lưu dữ liệu đồ thị"
        )
        if not fp:
            return
        try:
            # Kiểm tra macOS không tự điền đuôi file
            if not (fp.lower().endswith(".json") or fp.lower().endswith(".txt")):
                fp += ".json"
                
            if fp.lower().endswith(".json"):
                import json
                data = {
                    "directed": self.directed.get(),
                    "graph": self.graph
                }
                with open(fp, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                with open(fp, "w", encoding="utf-8") as f:
                    f.write(f"# Directed: {self.directed.get()}\n")
                    f.write(f"# Format: From To Weight\n")
                    seen = set()
                    for u in sorted(self.graph):
                        if not self.graph[u]:
                            f.write(f"{u}\n")
                        for v, w in self.graph[u]:
                            key = (u, v) if self.directed.get() else tuple(sorted([u, v]))
                            if key not in seen:
                                seen.add(key)
                                f.write(f"{u} {v} {w}\n")
            messagebox.showinfo("Thành công", f"Đã lưu dữ liệu đồ thị vào:\n{fp}")
        except Exception as e:
            messagebox.showerror("Lỗi khi lưu", f"Không thể lưu tệp:\n{e}")

    def _load_graph_main(self):
        """Nạp đồ thị từ tệp JSON hoặc TXT vào ứng dụng chính."""
        fp = filedialog.askopenfilename(
            filetypes=[
                ("JSON/TXT Files", "*.json *.txt"),
                ("JSON Graph", "*.json"),
                ("Text File", "*.txt"),
                ("Tất cả tệp", "*.*")
            ],
            title="Chọn đồ thị"
        )
        if not fp:
            return
            
        try:
            self.graph = {}
            self._pos = {}
            
            if fp.endswith(".json"):
                import json
                with open(fp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.directed.set(data.get("directed", False))
                self.graph = data.get("graph", {})
            else:
                with open(fp, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                is_directed = False
                for line in lines:
                    line = line.strip()
                    if not line: continue
                    if line.startswith("# Directed:"):
                        is_directed = "True" in line
                        continue
                    if line.startswith("#"): continue
                    parts = line.split()
                    if len(parts) == 1:
                        u = parts[0]
                        if u not in self.graph: self.graph[u] = []
                    elif len(parts) >= 3:
                        u, v, w = parts[0], parts[1], float(parts[2])
                        self.graph.setdefault(u, []).append((v, w))
                        if v not in self.graph: self.graph[v] = []
                self.directed.set(is_directed)
                
            self._upd_info()
            self.draw()
            messagebox.showinfo("Thành công", f"Đã nạp đồ thị từ:\n{fp}")
            
        except Exception as e:
            messagebox.showerror("Lỗi khi nạp", f"Không thể nạp tệp:\n{e}")

