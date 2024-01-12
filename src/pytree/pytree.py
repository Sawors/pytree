#!/bin/env python3
# depends on natsort
# $ pip3 install natsort
from natsort import natsorted
import os


###############################################################################

PATH_SEPARATOR = "/"
SPACER_SIZE = 3

class Colors:
    RESET = "\033[0m"
    LINE_COLOR = RESET
    PARENT_COLOR = "\033[93m\033[01m"
    ROOT_COLOR = "\033[32m"
    DATA_COLOR = "\033[96m"
    ENDPOINT_COLOR = "\033[94m"

class LineChar:
    HORIZONTAL = "─"
    VERTICAL = "│"
    HORIZONTAL_END = ">"
    VERTICAL_END = "╰"
    INTERSECTION = "├"

###############################################################################


class NodeError(Exception):
    pass

class TreeNodeError(NodeError):
    pass
    
class UnknownPathError(Exception):
    pass
class Node:

    PRINT_HIDE_HINT = "HIDE"
    PRINT_IGNORE_HINT = "IGNORE"
    PRINT_NO_ICON_HINT = "NO_ICON"
    PRINT_COLOR_HINT = "COLOR="
    
    def __init__(self, name:str, data=None, _parent=None):
        self.name = name
        self.data = data
        self._children = []
        self._parent = _parent
        self.print_hints = []

    def __str__(self):
        return(f"{self.name}{f': {self.data}' if not self.data == None else ''}")

    def __repr__(self):
        return(f"[{self.name}]:"+"{"+f"data={self.data}, parent={self._parent.name if not self._parent == None else 'None'}, children={self._children}"+"}")

    # returns a snapshot of the node's children
    def get_children(self) -> list:
        return self._children.copy()

    def is_endpoint(self) -> bool:
        return not self._parent == None and len(self._children) == 0

    def is_root(self) -> bool:
        return self._parent == None
    
    def add(self, *nodes, ignore_duplicates=False, replace_duplicates=False, replace_parent=False):
        for node in nodes:
            if node == self._parent:
                raise NodeError("A node cannot be the parent of its own parent.")
            if node == self:
                raise NodeError("A node cannot be its own child.")
            duplicate = any(node.name == n.name for n in self._children)
            if duplicate and ignore_duplicates:
                continue
            if duplicate and not replace_duplicates:
                raise NodeError(f"Another node with the name \"{node.name}\" already exists!")
            if not replace_parent and not node._parent == None:
                raise NodeError(f"The node {node} already has a parent!")
            self._children.append(node)
            node._parent = self

    def remove(self, node):
        self._children = filter(lambda n: n==node,self._children)

    def remove_by_name(self, name:str):
        self._children = filter(lambda n: n.name == node.nameself._children)
        
    def get_branch(self, reverse=False, include_self=True) -> list:
        # The path is naturally from self to root.
        path = [self] if include_self else []
        last_node = self
        while not last_node.is_root():
            parent = last_node._parent
            path.append(parent)
            last_node = parent
        # the path is naturally reversed, so we need to reverse it to
        # output the expected result.
        if not reverse:
            path.reverse()
        return path
        
    
    def get_path(self) -> str:
        branch = self.get_branch(reverse=False,include_self=True)
        path = "/"
        for index, node in enumerate(branch[1:len(branch)]):
            path += f"{node.name}{PATH_SEPARATOR if index < len(branch)-2 else ''}"
        return path

    def get_all_inheritance(self) -> list:
        # goes down all the way to the latest sub-children and
        # returns a list containing all child and sub-children.

        # THIS MIGHT BE VERY SLOW!
        flattened = []
        process_queue = self._children
        while len(process_queue) > 0:
            next_processes = []
            for child in process_queue:
                if child in flattened:
                    raise NodeError(f"Looping nodes detected, the node {child} is referenced from later in its inheritance.")
                flattened.append(child)
                sub = child._children
                if not sub == None and len(sub) > 0:
                    next_processes += sub
            process_queue = next_processes
            
        return flattened
    
    def get_tree_display(self, color=True) -> str:
        c1 = Colors.LINE_COLOR if color else ""
        c2 = Colors.DATA_COLOR if color else ""
        r = Colors.RESET if color else ""
        data_display = f'{c1}:{r} {c2}{self.data}{r}' if not self.data == None else ''
        color = Colors.ENDPOINT_COLOR
        if self.is_root():
            color = Colors.ROOT_COLOR
        elif not self.is_endpoint():
            color = Colors.PARENT_COLOR
        for hint in self.print_hints:
            if hint.startswith(Node.PRINT_COLOR_HINT):
                color = hint.replace(Node.PRINT_COLOR_HINT, "")
                break
        name_display = f"{color}{self.name}{Colors.RESET}" if color else self.name
        
        return name_display+data_display
    
    def _get_branches_print(branches:list, depth=0, prepend="", color=True) -> str:
        content = ""
        child_list = natsorted(filter(lambda c:not Node.PRINT_IGNORE_HINT in c.print_hints, branches), key=lambda c: c.name)
        for index, child in enumerate(child_list):
            sub = child._children
            last_key = index == len(child_list)-1
            
            mid_draw = f"{LineChar.INTERSECTION}{LineChar.HORIZONTAL}{LineChar.HORIZONTAL_END}"
            end_draw = f"{LineChar.VERTICAL_END}{LineChar.HORIZONTAL}{LineChar.HORIZONTAL_END}"
            branch_char = end_draw if last_key else mid_draw
            if color:
                branch_char= f"{Colors.LINE_COLOR}{branch_char}{Colors.RESET}"
                    
            line = f"{prepend}{branch_char} {child.get_tree_display()}"
            
            content += line+"\n"

            vertical_draw = f"{Colors.LINE_COLOR}{LineChar.VERTICAL}{Colors.RESET}" if color else "{LineChar.VERTICAL}"
            if len(sub) > 0:
                content += Node._get_branches_print(
                    sub,
                    depth=depth+1,
                    prepend=prepend+((SPACER_SIZE+1)*" " if last_key else vertical_draw+(SPACER_SIZE*" ") ),
            )
        return content
    
    def get_tree_print(self, depth=0, prepend="", color=True) -> str:
        return f"{self.get_tree_display()}\n{Node._get_branches_print(self._children, color=color)}"

class InsertMode:
    MAKE_CHILD=0
    MAKE_PARENT=1
    REPLACE=2

class Tree:
    def __init__(self, root, cache_all=True):
        self._root = root
        self._path_cache = {self._root.get_path(): self._root}

        if cache_all:
            for child in self._root.get_all_inheritance():
                self._path_cache[child.get_path()] = child

    def get_formatted_path(self, path:str) -> str:
        formated_path = path
        if formated_path.startswith(self._root.name):
            formated_path.replace(self._root.name, "")
        if not formated_path.startswith(PATH_SEPARATOR):
            formated_path = PATH_SEPARATOR + formated_path
        return formated_path
    
    def get_root(self) -> Node:
        return self._root 

    def add_to_cache(self, node:Node):
        self._path_cache[node.get_path()] = node

    def is_cached(self, path:str) -> bool:
        return path in self._path_cache.keys() and not self._path_cache[path] == None
        
    def from_cache(self, path:str) -> Node:
        if self.is_cached(path):
            return self._path_cache[path]
        else:
            return None

    def is_looping(self, node:Node, branch=None) -> bool:
        if branch == None: 
            branch = node.get_branch(include_self=True)
        base_children = node._children
        for nd in branch:
            if nd in base_children: 
                return True
        return False
        

    def get_node(self, path:str, unknown_raise_exception=True) -> Node:
        formated_path = self.get_formatted_path(path)
        
        if self.is_cached(path):
            return self.from_cache(path)
        
        # to handle escaped PATH_SEPARATOR in path names
        sep_replace = "aEzpmXxKd3OevOcMtVUjmFvEhmyqZm80"
        tree = [t.replace(sep_replace,f"\{PATH_SEPARATOR}") for t in formated_path.replace(f"\{PATH_SEPARATOR}",sep_replace).split(PATH_SEPARATOR)]

        node = None
        
        last_node = self._root
        for i in range(1,len(tree)):
            next_node = None
            path_step = tree[i]
            for child in last_node._children:
                if child.name == path_step:
                    next_node = child
                    break
            if next_node == None:
                break
            last_node = next_node
            
        if unknown_raise_exception and node == None:
            raise UnknownPathError("Node {path} does not exist!")
        if not node == None:
            self._path_cache[formated_path] = node
        return node
        
    def remove(self, path:str):
        node = self.get_node(path, unknown_raise_exception=False)
        if node == None: return
        parent = node._parent
        if parent == None:
            if node == self._root:
                self._root = Node("")
                self._path_cache = {PATH_SEPARATOR,self._root}
        else:
            parent.remove(node)
            del self._path_cache[path]

    # the behaviour is made to be the most predictable possible :
    # the path is the path to the parent, and the node is inserted
    # as a child if the parent is an endpoint, otherwise the insert_mode
    # resolution method is applied.
    def insert(self, path:str, node:Node, create_missing_nodes=False, cache_node=False, insert_mode=InsertMode.MAKE_CHILD):
        formated_path = self.get_formatted_path(path)
        # so here target is the parent node in which our node will be inserted
        target = self.get_node(formated_path, unknown_raise_exception=False)
        
        if target == None:
            # parent does not exist
            if create_missing_nodes:
                tree = formated_path.split(PATH_SEPARATOR)
                last_node = self._root
                for i in range(1,len(tree)):
                    next_node = None
                    path_step = tree[i]
                    for child in last_node._children:
                        if child.name == path_step:
                            next_node = child
                            continue
                    if next_node == None:
                        next_node = Node(path_step)
                        if cache_node: self.add_to_cache(next_node)
                        last_node.add(next_node)
                    last_node = next_node
                target = last_node
            else:
                raise UnknownPathError(f"Node {path} does not exist! Other nodes cannot be appended.")
        # parent already existed or was created, inserting..
        target_branch = target.get_branch(include_self=True)
        if self.is_looping(node,branch=target_branch):
            raise TreeNodeError(f"The node {node} introduces a loop when inserted at {path}")
        
        match insert_mode:
            case InsertMode.MAKE_CHILD:
                target.add(node)
            case InsertMode.MAKE_PARENT:
                old_parent = target._parent
                old_parent.remove(target)
                node.add(target)
                old_parent.add(node)
            case InsertMode.REPLACE:
                old_parent = target._parent
                old_children = target._children
                node.add(old_children)
                old_parent.remove(target)
                old_parent.add(node)
                    
        if cache_node: self.add_to_cache(node)
    
    # this time create a new node at the path. The name of the new node
    # is the last part of the path. For instance insert("/home/test/file")
    # is equivalent to insert("/home/test", Node("file")).
    # An error will be raised if the node already exists.
    def insert_from_path(self, path:str, create_missing_nodes=False, cache_node=False, insert_mode=InsertMode.MAKE_CHILD) -> Node:
        tree = path.split(PATH_SEPARATOR)
        node = Node(tree[len(tree)-1])
        sub_path = PATH_SEPARATOR.join(tree[0:len(tree)-1])
        self.insert(sub_path, node, create_missing_nodes=create_missing_nodes, cache_node=cache_node, insert_mode=insert_mode)
        return node
    
    def __str__(self):
        return self._root.get_tree_print()
    
    # static
    def build_tree(paths:list, cache_all=True):
        tree = Tree()
        for path in paths:
            formated_path = tree.get_formatted_path(path)
            try:
                tree.insert_from_path(formated_path, create_missing_nodes=True, cache_node=True)
            except TreeNodeError:
                pass
        return Tree()
    
    # create a tree from file system
    def fs_tree(path:str, full_path=False, recursive=True, show_dir=False):
        if not os.path.isdir(path):
            raise OSError("the path {path} is not a directory")
        tree_name = path if full_path else path[path.rfind(PATH_SEPARATOR)+1:len(path)]
        tree = Tree(Node(tree_name))
        if recursive:
            for root, dirs, files in os.walk(path, topdown=False,followlinks=False):
                for file in files:
                    file_target = f"{root}/{file}".replace(path,"")
                    tree.insert_from_path(file_target, create_missing_nodes=True, cache_node=True)
        else:
            for file in os.listdir(path):
                file_target = f"/{file}".replace(path,"")
                node = tree.insert_from_path(file_target, create_missing_nodes=True, cache_node=True)
                if show_dir and os.path.isdir(f"{path}/{file}"):
                    display_node = Node("")
                    display_node.print_hints.append(Node.PRINT_IGNORE_HINT)
                    node.add(display_node)
        return tree
    
if __name__ == "__main__":
    args = os.sys.argv[1:len(os.sys.argv)]

    for index, arg in enumerate(args):
        pass
    
    icons = {
        "default": "󰈔 ",".txt": "󰈙 ", "": "",
        # images
        ".png": "󰺰 ",".jpg": "󰈟 ",".jpeg": "󰈟 ",".webp": "󰈟 ",".svg": "󰕣 ",".bmp": "󰈟 ",".gif": "󱀺 ",".raw": "󱨏 ",
        # video
        ".mp4": "󰈫 ",".avi": "󰈫 ",".mpeg-4": "󰈫 ",".mkv": "󰈫 ",".mov": "󰈫 ",".webm": "󰈫 ",".flv": "󰈫 ",
        # sound
        ".mp3": "󰈣 ",".ogg": "󰈣 ",".wav": "󰈣 ",".m4a": "󰈣 ",".flac": "󱨏 ",".aac": "󰈣 ",
        # Libre Office
        ".odt": "󰈙 ",".ods": "󰱾 ",".odp": "󰈧 ",".odg": "󰈕 ",".odf": "󰠞 ",
        # Microsoft Office
        ".docx": "󰈬 ",".ppt": "󰈧 ",".xlsx": "󰈛 ",
        # code
        ".java": "󰬷 ",".js": "󰌞 ",".c": "󰙱 ",".cpp": "󰙲 ",".cs": "󰌛 ",".go": "󰟓 ",".hs": "󰲒 ",".lhs": "󰲒 ",".html": "󰌝 ",".kt": "󱈙 ",".lua": "󰢱 ",".md": "󰍔 ",".php": "󰌟 ",".py": "󰌠 ",".r": "󰟔 ",".ruby": "󰴭 ",".rc": "󱘗 ",".swift": "󰛥 ",".ts": "󰛦 ",".xml": "󰈮 ",
        # config
        ".json": "󰈮 ",".yml": "󱁻 ",".yaml": "󱁻 ",".conf": "󱁻 ",".toml": "󱁻 ",".rasi": "󱁻 ",".ini": "󱁻 ",
        # 3D
        ".stl": "󰐫 ",".3mf": "󰐫 ",".blend": "󰂫 ",".obj": "󰆦 ",".kmz": "󰆦 ",".fbx": "󰆦 ",".3ds": "󰆦 ",".cad": "󰻫 ",
        # archives
        ".pdf": "󱅷 ",".gpg": "󰈡 ",".gz": "󰛫 ",".zip": "󰛫 ",".7z": "󰛫 ",".tar": "󰀼 ",".deb": "󰀼 ",".rpm": "󰀼 ",
    }
    def get_icon(node:Node) -> str:
        if Node.PRINT_NO_ICON_HINT in node.print_hints: return ""
        if node.is_root():
            return "󰙅 "
        if len(node._children) > 0:
            return "󰉋 "
        name = node.name.lower()
        extension = name
        if "." in name:
            extension = name[name.rfind("."):len(name)]
        return icons[extension] if extension in icons else icons["default"]
    
    dir_arg = [c for c in args if not c.startswith("-")]
    if len(dir_arg) > 0 and os.path.isdir(dir_arg[0]):
        fs_tree = Tree.fs_tree(dir_arg[0], recursive=("-R" in args), show_dir=True)
        root = fs_tree.get_root()
        nodes = root.get_all_inheritance()
        root.name = get_icon(root)+root.name
        for node in nodes:
           node.name = get_icon(node)+node.name 
        print(fs_tree)
