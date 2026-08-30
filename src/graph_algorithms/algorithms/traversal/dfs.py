"""
Thuật toán duyệt đồ thị theo chiều sâu (Depth-First Search – DFS).

Hỗ trợ cả hai dạng đầu vào:
  - Graph object (dùng với module graph.py) có thuộc tính adj / adj_list
  - dict adjacency list (dùng nội bộ trong graph_ui.py):
      { node: [(neighbor, weight), ...], ... }
"""

from typing import Any, List


def dfs(graph, start: Any) -> List[Any]:
    """
    Duyệt DFS từ đỉnh `start` (dùng stack – iterative).

    Đẩy hàng xóm theo thứ tự ngược để khi pop sẽ thăm theo thứ tự
    tăng dần (tên), tạo kết quả ổn định và dễ đối chiếu tay.

    Parameters
    ----------
    graph : Graph object hoặc dict
        - Nếu là Graph object: phải có thuộc tính `adj` là dict
          mapping node → list[(neighbor, weight)] hoặc list[neighbor].
        - Nếu là dict: dạng { node: [(neighbor, weight), ...] }.
    start : Any
        Đỉnh bắt đầu duyệt.

    Returns
    -------
    List[Any]
        Danh sách các đỉnh theo thứ tự DFS.
    """
    adj = _get_adj(graph)

    visited: set = set()
    stack = [start]
    order: List[Any] = []

    while stack:
        u = stack.pop()
        if u in visited:
            continue
        visited.add(u)
        order.append(u)

        # Đẩy hàng xóm theo thứ tự ngược để thứ tự pop đúng
        for neighbor in reversed(_neighbors(adj, u)):
            if neighbor not in visited:
                stack.append(neighbor)

    return order


# ── Internal helpers ──────────────────────────────────────────────────────────

def _get_adj(graph) -> dict:
    """Trích xuất adjacency dict từ Graph object hoặc dict thuần."""
    if isinstance(graph, dict):
        return graph
    for attr in ("adj", "adj_list", "adjacency_list", "adjacency"):
        if hasattr(graph, attr):
            return getattr(graph, attr)
    raise TypeError(
        "graph phải là dict hoặc object có thuộc tính 'adj'/'adj_list'."
    )


def _neighbors(adj: dict, u: Any) -> List[Any]:
    """
    Trả về danh sách đỉnh kề của u (đã sắp xếp để kết quả ổn định).
    Hỗ trợ danh sách kề dạng [(neighbor, weight), ...] hoặc [neighbor, ...].
    """
    raw = adj.get(u, [])
    result = []
    for item in raw:
        if isinstance(item, (list, tuple)):
            result.append(item[0])   # (neighbor, weight)
        else:
            result.append(item)      # neighbor thuần
    try:
        return sorted(result, key=str)
    except TypeError:
        return result
