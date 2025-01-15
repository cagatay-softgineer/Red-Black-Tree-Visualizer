import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import random
import os
import asyncio
from typing import Optional, List, Tuple, Dict

# ==============================
#        DATA STRUCTURES
# ==============================
class RedBlackTreeNode:
    def __init__(self, value: Optional[int], color: str = "red") -> None:
        """
        Represents a node in the Red-Black Tree.
        
        :param value: The integer value stored in this node (or None if sentinel).
        :param color: Either 'red' or 'black'.
        """
        self.value: Optional[int] = value
        self.color: str = color
        self.left: Optional['RedBlackTreeNode'] = None
        self.right: Optional['RedBlackTreeNode'] = None
        self.parent: Optional['RedBlackTreeNode'] = None

class RedBlackTree:
    def __init__(self, color_only: bool = False) -> None:
        """
        Red-Black Tree container, with or without color-only mode.
        :param color_only: If True, skip rotations and only recolor when rebalancing.
        """
        self.nil: RedBlackTreeNode = RedBlackTreeNode(None, color="black")  # Sentinel node
        self.root: RedBlackTreeNode = self.nil
        self.steps: List[str] = []
        self.pending_nodes: List[RedBlackTreeNode] = []
        self.color_only: bool = color_only

    # -------------- INSERTION --------------
    def insert(self, value: int) -> None:
        if self.search_value(value) is not None:
            self.steps.append(f"Value {value} already exists, skipping.")
            return
        new_node = RedBlackTreeNode(value)
        new_node.left = self.nil
        new_node.right = self.nil
        self._bst_insert(new_node)
        self.steps.append(f"Inserted node {value} (red).")
        self.pending_nodes.append(new_node)

    def _bst_insert(self, node: RedBlackTreeNode) -> None:
        parent = None
        curr = self.root
        while curr != self.nil:
            parent = curr
            if node.value < curr.value:  # type: ignore
                curr = curr.left
            else:
                curr = curr.right
        node.parent = parent
        if parent is None:
            self.root = node
            self.root.color = "black"
            return
        if node.value < parent.value:  # type: ignore
            parent.left = node
        else:
            parent.right = node

    def rebalance_step(self) -> None:
        if not self.pending_nodes:
            self.steps.append("No pending nodes to rebalance.")
            return
        node = self.pending_nodes.pop(0)
        if self.color_only:
            self.insert_rebalance_color_only(node)
        else:
            self.insert_rebalance_full(node)

    def rebalance_all(self) -> None:
        while self.pending_nodes:
            self.rebalance_step()

    def insert_rebalance_full(self, node: RedBlackTreeNode) -> None:
        """
        Full rebalancing: recoloring + rotations (standard RB insertion fix).
        """
        while node.parent is not None and node.parent.color == "red":
            # Ensure node.parent.parent exists before accessing its properties
            grandparent = node.parent.parent
            if grandparent is None:
                break

            # Case: parent is the left child of grandparent
            if node.parent == grandparent.left:
                uncle = grandparent.right
                if uncle and uncle.color == "red":  # Case 1: Uncle is red
                    self.steps.append("Recoloring parent, uncle, and grandparent.")
                    node.parent.color = "black"
                    uncle.color = "black"
                    grandparent.color = "red"
                    node = grandparent
                else:  # Case 2 & 3: Uncle is black
                    if node == node.parent.right:  # Case 2: Node is a right child
                        self._rotate_left(node.parent)
                        node = node.parent
                    # Case 3: Node is a left child
                    if node.parent:  # Check again in case node.parent is None after rotation
                        node.parent.color = "black"
                    grandparent.color = "red"
                    self._rotate_right(grandparent)

            # Case: parent is the right child of grandparent
            else:
                uncle = grandparent.left
                if uncle and uncle.color == "red":  # Case 1: Uncle is red
                    self.steps.append("Recoloring parent, uncle, and grandparent.")
                    node.parent.color = "black"
                    uncle.color = "black"
                    grandparent.color = "red"
                    node = grandparent
                else:  # Case 2 & 3: Uncle is black
                    if node == node.parent.left:  # Case 2: Node is a left child
                        self._rotate_right(node.parent)
                        node = node.parent
                    # Case 3: Node is a right child
                    if node.parent:  # Check again in case node.parent is None after rotation
                        node.parent.color = "black"
                    grandparent.color = "red"
                    self._rotate_left(grandparent)

        # Ensure the root is always black
        if self.root:  # Extra safety check
            self.root.color = "black"

    def insert_rebalance_color_only(self, node: RedBlackTreeNode) -> None:
        """
        Simplified rebalancing: only recolors if parent & uncle are red, skipping rotations.
        """
        while node != self.root and node.parent is not None and node.parent.color == "red":
            if node.parent.parent is None:
                break
            if node.parent == node.parent.parent.left:  # type: ignore
                uncle = node.parent.parent.right  # type: ignore
            else:
                uncle = node.parent.parent.left  # type: ignore

            if uncle.color == "red":
                self.steps.append("Recoloring parent, uncle, and grandparent (color-only).")
                node.parent.color = "black"
                uncle.color = "black"
                node.parent.parent.color = "red"  # type: ignore
                node = node.parent.parent
            else:
                self.steps.append("Parent red, uncle black -> skipping rotation (color-only).")
                break
        self.root.color = "black"

    # -------------- ROTATIONS --------------
    def _rotate_left(self, node: RedBlackTreeNode) -> None:
        """
        Perform a left rotation around the given node.
        """
        right_child = node.right
        node.right = right_child.left
        if right_child.left != self.nil:
            right_child.left.parent = node
    
        right_child.parent = node.parent
        if node.parent is None:
            self.root = right_child
        elif node == node.parent.left:
            node.parent.left = right_child
        else:
            node.parent.right = right_child
    
        right_child.left = node
        node.parent = right_child
    
        self.steps.append(f"Left rotation at node {node.value}.")

    def _rotate_right(self, node: RedBlackTreeNode) -> None:
        """
        Perform a right rotation around the given node.
        """
        left_child = node.left
        node.left = left_child.right
        if left_child.right != self.nil:
            left_child.right.parent = node

        left_child.parent = node.parent
        if node.parent is None:
            self.root = left_child
        elif node == node.parent.right:
            node.parent.right = left_child
        else:
            node.parent.left = left_child

        left_child.right = node
        node.parent = left_child

        self.steps.append(f"Right rotation at node {node.value}.")

    # -------------- DELETION --------------
    def delete(self, value: int) -> None:
        node_to_delete = self.search_value(value)
        if node_to_delete is None:
            self.steps.append(f"Value {value} not found for deletion.")
            return
        self._delete_node(node_to_delete)

    def _delete_node(self, z: RedBlackTreeNode) -> None:
        y = z
        y_original_color = y.color
        if z.left == self.nil:
            x = z.right
            self._rb_transplant(z, z.right)
        elif z.right == self.nil:
            x = z.left
            self._rb_transplant(z, z.left)
        else:
            y = self._tree_minimum(z.right)
            y_original_color = y.color
            x = y.right
            if y.parent == z:
                x.parent = y
            else:
                self._rb_transplant(y, y.right)
                y.right = z.right
                y.right.parent = y
            self._rb_transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color
        self.steps.append(f"Deleted node {z.value}.")
        if y_original_color == "black":
            self._delete_fixup(x)

    def _tree_minimum(self, node: RedBlackTreeNode) -> RedBlackTreeNode:
        while node.left != self.nil:
            node = node.left
        return node

    def _rb_transplant(self, u: RedBlackTreeNode, v: RedBlackTreeNode) -> None:
        if u.parent is None:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent

    def _delete_fixup(self, x: RedBlackTreeNode) -> None:
        while x != self.root and x.color == "black":
            if x == x.parent.left:  # type: ignore
                sibling = x.parent.right  # type: ignore
                if sibling.color == "red":
                    sibling.color = "black"
                    x.parent.color = "red"  # type: ignore
                    self._rotate_left(x.parent)  # type: ignore
                    sibling = x.parent.right  # type: ignore
                if sibling.left.color == "black" and sibling.right.color == "black":
                    sibling.color = "red"
                    x = x.parent
                else:
                    if sibling.right.color == "black":
                        sibling.left.color = "black"
                        sibling.color = "red"
                        self._rotate_right(sibling)
                        sibling = x.parent.right  # type: ignore
                    sibling.color = x.parent.color
                    x.parent.color = "black"
                    sibling.right.color = "black"
                    self._rotate_left(x.parent)  # type: ignore
                    x = self.root
            else:
                sibling = x.parent.left  # type: ignore
                if sibling.color == "red":
                    sibling.color = "black"
                    x.parent.color = "red"  # type: ignore
                    self._rotate_right(x.parent)  # type: ignore
                    sibling = x.parent.left  # type: ignore
                if sibling.right.color == "black" and sibling.left.color == "black":
                    sibling.color = "red"
                    x = x.parent
                else:
                    if sibling.left.color == "black":
                        sibling.right.color = "black"
                        sibling.color = "red"
                        self._rotate_left(sibling)
                        sibling = x.parent.left  # type: ignore
                    sibling.color = x.parent.color
                    x.parent.color = "black"
                    sibling.left.color = "black"
                    self._rotate_right(x.parent)  # type: ignore
                    x = self.root
        x.color = "black"

    # -------------- SEARCHING --------------
    def search_value(self, value: int) -> Optional[RedBlackTreeNode]:
        curr = self.root
        while curr != self.nil:
            if curr.value == value:
                return curr
            elif value < curr.value:  # type: ignore
                curr = curr.left
            else:
                curr = curr.right
        return None

    # -------------- TRAVERSALS --------------
    def inorder(self, node: Optional[RedBlackTreeNode] = None,
                result: Optional[List[Tuple[int, str]]] = None) -> List[Tuple[int, str]]:
        if result is None:
            result = []
        if node is None:
            node = self.root
        if node != self.nil:
            self.inorder(node.left, result)
            if node.value is not None:
                result.append((node.value, node.color))
            self.inorder(node.right, result)
        return result

    def preorder(self, node: Optional[RedBlackTreeNode] = None,
                 result: Optional[List[Tuple[int, str]]] = None) -> List[Tuple[int, str]]:
        if result is None:
            result = []
        if node is None:
            node = self.root
        if node != self.nil:
            if node.value is not None:
                result.append((node.value, node.color))
            self.preorder(node.left, result)
            self.preorder(node.right, result)
        return result

    def postorder(self, node: Optional[RedBlackTreeNode] = None,
                  result: Optional[List[Tuple[int, str]]] = None) -> List[Tuple[int, str]]:
        if result is None:
            result = []
        if node is None:
            node = self.root
        if node != self.nil:
            self.postorder(node.left, result)
            self.postorder(node.right, result)
            if node.value is not None:
                result.append((node.value, node.color))
        return result

    def clear(self) -> None:
        self.root = self.nil
        self.pending_nodes.clear()
        self.steps.append("Cleared the entire tree.")

# ==============================
#           GUI APP
# ==============================
class RedBlackTreeApp:
    def __init__(self, master: tk.Tk) -> None:
        self.master: tk.Tk = master
        self.master.title("Red-Black Tree: Manual Coloring, Hide NIL, Zoom, Themes, RBC Checks")

        self.color_only_mode: tk.BooleanVar = tk.BooleanVar(value=False)
        self.tree: RedBlackTree = RedBlackTree(color_only=self.color_only_mode.get())

        self.search_path_edges: List[Tuple[RedBlackTreeNode, RedBlackTreeNode]] = []
        self.node_positions: Dict[RedBlackTreeNode, Tuple[int, int, int, int]] = {}
        self.tooltip_label: Optional[tk.Label] = None

        self.hide_nil_var: tk.BooleanVar = tk.BooleanVar(value=False)
        self.zoom_var: tk.DoubleVar = tk.DoubleVar(value=1.0)
        self.theme_var: tk.StringVar = tk.StringVar(value="Classic")
        self.manual_coloring_var: tk.BooleanVar = tk.BooleanVar(value=False)

        self.themes: Dict[str, Dict[str, str]] = {
            "Classic": {
                "bg": "white",
                "red_node": "red",
                "black_node": "black",
                "text_color": "white"
            },
            "Dark": {
                "bg": "#333333",
                "red_node": "#cc4444",
                "black_node": "#555555",
                "text_color": "white"
            },
            "High Contrast": {
                "bg": "white",
                "red_node": "blue",
                "black_node": "black",
                "text_color": "white"
            }
        }
        self.current_theme: Dict[str, str] = self.themes["Classic"]

        # Top Control Frame
        control_frame = tk.Frame(master)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Label(control_frame, text="Value:").pack(side=tk.LEFT)
        self.entry_var = tk.StringVar()  # Create a StringVar to track changes
        self.entry_var.trace("w", self.on_value_change)  # Attach the trace event
        self.value_entry = tk.Entry(control_frame, width=8, textvariable=self.entry_var)
        self.value_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(control_frame, text="Insert", command=self.insert_value).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="Delete", command=self.delete_value).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="Search", command=self.search_value).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="Rebalance Step", command=self.rebalance_step).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="Rebalance All", command=self.rebalance_all).pack(side=tk.LEFT, padx=2)

        tk.Checkbutton(
            control_frame, text="Color-Only Mode",
            variable=self.color_only_mode, command=self.toggle_color_mode
        ).pack(side=tk.LEFT, padx=10)

        tk.Label(control_frame, text="Random Count:").pack(side=tk.LEFT)
        self.random_count_entry = tk.Entry(control_frame, width=5)
        self.random_count_entry.insert(0, "10")
        self.random_count_entry.pack(side=tk.LEFT, padx=2)

        tk.Button(control_frame, text="Generate Random", command=self.generate_random_tree).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Generate Color-Only Random", command=self.generate_random_tree_color_only).pack(side=tk.LEFT, padx=5)

        # Balanced Tree Button
        tk.Button(control_frame, text="Generate Balanced", command=self.on_button_click).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Rebalance Tree", command=self.rebalance).pack(side=tk.LEFT, padx=5)

        # Extra Frame
        extra_frame = tk.Frame(master)
        extra_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Button(extra_frame, text="Clear Tree", command=self.clear_tree).pack(side=tk.LEFT, padx=5)
        tk.Button(extra_frame, text="Save to File", command=self.save_to_file).pack(side=tk.LEFT, padx=5)
        tk.Button(extra_frame, text="Load from File", command=self.load_from_file).pack(side=tk.LEFT, padx=5)

        # Traversal Frame
        traversal_frame = tk.Frame(master)
        traversal_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Button(traversal_frame, text="Inorder", command=self.show_inorder).pack(side=tk.LEFT, padx=3)
        tk.Button(traversal_frame, text="Preorder", command=self.show_preorder).pack(side=tk.LEFT, padx=3)
        tk.Button(traversal_frame, text="Postorder", command=self.show_postorder).pack(side=tk.LEFT, padx=3)

        # Advanced Controls
        adv_frame = tk.Frame(master, bd=2, relief=tk.GROOVE)
        adv_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Checkbutton(
            adv_frame, text="Hide NIL Nodes",
            variable=self.hide_nil_var,
            command=self.draw_tree
        ).pack(side=tk.LEFT, padx=10)

        tk.Label(adv_frame, text="Zoom:").pack(side=tk.LEFT)
        tk.Scale(
            adv_frame, from_=0.5, to=2.0, resolution=0.1,
            orient=tk.HORIZONTAL, variable=self.zoom_var,
            command=lambda _: self.draw_tree()
        ).pack(side=tk.LEFT, padx=5)

        tk.Label(adv_frame, text="Theme:").pack(side=tk.LEFT)
        self.theme_combo = ttk.Combobox(
            adv_frame, textvariable=self.theme_var,
            values=["Classic", "Dark", "High Contrast"],
            state="readonly"
        )
        self.theme_combo.pack(side=tk.LEFT, padx=5)
        self.theme_combo.bind("<<ComboboxSelected>>", self.on_theme_changed)

        # Manual Coloring & Check RB
        manual_frame = tk.Frame(master, bd=2, relief=tk.GROOVE)
        manual_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Checkbutton(
            manual_frame, text="Manual Coloring Mode",
            variable=self.manual_coloring_var,
            command=self._toggle_manual_coloring
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(manual_frame, text="Check RB Properties", command=self.check_rb_properties).pack(side=tk.LEFT, padx=10)

        # Log Frame
        self.log_frame = tk.Frame(master)
        self.log_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.log_label = tk.Label(self.log_frame, text="Steps / Log:")
        self.log_label.pack(side=tk.TOP, anchor=tk.W)

        self.log_text = tk.Text(self.log_frame, height=10, width=80)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.log_scroll = tk.Scrollbar(self.log_frame, command=self.log_text.yview)
        self.log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text['yscrollcommand'] = self.log_scroll.set

        # Canvas
        self.canvas = tk.Canvas(master, bg="white", width=800, height=600)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Bind events
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", self.on_mouse_click)

        self.draw_tree()

    # ============== Generate Balanced ==============
    
    def on_button_click(self):
        # Schedule the coroutine
        asyncio.ensure_future(self.generate_balanced_tree())
        print("Coroutine scheduled.")
    
    async def generate_balanced_tree(self) -> None:
        """
        Build a 'pseudo-balanced' BST from random values in [1..2^10].
        We pick a random seed so we get reproducible but different shapes.
        """
        count_str = self.random_count_entry.get()
        if not count_str.isdigit():
            messagebox.showwarning("Warning", "Please enter a valid integer for balanced count.")
            return
        count = int(count_str)
        if count < 1:
            messagebox.showwarning("Warning", "Balanced count must be >= 1.")
            return

        # 1) Generate a random seed for reproducible shapes
        seed = random.randint(0, 2**31)
        random.seed(seed)

        # 2) Create random values
        values = [random.randint(1, 2**10) for _ in range(count)]
        
        sorted_values = sorted(values)
        
        mid = sorted_values[count//2]

        new_tree = RedBlackTree(color_only=False)
        new_tree.insert(mid)
        sorted_values.remove(mid)
        self.tree = new_tree
    
        for value in sorted_values:
            self.tree.insert(value)
            self.balance_binary_tree()
            self._color_all_red(self.tree.root)
            best_node = self.select_best_node()
            if best_node:
                self.log(f"Best node for rebalancing: {best_node.value}")
                self.tree.insert_rebalance_full(best_node)
                self.tree.rebalance_all()
            #self._color_all_red(new_tree.root)
            self.tree.rebalance_all()
            self.update_log_and_tree(without_delete=True)
            #self.draw_tree()
            await asyncio.sleep(0.1/count)
            
        if not new_tree or new_tree.root == new_tree.nil:
            # If no tree got built, just return
            self.log("No tree built from the provided values.")
            return

        # 4) (Optional) Color the entire new tree red or black
        #    For demonstration, let's color them all red:
        #self._color_all_red(new_tree.root)

        # 5) Replace our current self.tree with this new tree
        self.tree = new_tree
        self.tree.rebalance_all()
        #self.log_text.delete('1.0', tk.END)
        self.log(f"Generated a pseudo-balanced BST of size {count} with seed {seed}.")
        self.draw_tree()

    def _build_balanced_bst(self, tree: Optional[RedBlackTree], value: int) -> Optional[RedBlackTree]:
        """
        Create a brand-new RedBlackTree, insert each value, then do a full rebalancing.
        Return that new tree object. This ensures we get a somewhat 'balanced' shape.
        """

        # Create a fresh RedBlackTree in normal (or color-only) mode
        # If you want it to do normal rebalancing, set color_only=False
        # If you want to skip rotations, set color_only=True
        if tree is None:
            tree = RedBlackTree(color_only=False)

        # Insert each value, then do a rebalance (like rebalancing after each insertion).
        # Alternatively, you can do them all first, then call rebalance_all once at the end.
        tree.insert(value)
        tree.insert_rebalance_full(tree.search_value(value))

        # or do partial rebalancing steps if you like

        return tree

    def _color_all_red(self, node: Optional[RedBlackTreeNode]) -> None:
        """
        Recursively color every real node (not NIL) red. 
        If you want the root to remain black, skip coloring if node is self.tree.root.
        """
        if not node or node == self.tree.nil:
            self.tree.nil.color = "black"
            return
        if node == self.tree.root:
            node.color = "black"
        else:
            node.color = "red"
            
        self._color_all_red(node.left)
        self._color_all_red(node.right)

    # ========== Basic RBC Ops (insert, delete, etc.) ==========

    def toggle_color_mode(self) -> None:
        self.tree.color_only = self.color_only_mode.get()
        self.log(f"Switched to {'COLOR-ONLY' if self.color_only_mode.get() else 'FULL'} rebalancing mode.")

    def insert_value(self) -> None:
        val_str = self.value_entry.get()
        if not val_str.isdigit():
            messagebox.showwarning("Warning", "Please enter a valid integer.")
            return
        val = int(val_str)
        self.tree.insert(val)
        self.update_log_and_tree()

    def delete_value(self) -> None:
        val_str = self.value_entry.get()
        if not val_str.isdigit():
            messagebox.showwarning("Warning", "Please enter a valid integer.")
            return
        val = int(val_str)
        self.tree.delete(val)
        self.update_log_and_tree()

    def search_value(self) -> None:
        val_str = self.value_entry.get()
        if not val_str.isdigit():
            messagebox.showwarning("Warning", "Please enter a valid integer.")
            return
        val = int(val_str)
        self.search_path_edges.clear()
        node = self.tree.root
        prev: Optional[RedBlackTreeNode] = None
        while node != self.tree.nil:
            if node.value == val:
                if prev is not None:
                    self.search_path_edges.append((prev, node))
                self.log(f"Found node with value {val}, color={node.color}.")
                self.draw_tree(highlight=node)
                return
            else:
                if prev is not None:
                    self.search_path_edges.append((prev, node))
                prev = node
                if val < node.value:  # type: ignore
                    node = node.left
                else:
                    node = node.right
        self.log(f"Value {val} not found in the tree.")
        if prev and prev != self.tree.nil:
            self.search_path_edges.append((prev, self.tree.nil))
        self.search_path_edges.clear()
        self.draw_tree()

    def rebalance_step(self) -> None:
        self.tree.rebalance_step()
        self.update_log_and_tree()

    def rebalance_all(self) -> None:
        self.tree.rebalance_all()
        self.update_log_and_tree()

    def generate_random_tree(self) -> None:
        count_str = self.random_count_entry.get()
        if not count_str.isdigit():
            messagebox.showwarning("Warning", "Please enter a valid integer for random count.")
            return
        count = int(count_str)
        if count < 1:
            messagebox.showwarning("Warning", "Random count must be >= 1.")
            return
        self.tree = RedBlackTree(color_only=self.color_only_mode.get())
        self.log_text.delete('1.0', tk.END)
        values = random.sample(range(1, 200), count)
        for v in values:
            self.tree.insert(v)
        self.log(f"Generated random tree with {count} nodes: {values}")
        self.update_log_and_tree()

    def select_best_node(self) -> Optional[RedBlackTreeNode]:
        """
        Select the best node for rebalancing based on:
        - Black-height imbalance.
        - Presence of consecutive red nodes.
        - Depth from the root.
        Returns the node with the highest priority for rebalancing.
        """
        def evaluate_node(node: RedBlackTreeNode) -> int:
            """
            Calculate a score for the node:
            - Higher score = higher priority for rebalancing.
            """
            if node == self.tree.nil:
                return -1

            # Calculate black-height of left and right subtrees
            left_bh = self._calculate_black_height(node.left)
            right_bh = self._calculate_black_height(node.right)
            imbalance = abs(left_bh - right_bh)

            # Check for consecutive red nodes
            red_violation = 0
            if node.color == "red":
                if node.left.color == "red" or node.right.color == "red":
                    red_violation += 10

            # Calculate depth (deeper nodes are penalized)
            depth_penalty = self._calculate_depth(node)

            # Score = black-height imbalance * weight + red violations - depth penalty
            score = (imbalance * 5) + (red_violation) - depth_penalty
            return score

        # Recursive traversal to find the best node
        def traverse_and_find_best(node: RedBlackTreeNode) -> Optional[RedBlackTreeNode]:
            if node == self.tree.nil:
                return None

            # Evaluate current node
            best_node = node

            # Recursively evaluate left and right children
            left_candidate = traverse_and_find_best(node.left)
            right_candidate = traverse_and_find_best(node.right)

            # Compare scores and select the best node
            if left_candidate and evaluate_node(left_candidate) > evaluate_node(best_node):
                best_node = left_candidate
            if right_candidate and evaluate_node(right_candidate) > evaluate_node(best_node):
                best_node = right_candidate

            return best_node

        # Start the traversal from the root
        return traverse_and_find_best(self.tree.root)

    def _calculate_black_height(self, node: RedBlackTreeNode) -> int:
        """
        Calculate the black-height of a node (number of black nodes to a NIL node).
        """
        if node == self.tree.nil:
            return 1
        left_bh = self._calculate_black_height(node.left)
        right_bh = self._calculate_black_height(node.right)
        return max(left_bh, right_bh) + (1 if node.color == "black" else 0)

    def _calculate_depth(self, node: RedBlackTreeNode) -> int:
        """
        Calculate the depth of a node from the root.
        """
        depth = 0
        while node and node != self.tree.root:
            node = node.parent
            depth += 1
        return depth
    
    def generate_random_tree_color_only(self) -> None:
        """
        Build a 'pseudo-balanced' BST from random values in [1..2^10].
        We pick a random seed so we get reproducible but different shapes.
        """
        count_str = self.random_count_entry.get()
        if not count_str.isdigit():
            messagebox.showwarning("Warning", "Please enter a valid integer for balanced count.")
            return
        count = int(count_str)
        if count < 1:
            messagebox.showwarning("Warning", "Balanced count must be >= 1.")
            return

        # 1) Generate a random seed for reproducible shapes
        seed = random.randint(0, 2**31)
        random.seed(seed)

        # 2) Create random values
        values = [random.randint(1, 2**10) for _ in range(count)]
        
        sorted_values = sorted(values)
        
        mid = sorted_values[count//2]

        new_tree = RedBlackTree(color_only=False)
        new_tree.insert(mid)
        sorted_values.remove(mid)
        self.tree = new_tree
    
        for value in sorted_values:
            self.tree.insert(value)
            self.balance_binary_tree()
            self._color_all_red(self.tree.root)
            best_node = self.select_best_node()
            if best_node:
                self.log(f"Best node for rebalancing: {best_node.value}")
                self.tree.insert_rebalance_full(best_node)
                self.tree.rebalance_all()
            #self._color_all_red(new_tree.root)
            self.tree.rebalance_all()
            self.update_log_and_tree(without_delete=True)
            #self.draw_tree()
        
        #new_tree.insert_rebalance_full(new_tree.search_value(random.choice(sorted_values)))
            
        if not new_tree or new_tree.root == new_tree.nil:
            # If no tree got built, just return
            self.log("No tree built from the provided values.")
            return

        # 4) (Optional) Color the entire new tree red or black
        #    For demonstration, let's color them all red:
        #self._color_all_red(new_tree.root)

        # 5) Replace our current self.tree with this new tree
        #self.tree = new_tree

        #self.log_text.delete('1.0', tk.END)
        self.log(f"Generated a pseudo-balanced BST of size {count} with seed {seed}.")
        self.draw_tree()

    def clear_tree(self) -> None:
        self.tree.clear()
        self.update_log_and_tree()

    def save_to_file(self) -> None:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files","*.txt"), ("All Files", "*.*")]
        )
        if not file_path:
            return
        traversal = self.tree.inorder()
        values = [str(val) for (val, _) in traversal if val is not None]
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(" ".join(values))
            self.log(f"Saved {len(values)} nodes to file: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{e}")

    def load_from_file(self) -> None:
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files","*.txt"), ("All Files", "*.*")]
        )
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if not content:
                messagebox.showwarning("Warning", "File is empty.")
                return
            parts = content.split()
            values: List[int] = []
            for p in parts:
                if p.isdigit():
                    values.append(int(p))
                else:
                    self.log(f"Skipping non-integer token '{p}'.")
            self.tree = RedBlackTree(color_only=self.color_only_mode.get())
            self.log_text.delete('1.0', tk.END)
            for v in values:
                self.tree.insert(v)
            self.log(f"Loaded {len(values)} nodes from file: {os.path.basename(file_path)}")
            self.update_log_and_tree()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load file:\n{e}")
        finally:
            self.draw_tree()

    def show_inorder(self) -> None:
        traversal = self.tree.inorder()
        self.log(f"Inorder: {[(val, color) for (val, color) in traversal]}")

    def show_preorder(self) -> None:
        traversal = self.tree.preorder()
        self.log(f"Preorder: {[(val, color) for (val, color) in traversal]}")

    def show_postorder(self) -> None:
        traversal = self.tree.postorder()
        self.log(f"Postorder: {[(val, color) for (val, color) in traversal]}")
    
    def rebalance(self) -> None:
        asyncio.ensure_future(self.rebalance_async())
        print("Coroutine scheduled.")
    
    def _set_nil_links(self, node: Optional[RedBlackTreeNode], parent: Optional[RedBlackTreeNode]) -> None:
       """
       Traverse the tree and set NIL (sentinel) links for all missing children.
       Ensure every node's missing children point to the NIL node.

       :param node: Current node being processed.
       :param parent: Parent of the current node.
       """
       if node is None or node == self.tree.nil:
           return

       node.parent = parent

       # Set left child to NIL if missing
       if node.left is None:
           node.left = self.tree.nil
       else:
           self._set_nil_links(node.left, node)

       # Set right child to NIL if missing
       if node.right is None:
           node.right = self.tree.nil
       else:
           self._set_nil_links(node.right, node)

    
    def balance_binary_tree(self) -> None:
        """
        Balances the entire tree as a simple binary search tree (BST),
        disregarding Red-Black Tree properties.
        """
        # Extract all node values via in-order traversal
        node_values = []
        self._inorder_traversal(self.tree.root, node_values)

        # Rebuild the tree from sorted values
        self.tree.root = self._build_balanced_bst_from_sorted(node_values, 0, len(node_values) - 1)
        self.tree.root.parent = None

        # Set NIL nodes and ensure they point to self.tree.nil
        self._set_nil_links(self.tree.root, None)

        # Log and redraw the tree
        self.log_text.delete("1.0", tk.END)
        self.log("Binary Tree Balanced: Converted to a balanced BST.")
        self.draw_tree()

    def _inorder_traversal(self, node: RedBlackTreeNode, values: List[int]) -> None:
        """
        Perform an in-order traversal and collect node values.
        """
        if node == self.tree.nil:
            return
        self._inorder_traversal(node.left, values)
        values.append(node.value)
        self._inorder_traversal(node.right, values)

    def _build_balanced_bst_from_sorted(self, values: List[int], start: int, end: int) -> Optional[RedBlackTreeNode]:
        """
        Build a balanced binary tree from a sorted list of values.
        """
        if start > end:
            return None

        # Choose the middle element as the root
        mid = (start + end) // 2
        node = RedBlackTreeNode(values[mid], color="black")  # Default to black for a standard BST

        # Recursively build left and right subtrees
        node.left = self._build_balanced_bst_from_sorted(values, start, mid - 1)
        node.right = self._build_balanced_bst_from_sorted(values, mid + 1, end)

        # Return the new root of this subtree
        return node
    
    async def rebalance_async(self) -> None:
        traversal = self.tree.inorder()
        values = [int(val) for (val, _) in traversal if val is not None]
        n = len(values)
        self.log(f"Total value Count : {n}")
        
        sorted_values = sorted(values)
        
        mid = sorted_values[n//2]
        
        new_tree = RedBlackTree(color_only=False)
        new_tree.insert(mid)
        sorted_values.remove(mid)
        self.tree = new_tree
    
        for value in sorted_values:
            self.tree.insert(value)
            self.balance_binary_tree()
            self._color_all_red(self.tree.root)
            best_node = self.select_best_node()
            if best_node:
                self.log(f"Best node for rebalancing: {best_node.value}")
                self.tree.insert_rebalance_full(best_node)
                self.tree.rebalance_all()
            #self._color_all_red(new_tree.root)
            self.tree.rebalance_all()
            self.update_log_and_tree(without_delete=True)
            #self.draw_tree()
            await asyncio.sleep(0.1/n)
        
        
        
        #for value in sorted_values:
        #    best_node = self.select_best_node()
        #    self.tree.insert(value)
        #    if best_node:
        #        self.log(f"Best node for rebalancing: {best_node.value}")
        #        self.tree.insert_rebalance_full(best_node)
        #        self.tree.rebalance_all()
        #    #self.balance_binary_tree()
        #    self.update_log_and_tree(without_delete=True)
        #    #self.draw_tree()
        #    await asyncio.sleep(0.1/n)
        
        #self.balance_binary_tree()
        self.tree.rebalance_all()
        
        self.draw_tree()

    # ========== Manual Coloring & Check RBC ==========
    def _toggle_manual_coloring(self) -> None:
        if self.manual_coloring_var.get():
            self.log("Manual coloring mode ENABLED. Click a node to toggle red/black.")
        else:
            self.log("Manual coloring mode DISABLED.")

    def on_mouse_click(self, event: tk.Event) -> None:
        if not self.manual_coloring_var.get():
            return
        for node, (left, top, right, bottom) in self.node_positions.items():
            if left <= event.x <= right and top <= event.y <= bottom:
                if node == self.tree.nil:
                    return
                old_col = node.color
                node.color = "black" if node.color == "red" else "red"
                self.log(f"Toggled node {node.value} from {old_col} to {node.color}.")
                self.draw_tree()
                return

    def check_rb_properties(self) -> None:
        """
        Validate this Red-Black Tree against the core RB properties:
          1) The root is black (unless the tree is empty).
          2) The NIL sentinel is black.
          3) No red node has red children.
          4) All root->NIL paths have the same black-height.
        Logs errors if found, otherwise logs a success message.
        """

        errors: List[str] = []

        # =========== 1) Root is black (if not empty) ===========
        if self.tree.root != self.tree.nil:
            if self.tree.root.color != "black":
                errors.append(f"Root node {self.tree.root.value} is not black.")

        # =========== 2) NIL sentinel is black =============
        if self.tree.nil.color != "black":
            errors.append("NIL sentinel is not black (unexpected).")

        # =========== 3) No red node has red children ======
        def check_red_children(node: RedBlackTreeNode) -> None:
            # If we hit the sentinel, do nothing
            if node == self.tree.nil:
                return

            # If this node is red, ensure its children are not red
            if node.color == "red":
                if node.left.color == "red":
                    errors.append(
                        f"Red node {node.value} has a red left child ({node.left.value})."
                    )
                if node.right.color == "red":
                    errors.append(
                        f"Red node {node.value} has a red right child ({node.right.value})."
                    )

            # Recur on left and right
            check_red_children(node.left)
            check_red_children(node.right)

        check_red_children(self.tree.root)

        # =========== 4) Consistent black-height ===========
        def black_height(n: RedBlackTreeNode, path_nodes=None) -> int:
            """
            Returns the black-height of the subtree rooted at n, or -1 if mismatched.
            black-height = # of black nodes from this node down to a NIL, inclusive of NIL.

            path_nodes: used for debugging - a list of node values from the root to 'n'.
            """
            if path_nodes is None:
                path_nodes = []

            # Record current node in path for debugging
            curr_info = f"(val={n.value}, color={n.color})" if n != self.tree.nil else "(NIL)"
            path_nodes.append(curr_info)

            if n == self.tree.nil:
                # If we are at the sentinel, that's 1 black node
                path_nodes.append("(end - NIL)")  # for clarity
                # If needed, you can log the entire path: self.log("Path: " + " -> ".join(path_nodes))
                return 1  # Corrected from 0 to 1

            left_bh = black_height(n.left, path_nodes[:])  # Pass a copy for accurate path logging
            right_bh = black_height(n.right, path_nodes[:])

            # if either subtree is invalid
            if left_bh < 0 or right_bh < 0:
                return -1

            if left_bh != right_bh:
                errors.append(
                    f"Black-height mismatch at node {n.value}: "
                    f"path_nodes={path_nodes}, left_bh={left_bh}, right_bh={right_bh}"
                )
                return -1

            add_if_black = 1 if n.color == "black" else 0
            return left_bh + add_if_black

        # Run the black-height check on the root
        tree_bh = black_height(self.tree.root)
        if tree_bh < 0:
            errors.append("Paths do not have the same black-height (see mismatch above).")

        # =========== Final Reporting ===========
        if errors:
            for e in errors:
                self.log(f"RB Check Failed: {e}")
        else:
            self.log("RB Check Passed: All Red-Black properties satisfied.")



    # ========== THEME & DRAWING ==========
    def on_theme_changed(self, event: tk.Event = None) -> None:
        choice = self.theme_var.get()
        if choice in self.themes:
            self.current_theme = self.themes[choice]
        self.draw_tree()

    def update_log_and_tree(self, without_delete: bool = False) -> None:
        if not without_delete:
            self.log_text.delete('1.0', tk.END)
        for step in self.tree.steps:
            self.log_text.insert(tk.END, step + "\n")
        self.draw_tree()
        self.tree.steps.clear()

    def draw_tree(self, highlight: Optional[RedBlackTreeNode] = None) -> None:
        self.canvas.delete("all")
        self.node_positions.clear()
        self.canvas.config(bg=self.current_theme["bg"])

        # If the tree is empty, nothing to draw
        if self.tree.root == self.tree.nil:
            return

        # 1) Compute in-order positions: (x_index, depth)
        positions: Dict[RedBlackTreeNode, Tuple[int, int]] = {}
        self._compute_positions(self.tree.root, 0, 0, positions)

        # 2) Determine min/max x_index to center the tree
        xs = [pos[0] for pos in positions.values()]
        min_x = min(xs)
        max_x = max(xs)
        width_in_order = max_x - min_x

        # 3) Zoom, spacing, margins
        zoom = self.zoom_var.get()
        node_gap_x = int(60 * zoom)  # Horizontal gap between nodes
        node_gap_y = int(80 * zoom)  # Vertical gap between levels
        margin_x = 40
        margin_y = 40

        # 4) Canvas width
        c_width = self.canvas.winfo_width()
        if c_width < 50:
            c_width = 800  # Default width if not yet rendered

        # Total tree width and centering offset
        total_tree_width = (width_in_order if width_in_order > 0 else 1) * node_gap_x
        offset_x_for_centering = (c_width - total_tree_width) / 2

        # 5) Build pixel coordinates for each node
        pixel_coords: Dict[RedBlackTreeNode, Tuple[int, int]] = {}
        for node, (x_index, depth) in positions.items():
            px = offset_x_for_centering + margin_x + (x_index - min_x) * node_gap_x
            py = margin_y + depth * node_gap_y
            pixel_coords[node] = (px, py)

        # 6) Recursive function to draw nodes and annotate NILs with black-height
        def draw_node(node: RedBlackTreeNode, px: int, py: int, current_bh: int) -> None:
            if node == self.tree.nil:
                # Draw NIL node
                r = int(15 * zoom)
                self.canvas.create_oval(px - r, py - r, px + r, py + r, fill="black", outline="white", width=2)
                # Annotate with black-height
                self.canvas.create_text(px, py - r + r*40/15, text=f"BH={current_bh}", fill="black")
                return

            # Draw edges to children
            if node.left and node.left in pixel_coords:
                    child_left_px, child_left_py = pixel_coords[node.left]
                    line_color, line_width = self._edge_color(node, node.left)
                    print(f"Drawing line to left child {node.left.value} with color: {line_color}")  # Debug
                    self.canvas.create_line(px, py, child_left_px, child_left_py, width=line_width, fill=line_color)
            if node.right and node.right in pixel_coords:
                    child_right_px, child_right_py = pixel_coords[node.right]
                    line_color, line_width = self._edge_color(node, node.right)
                    print(f"Drawing line to right child {node.right.value} with color: {line_color}")  # Debug
                    self.canvas.create_line(px, py, child_right_px, child_right_py, width=line_width, fill=line_color)

            # Draw the node
            node_color = self.current_theme["black_node"] if node.color == "black" else self.current_theme["red_node"]
            fill_color = "blue" if node == highlight else node_color

            r = int(15 * zoom)
            self.canvas.create_oval(px - r, py - r, px + r, py + r, fill=fill_color, outline="black", width=2)
            self.canvas.create_text(px, py, text=str(node.value), fill=self.current_theme["text_color"])

            self.node_positions[node] = (px - r, py - r, px + r, py + r)

            # Update current black-height
            new_bh = current_bh + (1 if node.color == "black" else 0)

            # Draw left child
            if node.left and node.left in pixel_coords:
                    draw_node(node.left, pixel_coords[node.left][0], pixel_coords[node.left][1], new_bh)
            else:
                # Draw and annotate NIL left child
                nil_left_px = px - node_gap_x // 2
                nil_left_py = py + node_gap_y
                draw_node(self.tree.nil, nil_left_px, nil_left_py, new_bh)

            # Draw right child
            if node.right and node.right in pixel_coords:
                draw_node(node.right, pixel_coords[node.right][0], pixel_coords[node.right][1], new_bh)
            else:
                # Draw and annotate NIL right child
                nil_right_px = px + node_gap_x // 2
                nil_right_py = py + node_gap_y
                draw_node(self.tree.nil, nil_right_px, nil_right_py, new_bh)

        # Start drawing from the root
        root_px, root_py = pixel_coords[self.tree.root]
        initial_bh = 1 if self.tree.root.color == "black" else 0
        draw_node(self.tree.root, root_px, root_py, initial_bh)

    def on_value_change(self, *args) -> None:
        """
        Callback function triggered when the value in the entry field changes.
        :param args: Additional arguments passed by the trace method (not used here).
        """
        self.search_path_edges.clear()
        self.draw_tree()

    def _edge_color(self, parent: RedBlackTreeNode, child: RedBlackTreeNode) -> str:
        for edge in self.search_path_edges:
            if edge == (parent, child):
                return "purple", 5
        return "black", 2

    def _compute_positions(self, node: RedBlackTreeNode, depth: int, x_index: int, positions: dict) -> int:
        if node == self.tree.nil:
            print(f"Skipping NIL node at depth {depth}, x_index {x_index}.")
            return x_index

        # Traverse left subtree
        x_index = self._compute_positions(node.left, depth + 1, x_index, positions)

        # Assign the current node's position
        positions[node] = (x_index, depth)
        print(f"Added node {node.value} to positions at depth {depth}, x_index {x_index}.")
        x_index += 1  # Increment the x_index

        # Traverse right subtree
        x_index = self._compute_positions(node.right, depth + 1, x_index, positions)

        return x_index

    def on_mouse_move(self, event: tk.Event) -> None:
        found_node: Optional[RedBlackTreeNode] = None
        for node, (left, top, right, bottom) in self.node_positions.items():
            if left <= event.x <= right and top <= event.y <= bottom:
                found_node = node
                break
        if found_node and found_node != self.tree.nil:
            tip = f"Value: {found_node.value}\nColor: {found_node.color}"
            self.show_tooltip(event.x + 10, event.y + 10, tip)
        else:
            self.hide_tooltip()

    def show_tooltip(self, x: int, y: int, text: str) -> None:
        if self.tooltip_label is None:
            self.tooltip_label = tk.Label(self.canvas, text=text,
                                          background="lightyellow", borderwidth=1, relief="solid")
            self.tooltip_label.place(x=x, y=y)
        else:
            self.tooltip_label.config(text=text)
            self.tooltip_label.place(x=x, y=y)

    def hide_tooltip(self) -> None:
        if self.tooltip_label:
            self.tooltip_label.destroy()
            self.tooltip_label = None

    def log(self, message: str) -> None:
        self.tree.steps.append(message)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

# ==============================
#         Poll asyncio
# ==============================

def poll_asyncio():
    try:
        loop = asyncio.get_event_loop()
        # Run any pending tasks briefly
        loop.stop()
        loop.run_forever()
    except RuntimeError:
        pass
    # Re-schedule
    root.after(50, poll_asyncio)

# ==============================
#           MAIN
# ==============================

if __name__ == "__main__":
    root = tk.Tk()
    app = RedBlackTreeApp(root)
    
    # Start polling the asyncio loop
    root.after(50, poll_asyncio)
    
    root.mainloop()

