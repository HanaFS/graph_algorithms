def bellman_ford(graph, start, target=None):
    """
    Tìm đường đi ngắn nhất từ start đến tất cả các đỉnh bằng thuật toán Bellman-Ford.
    Xử lý được cạnh trọng số âm, phát hiện chu trình âm.
    Trả về: (distances, previous_nodes)
    Ném ngoại lệ ValueError nếu có chu trình âm.
    """
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    previous = {node: None for node in graph}
    
    nodes = list(graph.keys())
    
    # V - 1 lần lặp (V là số đỉnh)
    for _ in range(len(nodes) - 1):
        for u in nodes:
            if distances[u] == float('inf'):
                continue
            for v, weight in graph.get(u, []):
                if distances[u] + weight < distances.get(v, float('inf')):
                    distances[v] = distances[u] + weight
                    previous[v] = u
                    
    # Lần lặp thứ V để kiểm tra chu trình âm
    for u in nodes:
        if distances[u] == float('inf'):
            continue
        for v, weight in graph.get(u, []):
            if distances[u] + weight < distances.get(v, float('inf')):
                # Phát hiện chu trình âm
                raise ValueError("Đồ thị chứa chu trình âm có thể đi tới được từ đỉnh xuất phát!")
                
    return distances, previous
