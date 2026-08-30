# Graph Algorithms Visualizer

Một ứng dụng trực quan hóa các thuật toán đồ thị, được xây dựng bằng Python (Tkinter + Matplotlib + NetworkX). Giao diện thiết kế hiện đại, thanh lịch với các nút bấm tương tác thông minh (Reactive Buttons), hỗ trợ vẽ đồ thị động và chạy thuật toán từng bước (step-by-step).

## 🌟 Tính năng nổi bật

* **Giao diện thân thiện & Hiện đại**: Các nút bấm có khả năng phát sáng thông minh dựa trên ngữ cảnh người dùng nhập dữ liệu (Thêm đỉnh, thêm cạnh, xóa...).
* **Vẽ và chỉnh sửa đồ thị linh hoạt**: Dễ dàng thêm, xóa đỉnh và cạnh, chuyển đổi linh hoạt giữa đồ thị có hướng và vô hướng.
* **Trực quan hóa thuật toán theo từng bước**: Chức năng điều khiển (Bắt đầu, Tiến, Lùi, Kết thúc) giúp sinh viên và người dùng dễ dàng theo dõi cách các thuật toán hoạt động.

## 🛠 Yêu cầu môi trường

1. Đã cài đặt **Python 3.9+**.
2. Cài đặt các thư viện yêu cầu (có thể sử dụng môi trường ảo):
   ```bash
   pip install -e .
   ```
   Hoặc cài thủ công:
   ```bash
   pip install matplotlib networkx
   ```

## 🚀 Hướng dẫn sử dụng

Khởi động giao diện chính của ứng dụng bằng lệnh:
```bash
python main.py
```
*(Hoặc chạy qua file `ui/graph_ui.py`)*

Để chạy Unit Test kiểm định logic các thuật toán:
```bash
python -m unittest discover -s tests/unit
```

## 📂 Danh sách 6 Tab chức năng chính

1. **1. Đồ thị**: Vẽ trực quan, thêm/xóa đỉnh cạnh, chuyển đổi Vô hướng $\leftrightarrow$ Có hướng, tự động căn chỉnh và xuất ảnh.
2. **2. Biểu diễn**: Tự động trích xuất các biểu diễn đồ thị: Ma trận kề, Danh sách kề, Danh sách cạnh (3 cột song song).
3. **3. Duyệt BFS/DFS**: Trực quan hóa thuật toán Tìm kiếm theo chiều rộng (BFS) và Tìm kiếm theo chiều sâu (DFS), hiển thị cây khung duyệt và thứ tự thăm.
4. **4. Hai phía**: Kiểm tra đồ thị 2 phía (Bipartite), tự động tô màu 2 tập đỉnh độc lập A/B.
5. **5. Đường ngắn nhất**: Thuật toán Dijkstra & Bellman-Ford, hiển thị bảng khoảng cách từng bước.
6. **6. Thuật toán nâng cao**:
   * **Fleury & Hierholzer**: Tìm đường đi / chu trình Euler.
   * **Prim & Kruskal**: Tìm cây khung nhỏ nhất (Minimum Spanning Tree).
   * **Ford-Fulkerson**: Tìm luồng cực đại trong mạng luồng (Max Flow).


