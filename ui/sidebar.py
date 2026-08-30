# ui/sidebar.py
"""
SidebarMixin – xây dựng layout chính, ttk styles, và sidebar trái.

Bao gồm:
  _build_styles()  : cấu hình ttk Style
  _build_ui()      : khung tiêu đề + layout chính
  _build_sidebar() : panel trái (loại đồ thị, thêm đỉnh/cạnh, thông tin đồ thị)
  _build_notebook(): tab notebook bên phải
"""
import tkinter as tk
from tkinter import ttk
from .theme import (
    BG, PANEL, ACCENT, ACCENT2, ERROR, SUCCESS, TEXT, TEXT2
)


class SidebarMixin:
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
        self.e_node.bind("<Return>",    lambda _: self._add_node())
        self.e_node.bind("<KeyRelease>", self._check_add_node_input)
        self.e_node.bind("<FocusIn>",   self._check_add_node_input)
        self.e_node.bind("<FocusOut>",  self._check_add_node_input)

        self.btn_add_node = self._btn(self.sec_node, "Thêm đỉnh", self._add_node,
                                      color="#e2e8f0", fg="#64748b")
        self.btn_add_node.pack(fill=tk.X)

        # ── add edge ───────────────────────────────────────────────────────
        self.sec_edge = self._section(p, "Thêm cạnh (Edge)")
        for lbl, attr in [("Từ:", "ef"), ("Đến:", "et"), ("Trọng số:", "ew")]:
            tk.Label(self.sec_edge, text=lbl, bg=PANEL, fg=TEXT2,
                     font=("Segoe UI", 9)).pack(anchor="w")
            e = self._entry(self.sec_edge)
            e.pack(fill=tk.X, pady=(3, 6))
            setattr(self, attr, e)
        self.ew.insert(0, "1")
        self.ef.bind("<KeyRelease>", self._check_add_edge_input)
        self.ef.bind("<FocusIn>",    self._check_add_edge_input)
        self.ef.bind("<FocusOut>",   self._check_add_edge_input)
        self.ef.bind("<Return>",     lambda _: self.et.focus_set())
        self.et.bind("<KeyRelease>", self._check_add_edge_input)
        self.et.bind("<FocusIn>",    self._check_add_edge_input)
        self.et.bind("<FocusOut>",   self._check_add_edge_input)
        self.et.bind("<Return>",     lambda _: self.ew.focus_set())
        self.ew.bind("<KeyRelease>", self._check_add_edge_input)
        self.ew.bind("<FocusIn>",    self._check_add_edge_input)
        self.ew.bind("<FocusOut>",   self._check_add_edge_input)
        self.ew.bind("<Return>",     lambda _: self._add_edge())

        self.btn_add_edge = self._btn(self.sec_edge, "Thêm cạnh", self._add_edge,
                                      color="#e2e8f0", fg="#64748b")
        self.btn_add_edge.pack(fill=tk.X)

        # ── action buttons ─────────────────────────────────────────────────
        bf = tk.Frame(p, bg=BG)
        bf.pack(side=tk.BOTTOM, fill=tk.X, pady=(4, 0))

        self._btn(bf, "Xóa sạch toàn bộ đồ thị", self._clear, ERROR).pack(fill=tk.X)

        # ── graph info ─────────────────────────────────────────────────────
        inf = self._section(p, "Đồ thị hiện tại", expand=True)
        self.info_t = tk.Text(inf, state="disabled",
                              bg="#f8fafc", fg=TEXT, relief="flat",
                              font=("Courier New", 8), wrap="word",
                              borderwidth=1, height=2)
        self.info_t.pack(fill=tk.BOTH, expand=True)


