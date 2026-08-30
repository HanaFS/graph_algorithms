# ui/tab_shortest.py
"""
Tab5Mixin – Tab "5. Đường ngắn nhất" (Dijkstra & Bellman-Ford).

Bao gồm:
  _tab5()    : xây dựng layout 2 cột
  _dijk_run(): placeholder Dijkstra
  _bf_run()  : placeholder Bellman-Ford
  _show_sp() : hiển thị kết quả đường ngắn nhất
  _cmp_sp()  : so sánh kết quả chạy tay
"""
import tkinter as tk
from tkinter import ttk, messagebox
from .theme import BG, PANEL, ACCENT, ACCENT2, SUCCESS, TEXT, TEXT2


class Tab5Mixin:
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
            e = ttk.Combobox(ctrl, width=10, state="readonly", font=("Segoe UI", 10))
            e.grid(row=0, column=col*2+1, sticky="ew", padx=6, pady=10)
            setattr(self, attr, e)
        self._btn(ctrl, "Dijkstra",     self._dijk_run).grid(row=0, column=4, padx=6, pady=10)
        self._btn(ctrl, "Bellman-Ford", self._bf_run, ACCENT2).grid(row=0, column=5, padx=6, pady=10)

        cols = tk.Frame(p, bg=BG)
        cols.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        for col, (lbl, clr, ra) in enumerate([
            ("Dijkstra",     ACCENT,  "rdi"),
            ("Bellman-Ford", ACCENT2, "rbf"),
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
                         font=("Courier New", 10), relief="flat", state="disabled", padx=6, pady=4)
            rt.pack(fill=tk.X, padx=12, pady=(0, 10))
            setattr(self, ra, rt)

    def _dijk_run(self):
        src = self.e_src.get().strip()
        tgt = self.e_tgt.get().strip()
        if not self.graph:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng tạo đồ thị trước.")
            return
        if not self._chk(src) or not self._chk(tgt): return
        
        try:
            from src.graph_algorithms.algorithms.shortest_path.dijkstra import dijkstra, get_path
            dist, prev = dijkstra(self.graph, src, tgt)
            path = get_path(prev, src, tgt)
            self._show_sp(self.rdi, src, tgt, dist.get(tgt, float('inf')), path, "Dijkstra")
            self._last_dijk = {"dist": dist.get(tgt, float('inf')), "path": path}
            if path: self.draw(hi_n=set(path), hi_e=set(zip(path, path[1:])), title=f"Dijkstra: {src} → {tgt}")
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))
            self._settext(self.rdi, f"LỖI: {str(e)}")

    def _bf_run(self):
        src = self.e_src.get().strip()
        tgt = self.e_tgt.get().strip()
        if not self.graph:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng tạo đồ thị trước.")
            return
        if not self._chk(src) or not self._chk(tgt): return
        
        try:
            from src.graph_algorithms.algorithms.shortest_path.bellman_ford import bellman_ford
            from src.graph_algorithms.algorithms.shortest_path.dijkstra import get_path
            dist, prev = bellman_ford(self.graph, src)
            path = get_path(prev, src, tgt)
            self._show_sp(self.rbf, src, tgt, dist.get(tgt, float('inf')), path, "Bellman-Ford")
            self._last_bf = {"dist": dist.get(tgt, float('inf')), "path": path}
            if path: self.draw(hi_n=set(path), hi_e=set(zip(path, path[1:])), title=f"Bellman-Ford: {src} → {tgt}")
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))
            self._settext(self.rbf, f"LỖI: {str(e)}")

    def _show_sp(self, widget, src, tgt, dist, path, algo):
        if dist == float('inf'):
            self._settext(widget, f"Không có đường đi từ {src} đến {tgt}.")
        else:
            p_str = " → ".join(path)
            # Tránh in .0 nếu là số nguyên
            dist_str = int(dist) if dist == int(dist) else dist
            self._settext(widget, f"Đường đi: {p_str}\nTổng chi phí: {dist_str}")
