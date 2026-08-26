"""
Thuật toán Hierholzer – Tìm chu trình Euler hiệu quả

Ý tưởng:
- Dùng stack để duyệt đồ thị.
- Khi đỉnh hiện tại không còn cạnh, thêm vào kết quả (backtrack).
- Stack + đảo ngược → chu trình Euler O(E).

Điều kiện:
  - Chu trình Euler: mọi đỉnh có bậc chẵn, đồ thị liên thông.
  - Đường đi Euler  : đúng 2 đỉnh bậc lẻ.

Độ phức tạp: O(V + E).
"""

from typing import Dict, List, Tuple, Optional
import copy


# ─── Kiểu dữ liệu ─────────────────────────────────────────────────────────────
Graph = Dict[str, List[Tuple[str, float]]]
Step  = Dict  # {"stack": list, "circuit": list, "current": str}


# ─── Kiểm tra điều kiện ───────────────────────────────────────────────────────
def check_euler_condition(graph: Graph) -> Tuple[bool, str, Optional[str]]:
    """
    Kiểm tra đồ thị vô hướng có tồn tại đường/chu trình Euler không.

    Trả về (ok, message, start_node).
    """
    if not graph:
        return False, "Đồ thị rỗng.", None

    degree = {n: len(graph[n]) for n in graph}
    odd_nodes = [n for n, d in degree.items() if d % 2 != 0]

    if len(odd_nodes) == 0:
        start = next(iter(graph))
        return True, "Tồn tại chu trình Euler.", start
    elif len(odd_nodes) == 2:
        start = odd_nodes[0]
        return True, f"Tồn tại đường đi Euler. Xuất phát từ '{start}'.", start
    else:
        return False, (
            f"Không tồn tại đường/chu trình Euler. "
            f"{len(odd_nodes)} đỉnh bậc lẻ: {', '.join(sorted(odd_nodes))}."
        ), None


# ─── Hàm chính ────────────────────────────────────────────────────────────────
def hierholzer(graph: Graph, start: str) -> Tuple[List[str], List[Step]]:
    """
    Chạy thuật toán Hierholzer tìm chu trình / đường đi Euler.

    Tham số:
        graph: đồ thị vô hướng (cạnh lưu 2 chiều)
        start: đỉnh xuất phát

    Trả về:
        circuit: danh sách đỉnh theo thứ tự chu trình Euler
        steps  : danh sách các bước cho visualization

    Raises:
        ValueError: nếu điều kiện Euler không thoả.
    """
    if not graph:
        raise ValueError("Đồ thị rỗng.")
    if start not in graph:
        raise ValueError(f"Đỉnh '{start}' không tồn tại trong đồ thị.")

    ok, msg, _ = check_euler_condition(graph)
    if not ok:
        raise ValueError(msg)

    # Làm việc trên bản sao – dùng list copy để xoá cạnh dễ
    # Lưu dạng {node: [neighbor, ...]} (bỏ weight để xử lý nhanh, giữ weight riêng)
    adj: Dict[str, List[str]] = {n: [nb for nb, _ in graph[n]] for n in graph}
    # Bảng weight để lưu lại khi trace
    weight_map: Dict[Tuple[str, str], float] = {}
    for u in graph:
        for v, w in graph[u]:
            weight_map[(u, v)] = w

    stack: List[str] = [start]
    circuit: List[str] = []
    steps: List[Step] = []

    steps.append({
        "stack": list(stack),
        "circuit": list(circuit),
        "current": start,
        "action": "init",
        "description": f"Khởi tạo stack = ['{start}'], circuit = [].",
    })

    while stack:
        v = stack[-1]
        if adj[v]:
            # Còn cạnh → đẩy đỉnh kế vào stack, xoá cạnh
            u = adj[v].pop(0)
            # Xoá cạnh ngược
            if u in adj and v in adj[u]:
                adj[u].remove(v)
            stack.append(u)
            steps.append({
                "stack": list(stack),
                "circuit": list(circuit),
                "current": u,
                "edge": (v, u, weight_map.get((v, u), 1)),
                "action": "push",
                "description": (
                    f"Đi theo cạnh ({v} → {u}). "
                    f"Stack = {stack}."
                ),
            })
        else:
            # Không còn cạnh → backtrack, thêm vào circuit
            stack.pop()
            circuit.append(v)
            steps.append({
                "stack": list(stack),
                "circuit": list(circuit),
                "current": v,
                "action": "backtrack",
                "description": (
                    f"'{v}' không còn cạnh → thêm vào circuit. "
                    f"Circuit = {circuit}."
                ),
            })

    circuit.reverse()

    steps.append({
        "stack": [],
        "circuit": list(circuit),
        "current": None,
        "action": "done",
        "description": (
            f"Hoàn thành! "
            + ("Chu trình Euler: " if circuit[0] == circuit[-1] else "Đường đi Euler: ")
            + " → ".join(circuit) + "."
        ),
    })

    return circuit, steps
