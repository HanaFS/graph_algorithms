import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import math
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from graph import Graph
from traversal import bfs, dfs
from bipartite import is_bipartite, get_partitions


# ============================================================
# VẼ ĐỒ THỊ
# ============================================================

def draw_graph(ax, graph):

    ax.clear()

    ax.set_facecolor("#111827")

    if graph.n == 0:

        ax.text(
            0.5,
            0.5,
            "ĐỒ THỊ TRỐNG",
            transform=ax.transAxes,
            ha="center",
            va="center",
            color="white",
            fontsize=20
        )

        ax.axis("off")
        return

    # --------------------------------------------------------
    # VỊ TRÍ ĐỈNH
    # --------------------------------------------------------

    positions = {}

    radius = 3

    for i in range(graph.n):

        angle = 2 * math.pi * i / graph.n

        x = radius * math.cos(angle)
        y = radius * math.sin(angle)

        positions[i] = (x, y)

    # --------------------------------------------------------
    # VẼ CẠNH
    # --------------------------------------------------------

    drawn_edges = set()

    for u, v, w in graph.edges:

        if graph.directed:

            edge_key = (u, v)

        else:

            edge_key = tuple(sorted((u, v)))

        if edge_key in drawn_edges:
            continue

        drawn_edges.add(edge_key)

        x1, y1 = positions[u]
        x2, y2 = positions[v]

        # ----------------------------------------------------
        # ĐỒ THỊ CÓ HƯỚNG
        # ----------------------------------------------------

        if graph.directed:

            ax.annotate(
                "",
                xy=(x2, y2),
                xytext=(x1, y1),
                arrowprops=dict(
                    arrowstyle="->",
                    linewidth=2,
                    color="#00e5ff",
                    shrinkA=25,
                    shrinkB=25
                )
            )

        # ----------------------------------------------------
        # ĐỒ THỊ VÔ HƯỚNG
        # ----------------------------------------------------

        else:

            ax.plot(
                [x1, x2],
                [y1, y2],
                linewidth=2,
                color="#00e5ff"
            )

        # ----------------------------------------------------
        # HIỂN THỊ TRỌNG SỐ
        # ----------------------------------------------------

        if w != 1:

            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2

            ax.text(
                mid_x,
                mid_y,
                str(w),
                color="white",
                fontsize=11,
                ha="center",
                va="center",
                bbox=dict(
                    facecolor="#111827",
                    edgecolor="white"
                )
            )

    # --------------------------------------------------------
    # VẼ ĐỈNH
    # --------------------------------------------------------

    for i in range(graph.n):

        x, y = positions[i]

        ax.scatter(
            x,
            y,
            s=1000,
            color="#a855f7",
            edgecolors="white",
            linewidths=2,
            zorder=3
        )

        ax.text(
            x,
            y,
            str(i + 1),
            color="white",
            fontsize=14,
            fontweight="bold",
            ha="center",
            va="center",
            zorder=4
        )

    # --------------------------------------------------------
    # TIÊU ĐỀ
    # --------------------------------------------------------

    if graph.directed:
        title = "ĐỒ THỊ CÓ HƯỚNG"
    else:
        title = "ĐỒ THỊ VÔ HƯỚNG"

    ax.set_title(
        title,
        color="white",
        fontsize=18,
        fontweight="bold"
    )

    ax.axis("off")

    ax.set_aspect("equal")


# ============================================================
# GRAPH APP
# ============================================================

class GraphApp:

    def __init__(self, root, graph):

        self.root = root
        self.graph = graph

        self.root.title("GRAPH ALGORITHMS")

        self.root.geometry("1400x850")

        self.root.configure(
            bg="#111827"
        )

        self.create_style()

        self.create_interface()

        self.update_all()

    # ========================================================
    # STYLE
    # ========================================================

    def create_style(self):

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except:
            pass

        style.configure(
            "TNotebook",
            background="#111827",
            borderwidth=0
        )

        style.configure(
            "TNotebook.Tab",
            background="#1f2937",
            foreground="#9ca3af",
            padding=(20, 10),
            font=("Arial", 11, "bold")
        )

        style.map(
            "TNotebook.Tab",
            background=[
                ("selected", "#374151")
            ],
            foreground=[
                ("selected", "white")
            ]
        )

    # ========================================================
    # TẠO GIAO DIỆN
    # ========================================================

    def create_interface(self):

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header = tk.Frame(
            self.root,
            bg="#111827"
        )

        header.pack(
            fill="x",
            padx=25,
            pady=15
        )

        tk.Label(
            header,
            text="GRAPH ALGORITHMS",
            bg="#111827",
            fg="white",
            font=("Arial", 24, "bold")
        ).pack(
            side="left"
        )

        self.type_label = tk.Label(
            header,
            bg="#111827",
            fg="#00e5ff",
            font=("Arial", 11, "bold")
        )

        self.type_label.pack(
            side="right"
        )

        # ----------------------------------------------------
        # NOTEBOOK
        # ----------------------------------------------------

        self.notebook = ttk.Notebook(
            self.root
        )

        self.notebook.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        self.tab_graph = tk.Frame(
            self.notebook,
            bg="#111827"
        )

        self.tab_representation = tk.Frame(
            self.notebook,
            bg="#111827"
        )

        self.tab_traversal = tk.Frame(
            self.notebook,
            bg="#111827"
        )

        self.tab_bipartite = tk.Frame(
            self.notebook,
            bg="#111827"
        )

        self.tab_algorithm = tk.Frame(
            self.notebook,
            bg="#111827"
        )

        self.notebook.add(
            self.tab_graph,
            text="1. Đồ thị"
        )

        self.notebook.add(
            self.tab_representation,
            text="2. Biểu diễn"
        )

        self.notebook.add(
            self.tab_traversal,
            text="3. Traversal"
        )

        self.notebook.add(
            self.tab_bipartite,
            text="4. Bipartite"
        )

        self.notebook.add(
            self.tab_algorithm,
            text="5. Thuật toán"
        )

        self.create_graph_tab()

        self.create_representation_tab()

        self.create_traversal_tab()

        self.create_bipartite_tab()

        self.create_algorithm_tab()

    # ========================================================
    # TAB 1 - ĐỒ THỊ
    # ========================================================

    def create_graph_tab(self):

        main = tk.Frame(
            self.tab_graph,
            bg="#111827"
        )

        main.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # PANEL TRÁI
        # ----------------------------------------------------

        left = tk.Frame(
            main,
            bg="#1f2937",
            width=350
        )

        left.pack(
            side="left",
            fill="y",
            padx=(0, 10)
        )

        left.pack_propagate(False)

        tk.Label(
            left,
            text="QUẢN LÝ ĐỒ THỊ",
            bg="#1f2937",
            fg="white",
            font=("Arial", 17, "bold")
        ).pack(
            pady=20
        )

        self.vertex_info = tk.Label(
            left,
            text="",
            bg="#1f2937",
            fg="#9ca3af"
        )

        self.vertex_info.pack(
            anchor="w",
            padx=20
        )

        # ----------------------------------------------------
        # SỐ ĐỈNH
        # ----------------------------------------------------

        tk.Label(
            left,
            text="Số đỉnh",
            bg="#1f2937",
            fg="#9ca3af"
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 3)
        )

        self.vertex_entry = tk.Entry(
            left,
            bg="#111827",
            fg="white",
            insertbackground="white",
            relief="flat"
        )

        self.vertex_entry.pack(
            fill="x",
            padx=20,
            ipady=8
        )

        self.vertex_entry.bind(
            "<KeyRelease>",
            lambda e: self.update_buttons()
        )

        self.add_vertex_btn = tk.Button(
            left,
            text="+ Thêm đỉnh",
            command=self.add_vertex,
            relief="flat",
            bd=0,
            font=("Arial", 10, "bold"),
            cursor="hand2"
        )

        self.add_vertex_btn.pack(
            fill="x",
            padx=20,
            pady=7,
            ipady=7
        )

        # ----------------------------------------------------
        # THÊM CẠNH
        # ----------------------------------------------------

        tk.Label(
            left,
            text="Thêm cạnh",
            bg="#1f2937",
            fg="#9ca3af"
        ).pack(
            anchor="w",
            padx=20,
            pady=(10, 3)
        )

        edge_frame = tk.Frame(
            left,
            bg="#1f2937"
        )

        edge_frame.pack(
            fill="x",
            padx=20
        )

        self.from_entry = tk.Entry(
            edge_frame,
            bg="#111827",
            fg="white",
            insertbackground="white",
            relief="flat"
        )

        self.from_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=7
        )

        tk.Label(
            edge_frame,
            text=" → ",
            bg="#1f2937",
            fg="#00e5ff"
        ).pack(
            side="left"
        )

        self.to_entry = tk.Entry(
            edge_frame,
            bg="#111827",
            fg="white",
            insertbackground="white",
            relief="flat"
        )

        self.to_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=7
        )

        self.from_entry.bind(
            "<KeyRelease>",
            lambda e: self.update_buttons()
        )

        self.to_entry.bind(
            "<KeyRelease>",
            lambda e: self.update_buttons()
        )

        self.weight_entry = tk.Entry(
            left,
            bg="#111827",
            fg="white",
            insertbackground="white",
            relief="flat"
        )

        self.weight_entry.insert(
            0,
            "1"
        )

        self.weight_entry.pack(
            fill="x",
            padx=20,
            pady=5,
            ipady=7
        )

        self.add_edge_btn = tk.Button(
            left,
            text="+ Thêm cạnh",
            command=self.add_edge,
            relief="flat",
            bd=0,
            font=("Arial", 10, "bold"),
            cursor="hand2"
        )

        self.add_edge_btn.pack(
            fill="x",
            padx=20,
            pady=7,
            ipady=7
        )

        # ----------------------------------------------------
        # LOẠI ĐỒ THỊ
        # ----------------------------------------------------

        tk.Label(
            left,
            text="Loại đồ thị",
            bg="#1f2937",
            fg="#9ca3af"
        ).pack(
            anchor="w",
            padx=20,
            pady=(10, 3)
        )

        self.direction_var = tk.StringVar(
            value=(
                "directed"
                if self.graph.directed
                else "undirected"
            )
        )

        direction = tk.Frame(
            left,
            bg="#1f2937"
        )

        direction.pack(
            fill="x",
            padx=20
        )

        tk.Radiobutton(
            direction,
            text="Vô hướng",
            variable=self.direction_var,
            value="undirected",
            command=self.change_direction,
            bg="#1f2937",
            fg="white",
            selectcolor="#374151"
        ).pack(
            side="left"
        )

        tk.Radiobutton(
            direction,
            text="Có hướng",
            variable=self.direction_var,
            value="directed",
            command=self.change_direction,
            bg="#1f2937",
            fg="white",
            selectcolor="#374151"
        ).pack(
            side="left"
        )

        # ----------------------------------------------------
        # VẼ / LƯU
        # ----------------------------------------------------

        button_frame = tk.Frame(
            left,
            bg="#1f2937"
        )

        button_frame.pack(
            fill="x",
            padx=20,
            pady=15
        )

        self.redraw_btn = tk.Button(
            button_frame,
            text="↺ Vẽ lại",
            command=self.redraw,
            relief="flat",
            bd=0,
            font=("Arial", 10, "bold")
        )

        self.redraw_btn.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 5),
            ipady=7
        )

        self.save_btn = tk.Button(
            button_frame,
            text="Lưu hình",
            command=self.save_image,
            relief="flat",
            bd=0,
            font=("Arial", 10, "bold")
        )

        self.save_btn.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(5, 0),
            ipady=7
        )

        # ----------------------------------------------------
        # XÓA
        # ----------------------------------------------------

        tk.Label(
            left,
            text="XÓA ĐỈNH & CẠNH",
            bg="#1f2937",
            fg="#ff1744",
            font=("Arial", 11, "bold")
        ).pack(
            anchor="w",
            padx=20
        )

        self.delete_vertex_entry = tk.Entry(
            left,
            bg="#111827",
            fg="white",
            insertbackground="white",
            relief="flat"
        )

        self.delete_vertex_entry.pack(
            fill="x",
            padx=20,
            pady=5,
            ipady=7
        )

        self.delete_vertex_entry.bind(
            "<KeyRelease>",
            lambda e: self.update_buttons()
        )

        self.delete_vertex_btn = tk.Button(
            left,
            text="Xóa đỉnh",
            command=self.delete_vertex,
            relief="flat",
            bd=0,
            font=("Arial", 10, "bold")
        )

        self.delete_vertex_btn.pack(
            fill="x",
            padx=20,
            pady=4,
            ipady=7
        )

        delete_edge = tk.Frame(
            left,
            bg="#1f2937"
        )

        delete_edge.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.delete_from_entry = tk.Entry(
            delete_edge,
            bg="#111827",
            fg="white",
            insertbackground="white",
            relief="flat"
        )

        self.delete_from_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=7
        )

        tk.Label(
            delete_edge,
            text=" → ",
            bg="#1f2937",
            fg="#ff1744"
        ).pack(
            side="left"
        )

        self.delete_to_entry = tk.Entry(
            delete_edge,
            bg="#111827",
            fg="white",
            insertbackground="white",
            relief="flat"
        )

        self.delete_to_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=7
        )

        self.delete_from_entry.bind(
            "<KeyRelease>",
            lambda e: self.update_buttons()
        )

        self.delete_to_entry.bind(
            "<KeyRelease>",
            lambda e: self.update_buttons()
        )

        self.delete_edge_btn = tk.Button(
            left,
            text="Xóa cạnh",
            command=self.delete_edge,
            relief="flat",
            bd=0,
            font=("Arial", 10, "bold")
        )

        self.delete_edge_btn.pack(
            fill="x",
            padx=20,
            pady=4,
            ipady=7
        )

        tk.Button(
            left,
            text="Xóa sạch toàn bộ đồ thị",
            command=self.clear_graph,
            bg="#374151",
            fg="white",
            relief="flat",
            bd=0,
            font=("Arial", 10, "bold")
        ).pack(
            fill="x",
            padx=20,
            pady=10,
            ipady=7
        )

        # ----------------------------------------------------
        # KHUNG VẼ
        # ----------------------------------------------------

        right = tk.Frame(
            main,
            bg="#1f2937"
        )

        right.pack(
            side="right",
            fill="both",
            expand=True
        )

        self.figure = plt.Figure(
            figsize=(8, 6),
            dpi=100,
            facecolor="#111827"
        )

        self.ax = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=right
        )

        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    # ========================================================
    # THÊM ĐỈNH
    # ========================================================

    def add_vertex(self):

        try:
            new_n = int(
                self.vertex_entry.get()
            )

        except ValueError:

            messagebox.showwarning(
                "Lỗi",
                "Vui lòng nhập số nguyên."
            )

            return

        if new_n <= self.graph.n:

            messagebox.showwarning(
                "Lỗi",
                f"Số đỉnh phải lớn hơn {self.graph.n}."
            )

            return

        while self.graph.n < new_n:

            self.graph.add_vertex()

        self.vertex_entry.delete(
            0,
            tk.END
        )

        self.update_all()

    # ========================================================
    # THÊM CẠNH
    # ========================================================

    def add_edge(self):

        try:

            u = int(
                self.from_entry.get()
            )

            v = int(
                self.to_entry.get()
            )

            w = float(
                self.weight_entry.get()
            )

        except ValueError:

            messagebox.showwarning(
                "Lỗi",
                "Đỉnh và trọng số phải là số."
            )

            return

        if w == 0:

            messagebox.showwarning(
                "Lỗi",
                "Trọng số không được bằng 0."
            )

            return

        # Nếu là số nguyên thì hiển thị đẹp hơn
        if w.is_integer():
            w = int(w)

        success = self.graph.add_edge(
            u,
            v,
            w
        )

        if success:

            self.from_entry.delete(
                0,
                tk.END
            )

            self.to_entry.delete(
                0,
                tk.END
            )

            self.update_all()

        else:

            messagebox.showwarning(
                "Lỗi",
                "Không thể thêm cạnh.\n"
                "Kiểm tra đỉnh, trọng số hoặc cạnh trùng."
            )

    # ========================================================
    # XÓA CẠNH
    # ========================================================

    def delete_edge(self):

        try:

            u = int(
                self.delete_from_entry.get()
            )

            v = int(
                self.delete_to_entry.get()
            )

        except ValueError:

            messagebox.showwarning(
                "Lỗi",
                "Vui lòng nhập số đỉnh."
            )

            return

        success = self.graph.delete_edge(
            u,
            v
        )

        if not success:

            messagebox.showwarning(
                "Lỗi",
                "Không tìm thấy cạnh."
            )

            return

        self.delete_from_entry.delete(
            0,
            tk.END
        )

        self.delete_to_entry.delete(
            0,
            tk.END
        )

        self.update_all()

    # ========================================================
    # XÓA ĐỈNH
    # ========================================================

    def delete_vertex(self):

        try:

            vertex = int(
                self.delete_vertex_entry.get()
            )

        except ValueError:

            messagebox.showwarning(
                "Lỗi",
                "Vui lòng nhập số đỉnh."
            )

            return

        if vertex < 1 or vertex > self.graph.n:

            messagebox.showwarning(
                "Lỗi",
                "Đỉnh không tồn tại."
            )

            return

        success = self.graph.delete_vertex(
            vertex - 1
        )

        if not success:

            messagebox.showwarning(
                "Lỗi",
                "Không thể xóa đỉnh."
            )

            return

        self.delete_vertex_entry.delete(
            0,
            tk.END
        )

        self.update_all()

    # ========================================================
    # XÓA TOÀN BỘ
    # ========================================================

    def clear_graph(self):

        answer = messagebox.askyesno(
            "Xác nhận",
            "Bạn có chắc chắn muốn xóa sạch toàn bộ đồ thị?"
        )

        if not answer:
            return

        self.graph.clear()

        self.update_all()

    # ========================================================
    # ĐỔI LOẠI ĐỒ THỊ
    # ========================================================

    def change_direction(self):

        directed = (
            self.direction_var.get()
            == "directed"
        )

        self.graph.change_direction(
            directed
        )

        self.update_all()

    # ========================================================
    # VẼ LẠI
    # ========================================================

    def redraw(self):

        self.update_graph()

    # ========================================================
    # UPDATE GRAPH
    # ========================================================

    def update_graph(self):

        draw_graph(
            self.ax,
            self.graph
        )

        if self.graph.directed:

            self.type_label.config(
                text="● ĐỒ THỊ CÓ HƯỚNG"
            )

        else:

            self.type_label.config(
                text="● ĐỒ THỊ VÔ HƯỚNG"
            )

        self.canvas.draw()

    # ========================================================
    # LƯU HÌNH
    # ========================================================

    def save_image(self):

        if self.graph.n == 0:

            messagebox.showwarning(
                "Lỗi",
                "Đồ thị đang trống."
            )

            return

        filename = filedialog.asksaveasfilename(
            title="Lưu hình đồ thị",
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPG", "*.jpg"),
                ("PDF", "*.pdf")
            ]
        )

        if not filename:
            return

        self.figure.savefig(
            filename,
            dpi=300,
            bbox_inches="tight",
            facecolor="#111827"
        )

        messagebox.showinfo(
            "Thành công",
            "Đã lưu hình đồ thị."
        )

    # ========================================================
    # UPDATE BUTTON
    # ========================================================

    def update_buttons(self):

        # ----------------------------------------------------
        # THÊM ĐỈNH
        # ----------------------------------------------------

        if self.vertex_entry.get().strip():

            self.add_vertex_btn.config(
                text="Thêm đỉnh",
                bg="#c026ff",
                fg="white"
            )

        else:

            self.add_vertex_btn.config(
                text="+ Thêm đỉnh",
                bg="#374151",
                fg="#9ca3af"
            )

        # ----------------------------------------------------
        # THÊM CẠNH
        # ----------------------------------------------------

        if (
            self.from_entry.get().strip()
            and
            self.to_entry.get().strip()
        ):

            self.add_edge_btn.config(
                text="Thêm cạnh",
                bg="#00bcd4",
                fg="white"
            )

        else:

            self.add_edge_btn.config(
                text="+ Thêm cạnh",
                bg="#374151",
                fg="#9ca3af"
            )

        # ----------------------------------------------------
        # XÓA ĐỈNH
        # ----------------------------------------------------

        if self.delete_vertex_entry.get().strip():

            self.delete_vertex_btn.config(
                text="Xóa đỉnh",
                bg="#ff1744",
                fg="white"
            )

        else:

            self.delete_vertex_btn.config(
                text="Xóa đỉnh",
                bg="#374151",
                fg="#9ca3af"
            )

        # ----------------------------------------------------
        # XÓA CẠNH
        # ----------------------------------------------------

        if (
            self.delete_from_entry.get().strip()
            and
            self.delete_to_entry.get().strip()
        ):

            self.delete_edge_btn.config(
                text="Xóa cạnh",
                bg="#ff1744",
                fg="white"
            )

        else:

            self.delete_edge_btn.config(
                text="Xóa cạnh",
                bg="#374151",
                fg="#9ca3af"
            )

    # ========================================================
    # UPDATE ALL
    # ========================================================

    def update_all(self):

        self.update_graph()

        self.update_buttons()

        self.vertex_info.config(
            text=(
                f"Số đỉnh: {self.graph.n}    "
                f"Số cạnh: {len(self.graph.edges)}"
            )
        )

        self.update_representation()

        self.update_algorithm()

    # ========================================================
    # TAB 2 - BIỂU DIỄN
    # ========================================================

    def create_representation_tab(self):

        tk.Label(
            self.tab_representation,
            text="BIỂU DIỄN ĐỒ THỊ",
            bg="#111827",
            fg="#00e5ff",
            font=("Arial", 22, "bold")
        ).pack(
            pady=20
        )

        self.representation_text = tk.Text(
            self.tab_representation,
            bg="#1f2937",
            fg="white",
            font=("Consolas", 11),
            relief="flat"
        )

        self.representation_text.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=20
        )

    # ========================================================
    # UPDATE BIỂU DIỄN
    # ========================================================

    def update_representation(self):

        self.representation_text.config(
            state="normal"
        )

        self.representation_text.delete(
            "1.0",
            tk.END
        )

        # ----------------------------------------------------
        # EDGE LIST
        # ----------------------------------------------------

        self.representation_text.insert(
            tk.END,
            "========== DANH SÁCH CẠNH ==========\n\n"
        )

        if not self.graph.edges:

            self.representation_text.insert(
                tk.END,
                "Chưa có cạnh.\n"
            )

        else:

            for u, v, w in self.graph.edges:

                if self.graph.directed:
                    symbol = "→"
                else:
                    symbol = "--"

                self.representation_text.insert(
                    tk.END,
                    f"{u + 1} {symbol} {v + 1}"
                )

                if w != 1:

                    self.representation_text.insert(
                        tk.END,
                        f" ({w})"
                    )

                self.representation_text.insert(
                    tk.END,
                    "\n"
                )

        # ----------------------------------------------------
        # MA TRẬN KỀ
        # ----------------------------------------------------

        self.representation_text.insert(
            tk.END,
            "\n========== MA TRẬN KỀ ==========\n\n"
        )

        if self.graph.n == 0:

            self.representation_text.insert(
                tk.END,
                "Đồ thị trống.\n"
            )

        else:

            self.representation_text.insert(
                tk.END,
                "     "
            )

            for i in range(self.graph.n):

                self.representation_text.insert(
                    tk.END,
                    f"{i + 1:5}"
                )

            self.representation_text.insert(
                tk.END,
                "\n"
            )

            for i in range(self.graph.n):

                self.representation_text.insert(
                    tk.END,
                    f"{i + 1:3} "
                )

                for j in range(self.graph.n):

                    self.representation_text.insert(
                        tk.END,
                        f"{self.graph.adj_matrix[i][j]:5}"
                    )

                self.representation_text.insert(
                    tk.END,
                    "\n"
                )

        # ----------------------------------------------------
        # DANH SÁCH KỀ
        # ----------------------------------------------------

        self.representation_text.insert(
            tk.END,
            "\n========== DANH SÁCH KỀ ==========\n\n"
        )

        for i in range(self.graph.n):

            self.representation_text.insert(
                tk.END,
                f"{i + 1}: "
            )

            if not self.graph.adj_list[i]:

                self.representation_text.insert(
                    tk.END,
                    "Không có cạnh\n"
                )

                continue

            for index, (v, w) in enumerate(
                self.graph.adj_list[i]
            ):

                self.representation_text.insert(
                    tk.END,
                    str(v + 1)
                )

                if w != 1:

                    self.representation_text.insert(
                        tk.END,
                        f"({w})"
                    )

                if index < len(
                    self.graph.adj_list[i]
                ) - 1:

                    if self.graph.directed:

                        self.representation_text.insert(
                            tk.END,
                            " → "
                        )

                    else:

                        self.representation_text.insert(
                            tk.END,
                            " -- "
                        )

            self.representation_text.insert(
                tk.END,
                "\n"
            )

        self.representation_text.config(
            state="disabled"
        )

    # ========================================================
    # TAB 3 - TRAVERSAL
    # ========================================================

    def create_traversal_tab(self):

        tk.Label(
            self.tab_traversal,
            text="BFS / DFS",
            bg="#111827",
            fg="#00e5ff",
            font=("Arial", 22, "bold")
        ).pack(
            pady=30
        )

        frame = tk.Frame(
            self.tab_traversal,
            bg="#1f2937"
        )

        frame.pack(
            pady=20
        )

        tk.Label(
            frame,
            text="Đỉnh bắt đầu:",
            bg="#1f2937",
            fg="white"
        ).pack(
            side="left",
            padx=10
        )

        self.start_entry = tk.Entry(
            frame,
            bg="#111827",
            fg="white",
            insertbackground="white"
        )

        self.start_entry.pack(
            side="left",
            padx=10,
            ipady=7
        )

        tk.Button(
            frame,
            text="BFS",
            command=self.run_bfs,
            bg="#00bcd4",
            fg="white",
            relief="flat",
            font=("Arial", 10, "bold"),
            padx=20
        ).pack(
            side="left",
            padx=10,
            ipady=5
        )

        tk.Button(
            frame,
            text="DFS",
            command=self.run_dfs,
            bg="#c026ff",
            fg="white",
            relief="flat",
            font=("Arial", 10, "bold"),
            padx=20
        ).pack(
            side="left",
            padx=10,
            ipady=5
        )

        self.traversal_result = tk.Label(
            self.tab_traversal,
            text="Nhập đỉnh bắt đầu rồi chọn BFS hoặc DFS.",
            bg="#111827",
            fg="white",
            font=("Consolas", 14)
        )

        self.traversal_result.pack(
            pady=50
        )

    # ========================================================
    # BFS
    # ========================================================

    def run_bfs(self):

        try:

            start = int(
                self.start_entry.get()
            )

        except ValueError:

            messagebox.showwarning(
                "Lỗi",
                "Vui lòng nhập số đỉnh."
            )

            return

        result = bfs(
            self.graph,
            start
        )

        if not result:

            messagebox.showwarning(
                "Lỗi",
                "Đỉnh bắt đầu không hợp lệ."
            )

            return

        self.traversal_result.config(
            text=(
                "BFS: "
                +
                " → ".join(
                    map(str, result)
                )
            ),
            fg="#00e5ff"
        )

    # ========================================================
    # DFS
    # ========================================================

    def run_dfs(self):

        try:

            start = int(
                self.start_entry.get()
            )

        except ValueError:

            messagebox.showwarning(
                "Lỗi",
                "Vui lòng nhập số đỉnh."
            )

            return

        result = dfs(
            self.graph,
            start
        )

        if not result:

            messagebox.showwarning(
                "Lỗi",
                "Đỉnh bắt đầu không hợp lệ."
            )

            return

        self.traversal_result.config(
            text=(
                "DFS: "
                +
                " → ".join(
                    map(str, result)
                )
            ),
            fg="#c026ff"
        )

    # ========================================================
    # TAB 4 - BIPARTITE
    # ========================================================

    def create_bipartite_tab(self):

        tk.Label(
            self.tab_bipartite,
            text="KIỂM TRA BIPARTITE",
            bg="#111827",
            fg="#00e5ff",
            font=("Arial", 22, "bold")
        ).pack(
            pady=40
        )

        tk.Button(
            self.tab_bipartite,
            text="Kiểm tra đồ thị",
            command=self.check_bipartite,
            bg="#c026ff",
            fg="white",
            relief="flat",
            font=("Arial", 11, "bold"),
            padx=30,
            pady=10
        ).pack()

        self.bipartite_result = tk.Label(
            self.tab_bipartite,
            text="",
            bg="#111827",
            fg="white",
            font=("Arial", 14)
        )

        self.bipartite_result.pack(
            pady=40
        )

    # ========================================================
    # KIỂM TRA BIPARTITE
    # ========================================================

    def check_bipartite(self):

        if self.graph.n == 0:

            self.bipartite_result.config(
                text="Đồ thị đang trống.",
                fg="#ff1744"
            )

            return

        if self.graph.directed:

            self.bipartite_result.config(
                text=(
                    "Vui lòng chuyển sang "
                    "đồ thị vô hướng để kiểm tra."
                ),
                fg="#ff1744"
            )

            return

        result = is_bipartite(
            self.graph
        )

        if result:

            a, b = get_partitions(
                self.graph
            )

            self.bipartite_result.config(
                text=(
                    "✓ ĐỒ THỊ LÀ BIPARTITE\n\n"
                    f"Tập A: {a}\n"
                    f"Tập B: {b}"
                ),
                fg="#00e5ff"
            )

        else:

            self.bipartite_result.config(
                text=(
                    "✕ ĐỒ THỊ KHÔNG PHẢI BIPARTITE"
                ),
                fg="#ff1744"
            )

    # ========================================================
    # TAB 5 - THUẬT TOÁN
    # ========================================================

    def create_algorithm_tab(self):

        tk.Label(
            self.tab_algorithm,
            text="THUẬT TOÁN ĐỒ THỊ",
            bg="#111827",
            fg="#00e5ff",
            font=("Arial", 22, "bold")
        ).pack(
            pady=50
        )

        tk.Label(
            self.tab_algorithm,
            text=(
                "Khu vực dành cho các thuật toán "
                "khác của đồ thị."
            ),
            bg="#111827",
            fg="#9ca3af",
            font=("Arial", 14)
        ).pack()

        self.algorithm_info = tk.Label(
            self.tab_algorithm,
            text="",
            bg="#111827",
            fg="white",
            font=("Consolas", 14)
        )

        self.algorithm_info.pack(
            pady=30
        )

    # ========================================================
    # UPDATE THUẬT TOÁN
    # ========================================================

    def update_algorithm(self):

        self.algorithm_info.config(
            text=(
                f"Số đỉnh hiện tại: {self.graph.n}\n"
                f"Số cạnh hiện tại: {len(self.graph.edges)}"
            )
        )


# ============================================================
# NHẬP ĐỒ THỊ BAN ĐẦU
# ============================================================

def input_graph():

    print("===================================")
    print("           NHẬP ĐỒ THỊ")
    print("===================================")

    # --------------------------------------------------------
    # SỐ ĐỈNH
    # --------------------------------------------------------

    while True:

        try:

            n = int(
                input("Nhập số đỉnh n: ")
            )

            if n > 0:
                break

            print(
                "Số đỉnh phải lớn hơn 0."
            )

        except ValueError:

            print(
                "Vui lòng nhập số nguyên."
            )

    # --------------------------------------------------------
    # SỐ CẠNH
    # --------------------------------------------------------

    while True:

        try:

            m = int(
                input("Nhập số cạnh m: ")
            )

            if m >= 0:
                break

            print(
                "Số cạnh không được âm."
            )

        except ValueError:

            print(
                "Vui lòng nhập số nguyên."
            )

    # --------------------------------------------------------
    # LOẠI ĐỒ THỊ
    # --------------------------------------------------------

    print("\nLoại đồ thị:")
    print("1. Đồ thị vô hướng")
    print("2. Đồ thị có hướng")

    while True:

        try:

            choice = int(
                input("Chọn: ")
            )

            if choice == 1:

                directed = False
                break

            if choice == 2:

                directed = True
                break

            print(
                "Chỉ được chọn 1 hoặc 2."
            )

        except ValueError:

            print(
                "Vui lòng nhập 1 hoặc 2."
            )

    # --------------------------------------------------------
    # TẠO GRAPH
    # --------------------------------------------------------

    graph = Graph(
        n,
        directed
    )

    # --------------------------------------------------------
    # NHẬP CẠNH
    # --------------------------------------------------------

    print("\n===================================")
    print("Nhập các cạnh")
    print("Dạng: u v")
    print("Hoặc: u v w")
    print("===================================")

    i = 0

    while i < m:

        print(
            f"Cạnh {i + 1}: ",
            end=""
        )

        try:

            data = input().split()

            if len(data) == 2:

                u = int(data[0])
                v = int(data[1])
                w = 1

            elif len(data) == 3:

                u = int(data[0])
                v = int(data[1])
                w = float(data[2])

                if w.is_integer():
                    w = int(w)

            else:

                print(
                    "Sai định dạng!"
                )

                continue

            if graph.add_edge(
                u,
                v,
                w
            ):

                i += 1

            else:

                print(
                    "Không thể thêm cạnh. "
                    "Kiểm tra lại đỉnh, cạnh trùng "
                    "hoặc trọng số."
                )

        except ValueError:

            print(
                "Vui lòng nhập đúng định dạng."
            )

    return graph


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # NHẬP GRAPH BẰNG TERMINAL
    # --------------------------------------------------------

    graph = input_graph()

    # --------------------------------------------------------
    # HIỆN THÔNG TIN
    # --------------------------------------------------------

    print("\n===================================")
    print("        THÔNG TIN ĐỒ THỊ")
    print("===================================")

    print(
        "Số đỉnh:",
        graph.n
    )

    print(
        "Số cạnh:",
        len(graph.edges)
    )

    if graph.directed:

        print(
            "Loại: Đồ thị có hướng"
        )

    else:

        print(
            "Loại: Đồ thị vô hướng"
        )

    graph.show_edge_list()

    graph.show_adjacency_matrix()

    graph.show_adjacency_list()

    # --------------------------------------------------------
    # MỞ GIAO DIỆN
    # --------------------------------------------------------

    root = tk.Tk()

    app = GraphApp(
        root,
        graph
    )

    root.mainloop()


# ============================================================
# CHẠY CHƯƠNG TRÌNH
# ============================================================

if __name__ == "__main__":
    main()