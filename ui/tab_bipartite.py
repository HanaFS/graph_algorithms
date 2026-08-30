# ui/tab_bipartite.py
"""
Tab4Mixin – Tab "4. Hai phía": kiểm tra đồ thị hai phía (Bipartite).

Bao gồm:
  _tab4()     : xây dựng layout kết quả + canvas
  _bip_check(): BFS 2-coloring để kiểm tra và tô màu hai tập A/B
"""
import tkinter as tk
from tkinter import ttk
from collections import deque
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .theme import (
    BG, PANEL, ACCENT, SUCCESS, ERROR, WARNING, TEXT, TEXT2,
    GRAPH_BG,
)


class Tab4Mixin:
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
        """Kiểm tra đồ thị hai phía bằng BFS tô màu 2 tập A/B.

        Với đồ thị có hướng, việc kiểm tra dùng cạnh như một quan hệ kề
        (bỏ qua chiều) để xác định hai tập đỉnh, phù hợp với khái niệm
        bipartite graph.
        """
        if not self.graph:
            self.bip_r.config(text="⚠ Đồ thị đang trống", fg=WARNING)
            self.bip_d.config(text="Hãy thêm ít nhất một đỉnh và một cạnh rồi kiểm tra lại.")
            self.draw(ax=self.ax4, cv=self.cv4)
            return

        # Xây adjacency vô hướng: mỗi cạnh chỉ cần đảm bảo hai đầu nằm
        # ở hai màu khác nhau. Điều này cũng xử lý được graph directed.
        adj = {u: set() for u in self.graph}
        for u, items in self.graph.items():
            for v, _w in items:
                adj.setdefault(v, set())
                adj[u].add(v)
                adj[v].add(u)

        color = {}
        ok = True
        conflict = None

        # Duyệt tất cả thành phần liên thông, vì đồ thị có thể không liên thông.
        for start in adj:
            if start in color:
                continue
            color[start] = 0
            q = deque([start])
            while q and ok:
                u = q.popleft()
                for v in sorted(adj[u]):
                    if v not in color:
                        color[v] = 1 - color[u]
                        q.append(v)
                    elif color[v] == color[u]:
                        ok = False
                        conflict = (u, v)
                        break

        if ok:
            group_a = sorted([n for n, c in color.items() if c == 0])
            group_b = sorted([n for n, c in color.items() if c == 1])
            self.bip_r.config(text="✓ ĐỒ THỊ LÀ HAI PHÍA (BIPARTITE)", fg=SUCCESS)
            self.bip_d.config(
                text=(f"Tập A = {{ {', '.join(group_a)} }}    |    "
                      f"Tập B = {{ {', '.join(group_b)} }}\n"
                      "Không có cạnh nào nối hai đỉnh trong cùng một tập."),
                fg=TEXT)

            # Tô màu 2 tập trên canvas Tab 4.
            node_colors = {n: ("#f59e0b" if c == 0 else "#8b5cf6")
                           for n, c in color.items()}
            self.draw(ax=self.ax4, cv=self.cv4, node_colors=node_colors,
                      title="Bipartite: Tập A / Tập B")
        else:
            u, v = conflict
            self.bip_r.config(text="✗ ĐỒ THỊ KHÔNG PHẢI HAI PHÍA", fg=ERROR)
            self.bip_d.config(
                text=(f"Phát hiện xung đột tại cạnh ({u}, {v}): "
                      f"hai đỉnh phải thuộc hai tập khác nhau nhưng hiện cùng màu.\n"
                      "Vì vậy không thể chia toàn bộ đỉnh thành hai tập A/B hợp lệ."),
                fg=ERROR)

            self.draw(ax=self.ax4, cv=self.cv4,
                      hi_n={u, v},
                      hi_e={(u, v), (v, u)},
                      title=f"Xung đột Bipartite: {u} — {v}")
