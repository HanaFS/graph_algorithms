import heapq

def dijkstra(graph, start, target=None):
    """
    Tìm đường đi ngắn nhất từ start đến tất cả các đỉnh (hoặc target) bằng thuật toán Dijkstra.
    Đồ thị không được có cạnh trọng số âm.
    Trả về: (distances, previous_nodes)
    """
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    previous = {node: None for node in graph}
    
    # Priority queue lưu (distance, node)
    pq = [(0, start)]
    
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        
        if current_distance > distances[current_node]:
            continue
            
        if target and current_node == target:
            break
            
        for neighbor, weight in graph.get(current_node, []):
            if weight < 0:
                raise ValueError("Dijkstra không hoạt động với đồ thị có trọng số âm!")
                
            distance = current_distance + weight
            
            if distance < distances.get(neighbor, float('inf')):
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))
                
    return distances, previous

def get_path(previous, start, target):
    """Truy vết đường đi từ start đến target."""
    path = []
    current = target
    while current is not None:
        path.append(current)
        if current == start:
            break
        current = previous.get(current)
    
    if not path or path[-1] != start:
        return []
    return path[::-1]
