"""
Các thuật toán cơ bản: BFS, DFS, Dijkstra, Bellman-Ford, Bipartite Check
"""

from collections import deque

class GraphAlgorithms:
    
    @staticmethod
    def bfs(graph, start):
        """Thuật toán BFS - Duyệt đồ thị theo chiều rộng"""
        visited = set()
        queue = deque([start])
        result = []
        parent = {start: None}
        
        visited.add(start)
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            # Sắp xếp để có thứ tự nhất quán
            neighbors = sorted(graph.get_neighbors(node), key=lambda x: x[0])
            
            for neighbor, _ in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = node
                    queue.append(neighbor)
        
        return result, parent
    
    @staticmethod
    def dfs(graph, start):
        """Thuật toán DFS - Duyệt đồ thị theo chiều sâu"""
        visited = set()
        result = []
        parent = {start: None}
        
        def dfs_recursive(node):
            visited.add(node)
            result.append(node)
            
            # Sắp xếp để có thứ tự nhất quán
            neighbors = sorted(graph.get_neighbors(node), key=lambda x: x[0])
            
            for neighbor, _ in neighbors:
                if neighbor not in visited:
                    parent[neighbor] = node
                    dfs_recursive(neighbor)
        
        dfs_recursive(start)
        return result, parent
    
    @staticmethod
    def dijkstra(graph, start, end=None):
        """Thuật toán Dijkstra - Tìm đường đi ngắn nhất"""
        distances = {node: float('infinity') for node in graph.nodes}
        distances[start] = 0
        parent = {start: None}
        unvisited = set(graph.nodes)
        
        while unvisited:
            # Tìm node chưa thăm có khoảng cách nhỏ nhất
            current = min(unvisited, key=lambda node: distances[node])
            
            if distances[current] == float('infinity'):
                break
            
            if end and current == end:
                break
            
            unvisited.remove(current)
            
            # Cập nhật khoảng cách cho các láng giềng
            for neighbor, weight in graph.get_neighbors(current):
                if neighbor in unvisited:
                    new_distance = distances[current] + weight
                    
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        parent[neighbor] = current
        
        return distances, parent
    
    @staticmethod
    def bellman_ford(graph, start):
        """Thuật toán Bellman-Ford - Tìm đường đi ngắn nhất (có chu trình âm)"""
        distances = {node: float('infinity') for node in graph.nodes}
        distances[start] = 0
        parent = {start: None}
        
        # Relax tất cả các cạnh V-1 lần
        for _ in range(len(graph.nodes) - 1):
            for u in graph.adjacency_list:
                for v, weight in graph.adjacency_list[u]:
                    if distances[u] + weight < distances[v]:
                        distances[v] = distances[u] + weight
                        parent[v] = u
        
        # Kiểm tra chu trình âm
        has_negative_cycle = False
        for u in graph.adjacency_list:
            for v, weight in graph.adjacency_list[u]:
                if distances[u] + weight < distances[v]:
                    has_negative_cycle = True
                    break
        
        return distances, parent, has_negative_cycle
    
    @staticmethod
    def reconstruct_path(parent, start, end):
        """Tái tạo đường đi từ start đến end"""
        if end not in parent:
            return None
        
        path = []
        current = end
        
        while current is not None:
            path.append(current)
            current = parent.get(current)
        
        path.reverse()
        
        if path[0] != start:
            return None
        
        return path
    
    @staticmethod
    def is_bipartite(graph):
        """Kiểm tra đồ thị có phải là đồ thị hai phía không"""
        color = {}
        
        def bfs_color(start):
            queue = deque([start])
            color[start] = 0
            
            while queue:
                node = queue.popleft()
                current_color = color[node]
                
                for neighbor, _ in graph.get_neighbors(node):
                    if neighbor not in color:
                        color[neighbor] = 1 - current_color
                        queue.append(neighbor)
                    elif color[neighbor] == current_color:
                        return False
            return True
        
        # Kiểm tra tất cả các thành phần liên thông
        for node in graph.nodes:
            if node not in color:
                if not bfs_color(node):
                    return False, {}
        
        # Chia thành 2 tập
        set_0 = [node for node, c in color.items() if c == 0]
        set_1 = [node for node, c in color.items() if c == 1]
        
        return True, {'Set A': set_0, 'Set B': set_1}
