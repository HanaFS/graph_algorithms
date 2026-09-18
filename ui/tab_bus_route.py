# ui/tab_bus_route.py
"""
Tab 7 - Ứng dụng thực tế: Tìm tuyến xe buýt ngắn nhất.

- Mạng mẫu 20 trạm
- Dijkstra tìm tuyến có tổng quãng đường nhỏ nhất
- Hiển thị tuyến, tổng km, số đoạn và chi tiết từng chặng
- Tô nổi đường đi trên đồ thị chung của ứng dụng
"""

import tkinter as tk
from tkinter import ttk, messagebox

from .theme import BG, PANEL, ACCENT, ACCENT2, SUCCESS, TEXT, TEXT2


class Tab7Mixin:
    def _tab7(self, p):
        self._tab_toolbar(p, "Ứng dụng thực tế - Tìm tuyến xe buýt ngắn nhất")

        # ===== KHU VỰC ĐIỀU KHIỂN =====
        ctrl = tk.Frame(p, bg=PANEL, relief="solid", bd=1)
        ctrl.pack(fill=tk.X, padx=8, pady=(0, 6))

        ctrl.columnconfigure(1, weight=1)
        ctrl.columnconfigure(3, weight=1)

        tk.Label(
            ctrl, text="Trạm xuất phát:",
            bg=PANEL, fg=TEXT, font=("Segoe UI", 10)
        ).grid(row=0, column=0, padx=(12, 6), pady=10)

        self.e_bus_src = ttk.Combobox(
            ctrl, width=18, state="readonly", font=("Segoe UI", 10)
        )
        self.e_bus_src.grid(row=0, column=1, sticky="ew", padx=6, pady=10)

        tk.Label(
            ctrl, text="Trạm đến:",
            bg=PANEL, fg=TEXT, font=("Segoe UI", 10)
        ).grid(row=0, column=2, padx=(12, 6), pady=10)

        self.e_bus_tgt = ttk.Combobox(
            ctrl, width=18, state="readonly", font=("Segoe UI", 10)
        )
        self.e_bus_tgt.grid(row=0, column=3, sticky="ew", padx=6, pady=10)

        self._btn(
            ctrl, "Nạp mạng xe buýt 20 trạm",
            self._load_bus_sample, ACCENT2
        ).grid(row=0, column=4, padx=6, pady=10)

        self._btn(
            ctrl, "Tìm tuyến",
            self._bus_find_route, SUCCESS
        ).grid(row=0, column=5, padx=(6, 12), pady=10)

        # ===== GIẢI THÍCH MÔ HÌNH =====
        info = tk.Frame(p, bg=PANEL, relief="solid", bd=1)
        info.pack(fill=tk.X, padx=8, pady=(0, 6))

        tk.Label(
            info,
            text=(
                "Mô hình: trạm xe buýt = đỉnh, đoạn đường = cạnh, "
                "trọng số = quãng đường (km). "
                "Dijkstra tìm tuyến có tổng quãng đường nhỏ nhất."
            ),
            bg=PANEL, fg=TEXT2, font=("Segoe UI", 9),
            justify="left", anchor="w"
        ).pack(fill=tk.X, padx=12, pady=10)

        # ===== KẾT QUẢ =====
        result = tk.Frame(p, bg=PANEL, relief="solid", bd=1)
        result.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        tk.Label(
            result, text="Kết quả tìm tuyến",
            bg=PANEL, fg=ACCENT,
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=12, pady=(12, 6))

        ttk.Separator(result, orient="horizontal").pack(fill=tk.X, padx=12)

        self.rbus = tk.Text(
            result,
            height=16,
            bg="#f0fdf4",
            fg=SUCCESS,
            font=("Courier New", 10),
            relief="flat",
            state="disabled",
            padx=8,
            pady=8
        )
        self.rbus.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

    def _load_bus_sample(self):
        """Nạp mạng xe buýt mẫu gồm 20 trạm."""
        if self.graph and not messagebox.askyesno(
            "Nạp mạng xe buýt",
            "Đồ thị hiện tại sẽ được thay bằng mạng xe buýt mẫu 20 trạm.\n"
            "Bạn có tiếp tục không?"
        ):
            return

        self._save_state()
        self.directed.set(False)

        # 20 trạm:
        # 1 Bến xe, 2 Ngã tư 1, 3 Chợ, 4 Trường học, 5 ĐH GTVT,
        # 6 Bệnh viện, 7 Công viên, 8 Siêu thị, 9 Ga Metro, 10 Bưu điện,
        # 11 Nhà văn hóa, 12 Sân vận động, 13 Khu dân cư, 14 Ngã tư 2,
        # 15 Trung tâm TM, 16 Bến tàu, 17 Nhà ga, 18 Khu công nghiệp,
        # 19 Sân bay, 20 Bến Thành.
        edges = [
            ("Bến xe", "Ngã tư 1", 4),
            ("Bến xe", "Chợ", 6),

            ("Ngã tư 1", "Trường học", 3),
            ("Ngã tư 1", "ĐH GTVT", 5),

            ("Chợ", "Trường học", 2),
            ("Chợ", "Bệnh viện", 4),

            ("Trường học", "Công viên", 3),
            ("Trường học", "ĐH GTVT", 2),

            ("Bệnh viện", "Công viên", 2),
            ("Bệnh viện", "Siêu thị", 5),

            ("Công viên", "Ga Metro", 4),

            ("ĐH GTVT", "Ga Metro", 3),
            ("ĐH GTVT", "Bưu điện", 4),

            ("Siêu thị", "Bưu điện", 3),
            ("Siêu thị", "Nhà văn hóa", 5),

            ("Ga Metro", "Bưu điện", 2),
            ("Ga Metro", "Sân vận động", 4),

            ("Bưu điện", "Nhà văn hóa", 3),
            ("Bưu điện", "Khu dân cư", 5),

            ("Nhà văn hóa", "Ngã tư 2", 3),
            ("Sân vận động", "Khu dân cư", 2),

            ("Khu dân cư", "Ngã tư 2", 3),
            ("Khu dân cư", "Trung tâm TM", 4),

            ("Ngã tư 2", "Bến tàu", 4),

            ("Trung tâm TM", "Bến tàu", 2),
            ("Trung tâm TM", "Nhà ga", 3),

            ("Bến tàu", "Nhà ga", 3),
            ("Bến tàu", "Khu công nghiệp", 5),

            ("Nhà ga", "Khu công nghiệp", 2),
            ("Nhà ga", "Sân bay", 6),

            ("Khu công nghiệp", "Sân bay", 4),
            ("Khu công nghiệp", "Bến Thành", 5),

            ("Sân bay", "Bến Thành", 3),
        ]

        self.graph = {}
        for u, v, w in edges:
            self.graph.setdefault(u, []).append((v, w))
            self.graph.setdefault(v, []).append((u, w))

        # Xóa vị trí cũ để ứng dụng tự bố trí lại 20 đỉnh.
        self._pos = {}

        # Cập nhật các phần dùng chung của app.
        self._upd_info()
        self._show_repr()
        self._update_action_buttons()

        nodes = sorted(self.graph.keys())
        self.e_bus_src["values"] = nodes
        self.e_bus_tgt["values"] = nodes
        self.e_bus_src.set("Bến xe")
        self.e_bus_tgt.set("Bến Thành")

        self._settext(
            self.rbus,
            "ĐÃ NẠP MẠNG XE BUÝT 20 TRẠM\n\n"
            "Trạm mặc định: Bến xe → Bến Thành\n"
            "Nhấn 'Tìm tuyến' để chạy thuật toán Dijkstra.\n\n"
            "Đồ thị đã được vẽ ở vùng hiển thị đồ thị chung của ứng dụng."
        )

        # Vẽ sau khi dữ liệu đã cập nhật.
        self.draw(title="Mạng xe buýt 20 trạm")

    def _bus_find_route(self):
        """Tìm đường ngắn nhất giữa hai trạm bằng Dijkstra."""
        start = self.e_bus_src.get().strip()
        target = self.e_bus_tgt.get().strip()

        if not self.graph:
            messagebox.showwarning(
                "Thiếu dữ liệu",
                "Chưa có đồ thị. Hãy nhấn 'Nạp mạng xe buýt 20 trạm'."
            )
            return

        if not start or not target:
            messagebox.showwarning(
                "Thiếu trạm",
                "Vui lòng chọn trạm xuất phát và trạm đến."
            )
            return

        if not self._chk(start) or not self._chk(target):
            return

        if start == target:
            self._settext(
                self.rbus,
                f"Trạm xuất phát và trạm đến đều là: {start}\n"
                "Tổng quãng đường: 0 km"
            )
            self.draw(hi_n={start}, title=f"Tuyến xe buýt: {start}")
            return

        # Dijkstra không dùng được nếu có trọng số âm.
        for u in self.graph:
            for v, w in self.graph[u]:
                if w < 0:
                    messagebox.showerror(
                        "Không thể chạy Dijkstra",
                        f"Cạnh {u} - {v} có trọng số âm ({w})."
                    )
                    return

        try:
            from src.graph_algorithms.algorithms.shortest_path.dijkstra import (
                dijkstra,
                get_path,
            )

            dist, prev = dijkstra(self.graph, start, target)
            distance = dist.get(target, float("inf"))
            path = get_path(prev, start, target)

        except Exception as e:
            messagebox.showerror("Lỗi Dijkstra", str(e))
            self._settext(self.rbus, f"LỖI: {e}")
            return

        if distance == float("inf") or not path:
            self._settext(
                self.rbus,
                f"Không tìm thấy tuyến xe buýt từ {start} đến {target}."
            )
            return

        # Chuẩn hóa số km.
        if isinstance(distance, (int, float)) and float(distance).is_integer():
            distance_text = str(int(distance))
        else:
            distance_text = str(distance)

        # Chi tiết từng đoạn trên tuyến.
        details = []
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i + 1]
            w = self._bus_edge_weight(u, v)
            details.append(f"  {i + 1}. {u} → {v}: {w} km")

        route_text = " → ".join(path)

        output = (
            f"TRẠM XUẤT PHÁT: {start}\n"
            f"TRẠM ĐẾN      : {target}\n\n"
            f"TUYẾN NGẮN NHẤT:\n{route_text}\n\n"
            f"TỔNG QUÃNG ĐƯỜNG: {distance_text} km\n"
            f"SỐ ĐOẠN ĐI QUA : {len(path) - 1}\n"
            f"SỐ TRẠM TRÊN TUYẾN: {len(path)}\n\n"
            "CHI TIẾT TỪNG CHẶNG:\n"
            + "\n".join(details)
        )

        self._settext(self.rbus, output)

        # Tô nổi tuyến trên đồ thị.
        hi_edges = set(zip(path, path[1:]))
        self.draw(
            hi_n=set(path),
            hi_e=hi_edges,
            title=f"Tuyến ngắn nhất: {start} → {target} ({distance_text} km)"
        )

    def _bus_edge_weight(self, u, v):
        """Lấy trọng số cạnh u-v để hiển thị chi tiết tuyến."""
        for nxt, weight in self.graph.get(u, []):
            if nxt == v:
                if isinstance(weight, (int, float)) and float(weight).is_integer():
                    return int(weight)
                return weight
        return "?"
