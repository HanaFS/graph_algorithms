"""
Lớp đồ thị với các phương pháp biểu diễn khác nhau
"""

class Graph:
    def __init__(self, directed=False):
        self.directed = directed
        self.adjacency_list = {}
        self.nodes = set()
        
    def add_node(self, node):
        """Thêm một đỉnh vào đồ thị"""
        if node not in self.adjacency_list:
            self.adjacency_list[node] = []
            self.nodes.add(node)
    
    def add_edge(self, u, v, weight=1):
        """Thêm một cạnh vào đồ thị"""
        self.add_node(u)
        self.add_node(v)
        
        # Thêm cạnh từ u đến v
        self.adjacency_list[u].append((v, weight))
        
        # Nếu đồ thị vô hướng, thêm cạnh ngược lại
        if not self.directed:
            self.adjacency_list[v].append((u, weight))
    
    def remove_edge(self, u, v):
        """Xóa cạnh"""
        if u in self.adjacency_list:
            self.adjacency_list[u] = [(node, weight) for node, weight in self.adjacency_list[u] if node != v]
        
        if not self.directed and v in self.adjacency_list:
            self.adjacency_list[v] = [(node, weight) for node, weight in self.adjacency_list[v] if node != u]
    
    def get_neighbors(self, node):
        """Lấy danh sách láng giềng của một đỉnh"""
        return self.adjacency_list.get(node, [])
    
    def to_adjacency_matrix(self):
        """Chuyển sang ma trận kề"""
        nodes_list = sorted(list(self.nodes))
        n = len(nodes_list)
        matrix = [[0] * n for _ in range(n)]
        
        node_to_index = {node: i for i, node in enumerate(nodes_list)}
        
        for u in self.adjacency_list:
            for v, weight in self.adjacency_list[u]:
                i, j = node_to_index[u], node_to_index[v]
                matrix[i][j] = weight
        
        return nodes_list, matrix
    
    def to_edge_list(self):
        """Chuyển sang danh sách cạnh"""
        edges = []
        seen = set()
        
        for u in self.adjacency_list:
            for v, weight in self.adjacency_list[u]:
                if self.directed:
                    edges.append((u, v, weight))
                else:
                    # Tránh trùng lặp cho đồ thị vô hướng
                    edge = tuple(sorted([u, v])) + (weight,)
                    if edge not in seen:
                        edges.append((u, v, weight))
                        seen.add(edge)
        
        return edges
    
    @staticmethod
    def from_adjacency_matrix(nodes_list, matrix, directed=False):
        """Tạo đồ thị từ ma trận kề"""
        graph = Graph(directed=directed)
        n = len(nodes_list)
        
        for i in range(n):
            for j in range(n):
                if matrix[i][j] != 0:
                    if directed or i <= j:  # Tránh trùng lặp cho vô hướng
                        graph.add_edge(nodes_list[i], nodes_list[j], matrix[i][j])
        
        return graph
    
    @staticmethod
    def from_edge_list(edges, directed=False):
        """Tạo đồ thị từ danh sách cạnh"""
        graph = Graph(directed=directed)
        
        for edge in edges:
            if len(edge) == 3:
                u, v, weight = edge
            else:
                u, v = edge
                weight = 1
            graph.add_edge(u, v, weight)
        
        return graph
    
    def display_representations(self):
        """Hiển thị tất cả các dạng biểu diễn"""
        print("\n" + "="*60)
        print("📊 CÁC PHƯƠNG PHÁP BIỂU DIỄN ĐỒ THỊ")
        print("="*60)
        
        # 1. Adjacency List
        print("\n1️⃣ DANH SÁCH KỀ (Adjacency List):")
        print("-" * 40)
        for node in sorted(self.adjacency_list.keys()):
            neighbors = self.adjacency_list[node]
            if neighbors:
                neighbor_str = ", ".join([f"{v}(w={w})" for v, w in neighbors])
                print(f"  {node} → [{neighbor_str}]")
            else:
                print(f"  {node} → []")
        
        # 2. Adjacency Matrix
        print("\n2️⃣ MA TRẬN KỀ (Adjacency Matrix):")
        print("-" * 40)
        nodes_list, matrix = self.to_adjacency_matrix()
        
        # Header
        print("     ", end="")
        for node in nodes_list:
            print(f"{node:4}", end="")
        print()
        
        # Matrix
        for i, node in enumerate(nodes_list):
            print(f"  {node:2} ", end="")
            for j in range(len(nodes_list)):
                print(f"{matrix[i][j]:4}", end="")
            print()
        
        # 3. Edge List
        print("\n3️⃣ DANH SÁCH CẠNH (Edge List):")
        print("-" * 40)
        edges = self.to_edge_list()
        for i, (u, v, w) in enumerate(edges, 1):
            arrow = "→" if self.directed else "↔"
            print(f"  {i}. {u} {arrow} {v} (trọng số: {w})")
        
        print("="*60 + "\n")
