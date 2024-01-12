#!/bin/env python3
import os
from pytree.pytree import Tree
from pytree.pytree import Node

DIR_ICON = "󰉋 "
TREE_ROOT_ICON = "󰙅 "
icons = {
    "default": "󰈔 ",".txt": "󰈙 ", "": "",
    # images
    ".png": "󰺰 ",".jpg": "󰈟 ",".jpeg": "󰈟 ",".webp": "󰈟 ",".svg": "󰕣 ",
    ".bmp": "󰈟 ",".gif": "󱀺 ",".raw": "󱨏 ",
    # video
    ".mp4": "󰈫 ",".avi": "󰈫 ",".mpeg-4": "󰈫 ",".mkv": "󰈫 ",".mov": "󰈫 ",
    ".webm": "󰈫 ",".flv": "󰈫 ",
    # sound
    ".mp3": "󰈣 ",".ogg": "󰈣 ",".wav": "󰈣 ",".m4a": "󰈣 ",".flac": "󱨏 ",
    ".aac": "󰈣 ",
    # Libre Office
    ".odt": "󰈙 ",".ods": "󰱾 ",".odp": "󰈧 ",".odg": "󰈕 ",".odf": "󰠞 ",
    # Microsoft Office
    ".docx": "󰈬 ",".ppt": "󰈧 ",".xlsx": "󰈛 ",
    # code
    ".java": "󰬷 ",".js": "󰌞 ",".c": "󰙱 ",".cpp": "󰙲 ",".cs": "󰌛 ",
    ".go": "󰟓 ",".hs": "󰲒 ",".lhs": "󰲒 ",".html": "󰌝 ",".kt": "󱈙 ",
    ".lua": "󰢱 ",".md": "󰍔 ",".php": "󰌟 ",".py": "󰌠 ",".r": "󰟔 ",".ruby": "󰴭 ",
    ".rc": "󱘗 ",".swift": "󰛥 ",".ts": "󰛦 ",".xml": "󰈮 ",
    # config
    ".json": "󰈮 ",".yml": "󱁻 ",".yaml": "󱁻 ",".conf": "󱁻 ",".toml": "󱁻 ",
    ".rasi": "󱁻 ",".ini": "󱁻 ",
    # 3D
    ".stl": "󰐫 ",".3mf": "󰐫 ",".blend": "󰂫 ",".obj": "󰆦 ",".kmz": "󰆦 ",
    ".fbx": "󰆦 ",".3ds": "󰆦 ",".cad": "󰻫 ",
    # archives
    ".pdf": "󱅷 ",".gpg": "󰈡 ",".gz": "󰛫 ",".zip": "󰛫 ",".7z": "󰛫 ",".tar": "󰀼 ",
    ".deb": "󰀼 ",".rpm": "󰀼 ",
}

def main():
    """Print a tree from the file system."""
    args = os.sys.argv[1:len(os.sys.argv)]

    def get_icon(node:Node) -> str:
        if Node.PRINT_NO_ICON_HINT in node.print_hints:
            return ""
        if node.is_root():
            return TREE_ROOT_ICON
        if len(node.get_children()) > 0:
            return DIR_ICON
        name = node.name.lower()
        extension = name
        if "." in name:
            extension = name[name.rfind("."):len(name)]
        return icons[extension] if extension in icons else icons["default"]

    dir_arg = [c for c in args if not c.startswith("-")]
    if len(dir_arg) == 0:
        dir_arg = [os.getcwd()]
    if len(dir_arg) > 0 and os.path.isdir(dir_arg[0]):
        fs_tree = Tree.fs_tree(dir_arg[0], recursive=("-R" in args), show_dir=True, full_path=("-f" in args))
        root = fs_tree.get_root()
        nodes = root.get_all_inheritance()
        root.name = get_icon(root)+root.name
        for node in nodes:
            node.name = get_icon(node)+node.name
        print(fs_tree)

if __name__ == "__main__":
    main()
