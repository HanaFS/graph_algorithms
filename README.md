# Graph Algorithms Visualizer

Giao diện đồ họa Python (tkinter + matplotlib + networkx) phong cách Qt thanh lịch, hiện đại với các nút tương tác thông minh (Reactive Glowing Buttons) và bộ công cụ Xóa.

## Yêu cầu môi trường

1. Đã cài đặt **Python 3.14** (hoặc môi trường ảo `.venv` trong thư mục dự án).
2. Các thư viện:
   ```bash
   pip install matplotlib networkx
   ```

## Cách chạy giao diện đồ họa (GUI)

Để khởi động giao diện ứng dụng:
```bash
.venv/bin/python ui/graph_ui.py
```

## Chạy Unit Test kiểm định thuật toán

```bash
.venv/bin/python -m unittest discover -s tests/unit
```

## Các tính năng tương tác nổi bật

* **💡 Nút "+ Thêm đỉnh" tự động sáng đèn**:
  * Khi gõ tên đỉnh vào ô nhập: Nút lập tức phát sáng tím neon rực rỡ `💡 Thêm đỉnh`.
  * Khi ô nhập trống: Nút tự động chuyển về trạng thái mờ dịu (`+ Thêm đỉnh`).
* **✨ Nút "+ Thêm cạnh" tự động sáng đèn**:
  * Khi nhập đủ cả đỉnh Từ (From) và Đến (To): Nút lập tức phát sáng Cyan nổi bật `✨ Thêm cạnh`.
  * Khi chưa đủ thông tin: Nút ở trạng thái mờ dịu.
* **💡 Nút "Vẽ lại" & "Lưu hình" tự động sáng đèn**:
  * Khi đồ thị có dữ liệu: Các nút `💡 ↺ Vẽ lại`, `💡 💾 Lưu hình` tự động sáng đèn rực rỡ.
  * Khi đồ thị trống: Các nút chuyển về màu mờ nền nã.
* **🔥 Mục "Xóa đỉnh & Cạnh" (Delete Tools)**:
  * **Xoá 1 đỉnh**: Ô nhập tên đỉnh cần xoá $\rightarrow$ Khi gõ vào, nút sáng đèn đỏ `🔥 Xoá đỉnh`.
  * **Xoá 1 cạnh**: Ô nhập cạnh cần xoá (Từ $\rightarrow$ Đến) $\rightarrow$ Khi gõ vào, nút sáng đèn đỏ `🔥 Xoá cạnh`.
  * **Xoá toàn bộ đồ thị**: Nút `✕ Xóa sạch toàn bộ đồ thị` với hộp thoại xác nhận an toàn.

## Danh sách 5 Tab chức năng

1. **1. Đồ thị**: Vẽ trực quan, chuyển đổi Vô hướng $\leftrightarrow$ Có hướng, nút *Vẽ lại* và *Lưu hình*.
2. **2. Biểu diễn**: Ma trận kề, Danh sách kề, Danh sách cạnh (3 cột song song).
3. **3. Duyệt BFS/DFS**: Duyệt BFS & DFS và so sánh kết quả chạy tay.
4. **4. Hai phía**: Kiểm tra đồ thị 2 phía (Bipartite), tô màu 2 tập đỉnh A/B.
5. **5. Đường ngắn nhất**: Dijkstra & Bellman-Ford, bảng khoảng cách và so sánh chạy tay.
