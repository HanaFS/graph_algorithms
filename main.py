import tkinter as tk
from ui.graph_ui import GraphApp

def main():
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
