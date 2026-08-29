from graph import Graph
from traversal import bfs, dfs
from bipartite import is_bipartite, get_partitions


# ============================================================
# NHẬP ĐỒ THỊ
# ============================================================

def input_graph():

    print("===================================")
    print("           NHẬP ĐỒ THỊ")
    print("===================================")

    # Nhập số đỉnh
    while True:
        try:
            n = int(input("Nhập số đỉnh n: "))

            if n > 0:
                break

            print("Số đỉnh phải lớn hơn 0.")

        except:
            print("Vui lòng nhập số nguyên.")

    # Nhập số cạnh
    while True:
        try:
            m = int(input("Nhập số cạnh m: "))

            if m >= 0:
                break

            print("Số cạnh không được âm.")

        except:
            print("Vui lòng nhập số nguyên.")

    # Chọn loại đồ thị
    print("\nLoại đồ thị:")
    print("1. Đồ thị vô hướng")
    print("2. Đồ thị có hướng")

    while True:
        try:
            choice = int(input("Chọn: "))

            if choice == 1:
                directed = False
                break

            elif choice == 2:
                directed = True
                break

            else:
                print("Chỉ được chọn 1 hoặc 2.")

        except:
            print("Vui lòng nhập 1 hoặc 2.")

    # Tạo đồ thị
    graph = Graph(n, directed)

    # Nhập các cạnh
    print("\n===================================")
    print("Nhập các cạnh")
    print("Dạng: u v")
    print("Hoặc: u v w")
    print("===================================")

    i = 0

    while i < m:

        try:
            data = input(f"Cạnh {i + 1}: ").split()

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
                print("Sai định dạng!")
                continue

            if graph.add_edge(u, v, w):
                i += 1
            else:
                print(
                    "Không thể thêm cạnh."
                )
                print(
                    "Kiểm tra lại đỉnh, cạnh trùng "
                    "hoặc trọng số."
                )

        except:
            print("Vui lòng nhập đúng định dạng.")

    return graph


# ============================================================
# HIỂN THỊ THÔNG TIN ĐỒ THỊ
# ============================================================

def show_graph_information(graph):

    print("\n===================================")
    print("        THÔNG TIN ĐỒ THỊ")
    print("===================================")

    print("Số đỉnh:", graph.n)
    print("Số cạnh:", len(graph.edges))

    if graph.directed:
        print("Loại: Đồ thị có hướng")
    else:
        print("Loại: Đồ thị vô hướng")

    print("\n========== DANH SÁCH CẠNH ==========")
    graph.show_edge_list()

    print("\n========== MA TRẬN KỀ ==========")
    graph.show_adjacency_matrix()

    print("\n========== DANH SÁCH KỀ ==========")
    graph.show_adjacency_list()


# ============================================================
# CHẠY BFS
# ============================================================

def run_bfs(graph):

    if graph.n == 0:
        print("Đồ thị đang trống.")
        return

    while True:

        try:
            start = int(input("Nhập đỉnh bắt đầu BFS: "))

            if start < 1 or start > graph.n:
                print("Đỉnh không tồn tại.")
                continue

            break

        except:
            print("Vui lòng nhập số nguyên.")

    result = bfs(graph, start)

    print("\nKết quả BFS:")
    print(" -> ".join(map(str, result)))


# ============================================================
# CHẠY DFS
# ============================================================

def run_dfs(graph):

    if graph.n == 0:
        print("Đồ thị đang trống.")
        return

    while True:

        try:
            start = int(input("Nhập đỉnh bắt đầu DFS: "))

            if start < 1 or start > graph.n:
                print("Đỉnh không tồn tại.")
                continue

            break

        except:
            print("Vui lòng nhập số nguyên.")

    result = dfs(graph, start)

    print("\nKết quả DFS:")
    print(" -> ".join(map(str, result)))


# ============================================================
# KIỂM TRA BIPARTITE
# ============================================================

def run_bipartite(graph):

    if graph.n == 0:
        print("Đồ thị đang trống.")
        return

    if graph.directed:
        print(
            "Bipartite trong chương trình này "
            "chỉ kiểm tra đồ thị vô hướng."
        )
        return

    result = is_bipartite(graph)

    if result:

        a, b = get_partitions(graph)

        print("\nĐỒ THỊ LÀ BIPARTITE")
        print("Tập A:", a)
        print("Tập B:", b)

    else:

        print("\nĐỒ THỊ KHÔNG PHẢI BIPARTITE")


# ============================================================
# MENU
# ============================================================

def menu(graph):

    while True:

        print("\n")
        print("===================================")
        print("          GRAPH ALGORITHMS")
        print("===================================")

        print("1. Hiển thị thông tin đồ thị")
        print("2. BFS")
        print("3. DFS")
        print("4. Kiểm tra Bipartite")
        print("5. Thêm đỉnh")
        print("6. Thêm cạnh")
        print("7. Xóa đỉnh")
        print("8. Xóa cạnh")
        print("9. Đổi loại đồ thị")
        print("10. Xóa toàn bộ đồ thị")
        print("0. Thoát")

        print("===================================")

        choice = input("Chọn chức năng: ")

        # ----------------------------------------------------
        # HIỂN THỊ
        # ----------------------------------------------------

        if choice == "1":

            show_graph_information(graph)

        # ----------------------------------------------------
        # BFS
        # ----------------------------------------------------

        elif choice == "2":

            run_bfs(graph)

        # ----------------------------------------------------
        # DFS
        # ----------------------------------------------------

        elif choice == "3":

            run_dfs(graph)

        # ----------------------------------------------------
        # BIPARTITE
        # ----------------------------------------------------

        elif choice == "4":

            run_bipartite(graph)

        # ----------------------------------------------------
        # THÊM ĐỈNH
        # ----------------------------------------------------

        elif choice == "5":

            try:

                graph.add_vertex()

                print(
                    "Đã thêm đỉnh.",
                    "Số đỉnh hiện tại:",
                    graph.n
                )

            except:

                print("Không thể thêm đỉnh.")

        # ----------------------------------------------------
        # THÊM CẠNH
        # ----------------------------------------------------

        elif choice == "6":

            try:

                u = int(input("Nhập đỉnh u: "))
                v = int(input("Nhập đỉnh v: "))

                weight_input = input(
                    "Nhập trọng số (Enter = 1): "
                )

                if weight_input == "":
                    w = 1
                else:
                    w = float(weight_input)

                    if w.is_integer():
                        w = int(w)

                if w == 0:
                    print(
                        "Trọng số không được bằng 0."
                    )

                elif graph.add_edge(u, v, w):

                    print("Đã thêm cạnh.")

                else:

                    print(
                        "Không thể thêm cạnh."
                    )

            except:

                print(
                    "Dữ liệu nhập không hợp lệ."
                )

        # ----------------------------------------------------
        # XÓA ĐỈNH
        # ----------------------------------------------------

        elif choice == "7":

            try:

                vertex = int(
                    input("Nhập đỉnh cần xóa: ")
                )

                if graph.delete_vertex(vertex - 1):

                    print("Đã xóa đỉnh.")

                else:

                    print(
                        "Không thể xóa đỉnh."
                    )

            except:

                print(
                    "Dữ liệu không hợp lệ."
                )

        # ----------------------------------------------------
        # XÓA CẠNH
        # ----------------------------------------------------

        elif choice == "8":

            try:

                u = int(
                    input("Nhập đỉnh u: ")
                )

                v = int(
                    input("Nhập đỉnh v: ")
                )

                if graph.delete_edge(u, v):

                    print("Đã xóa cạnh.")

                else:

                    print(
                        "Không tìm thấy cạnh."
                    )

            except:

                print(
                    "Dữ liệu không hợp lệ."
                )

        # ----------------------------------------------------
        # ĐỔI LOẠI ĐỒ THỊ
        # ----------------------------------------------------

        elif choice == "9":

            print("\nLoại đồ thị mới:")
            print("1. Vô hướng")
            print("2. Có hướng")

            choice_type = input("Chọn: ")

            if choice_type == "1":

                graph.change_direction(False)

                print(
                    "Đã chuyển sang đồ thị vô hướng."
                )

            elif choice_type == "2":

                graph.change_direction(True)

                print(
                    "Đã chuyển sang đồ thị có hướng."
                )

            else:

                print("Lựa chọn không hợp lệ.")

        # ----------------------------------------------------
        # XÓA TOÀN BỘ
        # ----------------------------------------------------

        elif choice == "10":

            confirm = input(
                "Bạn có chắc muốn xóa toàn bộ? (y/n): "
            )

            if confirm.lower() == "y":

                graph.clear()

                print(
                    "Đã xóa toàn bộ đồ thị."
                )

        # ----------------------------------------------------
        # THOÁT
        # ----------------------------------------------------

        elif choice == "0":

            print("Kết thúc chương trình.")
            break

        else:

            print(
                "Lựa chọn không hợp lệ."
            )


# ============================================================
# MAIN
# ============================================================

def main():

    graph = input_graph()

    show_graph_information(graph)

    menu(graph)


# ============================================================
# CHẠY
# ============================================================

if __name__ == "__main__":
    main()
