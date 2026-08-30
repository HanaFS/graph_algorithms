# ui/tab_traversal.py
"""
Tab3Mixin – Tab "3. Duyệt BFS/DFS".

Bao gồm:
  _tab3()                 : xây dựng layout 2 cột BFS/DFS
  _bfs_run()              : chạy BFS và hiển thị kết quả
  _dfs_run()              : chạy DFS và hiển thị kết quả
  _parse_traversal_input(): chuẩn hóa chuỗi nhập tay
  _cmp_trav()             : so sánh kết quả chạy tay vs thuật toán
"""
import tkinter as tk
from tkinter import ttk, messagebox
import re
from collections import deque
from .theme import BG, PANEL, ACCENT, ACCENT2, SUCCESS, WARNING, ERROR, TEXT, TEXT2


class Tab3Mixin:
    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 3 – TRAVERSAL
    # ═══════════════════════════════════════════════════════════════════════════
    def _tab3(self, p):
        tb = self._tab_toolbar(p, "Duyệt đồ thị: BFS & DFS")

        ctrl = tk.Frame(p, bg=PANEL, relief="solid", bd=1)
        ctrl.pack(fill=tk.X, padx=8, pady=(0, 6))
        tk.Label(ctrl, text="Đỉnh xuất phát:", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 10)).grid(row=0, column=0, padx=12, pady=10, sticky="w")
        self.e_ts = ttk.Combobox(ctrl, width=12, state="readonly", font=("Segoe UI", 10))
        self.e_ts.grid(row=0, column=1, padx=6, pady=10, sticky="ew")
        ctrl.columnconfigure(1, weight=1)
        self._btn(ctrl, "▶ BFS", self._bfs_run).grid(row=0, column=2, padx=6, pady=10)
        self._btn(ctrl, "▶ DFS", self._dfs_run, ACCENT2).grid(row=0, column=3, padx=6, pady=10)

        # two result columns
        cols = tk.Frame(p, bg=BG)
        cols.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        for col, (lbl, clr, ra) in enumerate([
            ("BFS – Breadth First Search", ACCENT,  "rb"),
            ("DFS – Depth First Search",   ACCENT2, "rd"),
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
                         font=("Courier New", 11), relief="flat", state="disabled", padx=6, pady=4)
            rt.pack(fill=tk.X, padx=12, pady=(0, 10))
            setattr(self, ra, rt)

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
