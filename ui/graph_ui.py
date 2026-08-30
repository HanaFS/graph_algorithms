# ui/graph_ui.py
"""
Main Application UI Entry Point

This file defines the main GraphApp class, which inherits all functionalities
from specialized Mixins to keep the architecture modular and maintainable.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx

from .theme import BG, ACCENT, ACCENT2, SUCCESS, ERROR, WARNING, TEXT, PANEL
from .sidebar import SidebarMixin
from .tab_graph import Tab1Mixin
from .tab_repr import Tab2Mixin
from .tab_traversal import Tab3Mixin
from .tab_bipartite import Tab4Mixin
from .tab_shortest import Tab5Mixin
from .tab_advanced import Tab6Mixin


class GraphApp(
    SidebarMixin,
    Tab1Mixin,
    Tab2Mixin,
    Tab3Mixin,
    Tab4Mixin,
    Tab5Mixin,
    Tab6Mixin,
):
    """
    Main Application Class for Graph Algorithms.
    Inherits all specific UI tabs and logic from Mixin classes.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Algorithms & Visualization")
        self.root.geometry("1050x700")
        self.root.configure(bg=BG)

        # Trạng thái đồ thị toàn cục
        self.graph = {}            # {u: [(v, weight), ...]}
        self.history = []          # undo stack
        self._pos = {}             # toạ độ đỉnh cho networkx
        self.directed = tk.BooleanVar(value=False)

        # Cấu hình Style chung cho Notebook
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("TNotebook", background=BG, borderwidth=0)
        s.configure("TNotebook.Tab",
                    background="#e2e8f0", foreground="#475569",
                    padding=[16, 8], font=("Segoe UI", 10, "bold"),
                    borderwidth=0)
        s.map("TNotebook.Tab",
              background=[("selected", ACCENT)],
              foreground=[("selected", "white")])

        # Main Layout
        self.main_container = tk.Frame(self.root, bg=BG)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Sidebar Frame
        self.sidebar_frame = tk.Frame(self.main_container, bg=BG, width=320)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        self.sidebar_frame.pack_propagate(False)

        # Build Sidebar (từ SidebarMixin)
        self._build_sidebar(self.sidebar_frame)

        # Right Tabs Frame
        self.tabs_frame = tk.Frame(self.main_container, bg=BG)
        self.tabs_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Build Tabs (từ các Tab Mixins)
        self.nb = ttk.Notebook(self.tabs_frame)
        self.nb.pack(fill=tk.BOTH, expand=True)

        tabs_info = [
            ("1. Đồ thị", self._tab1),
            ("2. Biểu diễn", self._tab2),
            ("3. Duyệt (BFS/DFS)", self._tab3),
            ("4. Hai phía", self._tab4),
            ("5. Đường đi ngắn nhất", self._tab5),
            ("6. Thuật toán nâng cao", self._tab6),
        ]

        for title, builder in tabs_info:
            f = tk.Frame(self.nb, bg=BG)
            self.nb.add(f, text=title)
            builder(f)

        # Init state
        self._refresh()

    # ═══════════════════════════════════════════════════════════════════════════
    # GRAPH MANAGEMENT (Core state updates)
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
        
        self.ef.focus_set()
        def _restore_ew():
            if not self.ew.get():
                self.ew.insert(0, "1")
            self._check_add_edge_input()
        self.root.after(50, _restore_ew)
        
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
        if hasattr(self, 'btn_save_graph'):
            if has_nodes:
                self.btn_save_graph.config(bg=ACCENT, fg="white", text="Lưu đồ thị", highlightbackground="#86efac", highlightthickness=2)
            else:
                self.btn_save_graph.config(bg="#e2e8f0", fg="#94a3b8", text="Lưu đồ thị", highlightbackground="#ffffff", highlightthickness=2)

    def _upd_info(self):
        if not hasattr(self, 'info_t'): return
        nodes = sorted(self.graph)
        
        for attr in ['e_ts', 'e_src', 'e_tgt', 'e_fleury_start', 'e_hier_start', 'e_prim_root', 'e_ff_src', 'e_ff_snk']:
            if hasattr(self, attr):
                cb = getattr(self, attr)
                if isinstance(cb, ttk.Combobox):
                    cb['values'] = nodes
                    if cb.get() not in nodes:
                        cb.set('')
        
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
        """Bảo vệ crash khi bg không phải mã hex (VD: tên màu hệ thống)."""
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
