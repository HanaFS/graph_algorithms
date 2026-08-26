"""
Thuật toán Fleury – Tìm đường đi / chu trình Euler

Ý tưởng:
- Đi từng cạnh một, ưu tiên chọn cạnh không phải cầu (bridge).
- Dùng DFS để kiểm tra xem một cạnh có phải cầu không (Tarjan/counting).
- Tiếp tục cho đến khi không còn cạnh nào.

Điều kiện tồn tại:
  - Đường đi Euler : đúng 2 đỉnh có bậc lẻ (xuất phát từ 1 trong 2 đỉnh đó).
  - Chu trình Euler: mọi đỉnh đều có bậc chẵn.

Độ phức tạp: O(E²) do kiểm tra cầu mỗi bước.
"""

from typing import Dict, List, Tuple, Optional
import copy


# ─── Kiểu dữ liệu ─────────────────────────────────────────────────────────────
Graph = Dict[str, List[Tuple[str, float]]]
Step  = Dict  # {"current": node, "edge": (u,v,w), "path": list, "remaining": Graph}


# ─── Kiểm tra điều kiện Euler ─────────────────────────────────────────────────
def check_euler_condition(graph: Graph, directed: bool = False) -> Tuple[bool, str, Optional[str]]:
    """
    Kiểm tra đồ thị có thoả điều kiện Euler không.

    Trả về:
        (ok, message, start_node)
        ok        : True nếu có thể chạy Fleury
        message   : mô tả kết quả
        start_node: đỉnh xuất phát gợi ý (None nếu không thoả)
    """
    if not graph:
        return False, "Đồ thị rỗng.", None

    # Tính bậc mỗi đỉnh
    degree: Dict[str, int] = {n: 0 for n in graph}
    for u in graph:
        for v, _ in graph[u]:
            degree[u] += 1
            if not directed:
                pass  # với đồ thị vô hướng, cạnh đã lưu 2 chiều

    odd_nodes = [n for n, d in degree.items() if d % 2 != 0]

    if len(odd_nodes) == 0:
        # Chu trình Euler
        start = next(iter(graph))  # bất kỳ đỉnh nào có cạnh
        return True, "Tồn tại chu trình Euler (mọi đỉnh có bậc chẵn).", start
    elif len(odd_nodes) == 2:
        # Đường đi Euler
        start = odd_nodes[0]
        return True, (
            f"Tồn tại đường đi Euler. Xuất phát từ đỉnh bậc lẻ: '{start}'."
        ), start
    else:
        return False, (
            f"Không tồn tại đường/chu trình Euler. "
            f"Có {len(odd_nodes)} đỉnh bậc lẻ: {', '.join(sorted(odd_nodes))}."
        ), None


def _is_connected(graph: Dict[str, List[Tuple[str, float]]]) -> bool:
    """Kiểm tra đồ thị (với các đỉnh còn cạnh) có liên thông không."""
    # Chỉ xét đỉnh còn ít nhất 1 cạnh
    active = [n for n in graph if graph[n]]
    if not active:
        return True
    visited: set = set()
    stack = [active[0]]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        for nb, _ in graph[node]:
            if nb not in visited:
                stack.append(nb)
    return all(n in visited for n in active)


def _is_bridge(graph: Dict[str, List[Tuple[str, float]]], u: str, v: str) -> bool:
    """Kiểm tra cạnh (u, v) có phải cầu trong đồ thị hiện tại không."""
    # Đếm số đỉnh đến được từ u khi không đi qua cạnh (u, v)
    temp = copy.deepcopy(graph)
    temp[u] = [(nb, w) for nb, w in temp[u] if nb != v]
    temp[v] = [(nb, w) for nb, w in temp[v] if nb != u]
    return not _is_connected(temp)


# ─── Hàm chính ────────────────────────────────────────────────────────────────
def fleury(graph: Graph, start: str) -> Tuple[List[str], List[Step]]:
    """
    Chạy thuật toán Fleury tìm đường đi / chu trình Euler.

    Tham số:
        graph: đồ thị vô hướng (cạnh lưu 2 chiều)
        start: đỉnh xuất phát

    Trả về:
        path : danh sách đỉnh theo thứ tự đường đi Euler
        steps: danh sách các bước cho visualization

    Raises:
        ValueError: nếu start không hợp lệ hoặc không thoả điều kiện Euler.
    """
    if not graph:
        raise ValueError("Đồ thị rỗng.")
    if start not in graph:
        raise ValueError(f"Đỉnh '{start}' không tồn tại trong đồ thị.")

    ok, msg, _ = check_euler_condition(graph)
    if not ok:
        raise ValueError(msg)

    # Làm việc trên bản sao (xoá cạnh khi đi)
    g = copy.deepcopy(graph)

    path: List[str] = [start]
    steps: List[Step] = []
    current = start

    steps.append({
        "current": current,
        "edge": None,
        "path": list(path),
        "description": f"Bắt đầu từ đỉnh '{start}'.",
    })

    while True:
        neighbors = g[current]
        if not neighbors:
            break

        # Ưu tiên chọn cạnh không phải cầu
        chosen_nb, chosen_w = None, None
        for nb, w in neighbors:
            if not _is_bridge(g, current, nb):
                chosen_nb, chosen_w = nb, w
                break
        if chosen_nb is None:
            # Mọi cạnh đều là cầu → chọn cạnh đầu tiên (bắt buộc)
            chosen_nb, chosen_w = neighbors[0]

        # Xoá cạnh (current → chosen_nb) và ngược lại
        g[current] = [(nb, w) for nb, w in g[current] if nb != chosen_nb]
        g[chosen_nb] = [(nb, w) for nb, w in g[chosen_nb] if nb != current]

        path.append(chosen_nb)
        steps.append({
            "current": chosen_nb,
            "edge": (current, chosen_nb, chosen_w),
            "path": list(path),
            "description": (
                f"Đi theo cạnh ({current} — {chosen_nb}), w={chosen_w}. "
                f"Đường đi: {' → '.join(path)}."
            ),
        })
        current = chosen_nb

    steps.append({
        "current": current,
        "edge": None,
        "path": list(path),
        "description": (
            f"Hoàn thành! Đường đi Euler: {' → '.join(path)}."
            if path[0] != path[-1]
            else f"Hoàn thành! Chu trình Euler: {' → '.join(path)}."
        ),
    })

    return path, steps
