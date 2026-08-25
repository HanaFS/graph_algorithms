import unittest
import tkinter as tk
from unittest.mock import patch
from ui.graph_ui import GraphApp

class TestGraphAlgorithms(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.patcher_info = patch('tkinter.messagebox.showinfo')
        self.patcher_warn = patch('tkinter.messagebox.showwarning')
        self.patcher_err = patch('tkinter.messagebox.showerror')
        self.patcher_info.start()
        self.patcher_warn.start()
        self.patcher_err.start()

        self.app = GraphApp(self.root)
        self.app.graph = {}

    def tearDown(self):
        self.patcher_info.stop()
        self.patcher_warn.stop()
        self.patcher_err.stop()
        self.root.destroy()

    def test_add_node_and_edge(self):
        self.app.e_node.insert(0, "A")
        self.app._add_node()
        self.assertIn("A", self.app.graph)

        self.app.ef.insert(0, "A")
        self.app.et.insert(0, "B")
        self.app.ew.delete(0, tk.END)
        self.app.ew.insert(0, "5")
        self.app._add_edge()

        self.assertIn("B", self.app.graph)
        self.assertEqual(self.app.graph["A"], [("B", 5)])

    def test_delete_node_and_edge(self):
        self.app.graph = {
            "A": [("B", 1), ("C", 2)],
            "B": [("A", 1)],
            "C": [("A", 2)]
        }
        self.app.directed.set(False)

        # Test delete edge
        self.app.e_del_ef.insert(0, "A")
        self.app.e_del_et.insert(0, "B")
        self.app._delete_edge()
        self.assertNotIn(("B", 1), self.app.graph["A"])
        self.assertNotIn(("A", 1), self.app.graph["B"])

        # Test delete node
        self.app.e_del_node.insert(0, "C")
        self.app._delete_node()
        self.assertNotIn("C", self.app.graph)
        self.assertNotIn(("C", 2), self.app.graph["A"])

    def test_bfs_dfs(self):
        self.app.graph = {
            "A": [("B", 1)],
            "B": [("A", 1), ("C", 1)],
            "C": [("B", 1)]
        }
        self.app.directed.set(False)
        
        bfs_order, _ = self.app._bfs("A")
        dfs_order, _ = self.app._dfs("A")
        
        self.assertEqual(bfs_order, ["A", "B", "C"])
        self.assertEqual(dfs_order, ["A", "B", "C"])

    def test_bipartite(self):
        # Bipartite graph
        self.app.graph = {
            "A": [("X", 1)],
            "B": [("X", 1)],
            "X": [("A", 1), ("B", 1)]
        }
        self.app.directed.set(False)
        is_bip, cmap, _ = self.app._is_bip()
        self.assertTrue(is_bip)
        self.assertNotEqual(cmap["A"], cmap["X"])
        
        # Non-bipartite graph (triangle)
        self.app.graph = {
            "A": [("B", 1), ("C", 1)],
            "B": [("A", 1), ("C", 1)],
            "C": [("A", 1), ("B", 1)]
        }
        is_bip, _, _ = self.app._is_bip()
        self.assertFalse(is_bip)

    def test_shortest_path(self):
        self.app.graph = {
            "S": [("A", 10), ("C", 5)],
            "A": [("B", 1), ("C", 2)],
            "B": [],
            "C": [("A", 3), ("B", 9)]
        }
        self.app.directed.set(True)

        dist, prev = self.app._dijkstra("S")
        self.assertEqual(dist["A"], 8)
        self.assertEqual(self.app._mkpath(prev, "S", "A"), ["S", "C", "A"])

        bf_dist, bf_prev = self.app._bellman_ford("S")
        self.assertEqual(bf_dist["A"], 8)
        self.assertEqual(self.app._mkpath(bf_prev, "S", "A"), ["S", "C", "A"])

if __name__ == "__main__":
    unittest.main()
