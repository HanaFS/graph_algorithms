# ui/tab_advanced.py
"""
Tab6Mixin – Tab "6. Thuật toán nâng cao" (Fleury, Hierholzer, Prim, Kruskal, Ford-Fulkerson).

Bao gồm:
  _tab6()                : khung chính chia sub-tabs
  _algo_layout()         : helper tạo layout 2 cột cho mỗi thuật toán
  _algo_canvas()         : helper tạo canvas vẽ đồ thị
  _result_box()          : helper tạo khung hiển thị text kết quả
  _draw_mst_result()     : vẽ đồ thị với các cạnh MST được tô màu
  _draw_euler_result()   : vẽ đồ thị với chu trình/đường đi Euler
  _draw_flow_result()    : vẽ mạng luồng
  _step_algo()           : xử lý step-by-step
  _run_*                 : gọi logic thuật toán và hiển thị
"""
import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Patch

from .theme import (
    BG, PANEL, ACCENT, SUCCESS, ERROR, WARNING, TEXT, TEXT2,
    GRAPH_BG, NODE_DEFAULT, NODE_HI, EDGE_DEFAULT, EDGE_HI,
    _ALGO_AVAILABLE, _ALGO_ERROR,
    prim, kruskal, fleury, hierholzer, ford_fulkerson, check_euler_condition
)


class Tab6Mixin:
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
                    font=("Courier New", 9), relief="flat",
                    state="disabled", padx=6, pady=4, wrap="word")
        t.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        return t

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
        self.e_fleury_start = ttk.Combobox(left, state="readonly", font=("Segoe UI", 10))
        self.e_fleury_start.pack(fill=tk.X, padx=10, pady=(0, 8))

        self._btn(left, "Chạy Fleury",
                  lambda: self._run_fleury(),
                  color=ACCENT).pack(fill=tk.X, padx=10, pady=(0, 6))

        ttk.Separator(left, orient="horizontal").pack(fill=tk.X, padx=10, pady=4)
        self.r_fleury = self._result_box(left, height=7, bg="#f0fdf4", fg=SUCCESS)

        # legend note removed

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
        self.e_hier_start = ttk.Combobox(left, state="readonly", font=("Segoe UI", 10))
        self.e_hier_start.pack(fill=tk.X, padx=10, pady=(0, 8))

        self._btn(left, "Chạy Hierholzer",
                  lambda: self._run_hierholzer(),
                  color=ACCENT).pack(fill=tk.X, padx=10, pady=(0, 6))

        ttk.Separator(left, orient="horizontal").pack(fill=tk.X, padx=10, pady=4)
        self.r_hier = self._result_box(left, height=7, bg="#f0fdf4", fg=SUCCESS)

        # Note removed

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
        self.e_prim_root = ttk.Combobox(left, state="readonly", font=("Segoe UI", 10))
        self.e_prim_root.pack(fill=tk.X, padx=10, pady=(0, 8))

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
            e = ttk.Combobox(left, state="readonly", font=("Segoe UI", 10))
            e.pack(fill=tk.X, padx=10, pady=(0, 4))
            setattr(self, attr, e)

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
