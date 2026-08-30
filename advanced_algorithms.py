"""
Các thuật toán nâng cao: Fleury, Hierholzer, Prim, Kruskal, Ford-Fulkerson
"""

from collections import defaultdict, deque
import copy

class AdvancedAlgorithms:
    
    @staticmethod
    def fleury(graph):
        """Thuật toán Fleury - Tìm chu trình Euler"""
        # Kiểm tra điều kiện Euler
        odd_degree_vertices = []
        for node in graph.nodes:
            degree = len(graph.get_neighbors(node))
            if degree % 2 == 1:
                odd_degree_vertices.append(node)
        
        if len(odd_degree_vertices) not in [0, 2]:
            return None, "Đồ thị không có đường đi Euler"
        
        # Tạo bản sao đồ thị để có thể xóa cạnh
        temp_graph = copy.deepcopy(graph)
        
        # Chọn điểm bắt đầu
        if len(odd_degree_vertices) == 0:
            start = list(temp_graph.nodes)[0]
        else:
            start = odd_degree_vertices[0]
        
        path = []
        
        def is_bridge(u, v, temp_graph):
            """Kiểm tra cạnh có phải là cầu không"""
            # Đếm số thành phần liên thông trước khi xóa
            def count_reachable(start, graph):
                visited = set()
                stack = [start]
                while stack:
                    node = stack.pop()
                    if node not in visited:
                        visited.add(node)
                        for neighbor, _ in graph.get_neighbors(node):
                            stack.append(neighbor)
                return len(visited)
            
            count_before = count_reachable(u, temp_graph)
            
            # Xóa cạnh tạm thời
            temp_graph.remove_edge(u, v)
            count_after = count_reachable(u, temp_graph)
            
            # Khôi phục cạnh
            weight = 1
            for neighbor, w in graph.get_neighbors(u):
                if neighbor == v:
                    weight = w
                    break
            temp_graph.add_edge(u, v, weight)
            
            return count_after < count_before
        
        current = start
        while True:
            neighbors = temp_graph.get_neighbors(current)
            if not neighbors:
                break
            
            # Tìm cạnh không phải là cầu
            next_node = None
            for neighbor, weight in neighbors:
                if len(neighbors) == 1 or not is_bridge(current, neighbor, temp_graph):
                    next_node = neighbor
                    break
            
            if next_node is None:
                next_node = neighbors[0][0]
            
            path.append((current, next_node))
            temp_graph.remove_edge(current, next_node)
            current = next_node
        
        return path, "Thành công"
    
    @staticmethod
    def hierholzer(graph):
        """Thuật toán Hierholzer - Tìm chu trình Euler hiệu quả hơn"""
        # Kiểm tra điều kiện
        in_degree = defaultdict(int)
        out_degree = defaultdict(int)
        
        for u in graph.adjacency_list:
            for v, _ in graph.adjacency_list[u]:
                out_degree[u] += 1
                in_degree[v] += 1
        
        # Với đồ thị vô hướng
        if not graph.directed:
            odd_vertices = []
            for node in graph.nodes:
                degree = len(graph.get_neighbors(node))
                if degree % 2 == 1:
                    odd_vertices.append(node)
            
            if len(odd_vertices) not in [0, 2]:
                return None, "Không tồn tại chu trình/đường đi Euler"
            
            start = odd_vertices[0] if odd_vertices else list(graph.nodes)[0]
        else:
            # Với đồ thị có hướng
            start = list(graph.nodes)[0]
            for node in graph.nodes:
                if in_degree[node] != out_degree[node]:
                    return None, "Không tồn tại chu trình Euler"
        
        # Tạo bản sao
        temp_adj = defaultdict(list)
        for u in graph.adjacency_list:
            temp_adj[u] = list(graph.adjacency_list[u])
        
        stack = [start]
        path = []
        
        while stack:
            curr = stack[-1]
            if temp_adj[curr]:
                next_node, weight = temp_adj[curr].pop()
                
                # Xóa cạnh ngược nếu vô hướng
                if not graph.directed:
                    temp_adj[next_node] = [(v, w) for v, w in temp_adj[next_node] if v != curr]
                
                stack.append(next_node)
            else:
                path.append(stack.pop())
        
        path.reverse()
        
        # Chuyển thành danh sách cạnh
        edge_path = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
        
        return edge_path, "Thành công"
    
    @staticmethod
    def prim(graph):
        """Thuật toán Prim - Tìm cây khung nhỏ nhất"""
        if graph.directed:
            return None, "Thuật toán Prim chỉ áp dụng cho đồ thị vô hướng"
        
        start = list(graph.nodes)[0]
        mst_edges = []
        visited = {start}
        total_weight = 0
        
        # Danh sách các cạnh có thể chọn
        available_edges = []
        for neighbor, weight in graph.get_neighbors(start):
            available_edges.append((weight, start, neighbor))
        
        while len(visited) < len(graph.nodes) and available_edges:
            # Sắp xếp để chọn cạnh nhỏ nhất
            available_edges.sort()
            
            # Tìm cạnh nhỏ nhất không tạo chu trình
            for i, (weight, u, v) in enumerate(available_edges):
                if v not in visited:
                    # Thêm cạnh vào MST
                    mst_edges.append((u, v, weight))
                    visited.add(v)
                    total_weight += weight
                    
                    # Xóa cạnh đã chọn
                    available_edges.pop(i)
                    
                    # Thêm các cạnh mới
                    for neighbor, w in graph.get_neighbors(v):
                        if neighbor not in visited:
                            available_edges.append((w, v, neighbor))
                    
                    break
        
        return mst_edges, total_weight
    
    @staticmethod
    def kruskal(graph):
        """Thuật toán Kruskal - Tìm cây khung nhỏ nhất"""
        if graph.directed:
            return None, "Thuật toán Kruskal chỉ áp dụng cho đồ thị vô hướng"
        
        # Union-Find
        parent = {node: node for node in graph.nodes}
        rank = {node: 0 for node in graph.nodes}
        
        def find(node):
            if parent[node] != node:
                parent[node] = find(parent[node])
            return parent[node]
        
        def union(u, v):
            root_u = find(u)
            root_v = find(v)
            
            if root_u != root_v:
                if rank[root_u] < rank[root_v]:
                    parent[root_u] = root_v
                elif rank[root_u] > rank[root_v]:
                    parent[root_v] = root_u
                else:
                    parent[root_v] = root_u
                    rank[root_u] += 1
                return True
            return False
        
        # Lấy tất cả các cạnh và sắp xếp
        edges = graph.to_edge_list()
        edges.sort(key=lambda x: x[2])
        
        mst_edges = []
        total_weight = 0
        
        for u, v, weight in edges:
            if union(u, v):
                mst_edges.append((u, v, weight))
                total_weight += weight
                
                if len(mst_edges) == len(graph.nodes) - 1:
                    break
        
        return mst_edges, total_weight
    
    @staticmethod
    def ford_fulkerson(graph, source, sink):
        """Thuật toán Ford-Fulkerson - Tìm luồng cực đại"""
        # Tạo đồ thị thặng dư
        residual = defaultdict(lambda: defaultdict(int))
        
        for u in graph.adjacency_list:
            for v, capacity in graph.adjacency_list[u]:
                residual[u][v] += capacity
        
        def bfs_find_path(source, sink):
            """Tìm đường tăng luồng bằng BFS"""
            visited = {source}
            queue = deque([(source, [source])])
            
            while queue:
                node, path = queue.popleft()
                
                for neighbor in residual[node]:
                    if neighbor not in visited and residual[node][neighbor] > 0:
                        visited.add(neighbor)
                        new_path = path + [neighbor]
                        
                        if neighbor == sink:
                            return new_path
                        
                        queue.append((neighbor, new_path))
            
            return None
        
        max_flow = 0
        flow_paths = []
        
        while True:
            path = bfs_find_path(source, sink)
            
            if path is None:
                break
            
            # Tìm luồng tối thiểu trên đường đi
            flow = float('infinity')
            for i in range(len(path) - 1):
                flow = min(flow, residual[path[i]][path[i + 1]])
            
            # Cập nhật đồ thị thặng dư
            for i in range(len(path) - 1):
                residual[path[i]][path[i + 1]] -= flow
                residual[path[i + 1]][path[i]] += flow
            
            max_flow += flow
            flow_paths.append((path, flow))
        
        return max_flow, flow_paths
