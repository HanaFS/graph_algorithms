# ui/tab_repr.py
"""
Tab2Mixin – Tab "2. Biểu diễn": hiển thị ma trận kề, danh sách kề, danh sách cạnh.

Bao gồm:
  _tab2()      : xây dựng layout 3 cột
  _show_repr() : tính và điền nội dung các bảng biểu diễn
"""
import tkinter as tk
from tkinter import ttk
from .theme import BG, PANEL, ACCENT, ACCENT2, TEXT, TEXT2, SUCCESS


class Tab2Mixin:
    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 2 – REPRESENTATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    def _tab2(self, p):
        tb = self._tab_toolbar(p, "Biểu diễn đồ thị")
        self._btn(tb, "Cập nhật biểu diễn", self._show_repr, ACCENT2).pack(
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
                        font=("Courier New", 10), relief="flat",
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
            hdr = " "*(W+1) + "".join(f"{n:>{W}}" for n in nodes)
            sep = " "*(W+1) + "─"*(W*sz)
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
