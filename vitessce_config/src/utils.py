import matplotlib.pyplot as plt
import numpy as np

def hex_to_rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i+2], 16) for i in (0, 2, 4)]

def cmap_colors(cmap_name, n):
    cmap = plt.get_cmap(cmap_name)
    indices = np.linspace(0, 1, n)
    return [[int(c * 255) for c in cmap(i)[:3]] for i in indices]

def make_obs_set_colors(specs):
    """
    specs: dict of obs_set_name -> color definition:
      - dict {value: "#hex"}          custom palette
      - (cmap_name, [values])         discrete colormap
    """
    result = []
    for obs_set_name, spec in specs.items():
        if isinstance(spec, dict):
            for val, color in spec.items(): # traverse; TODO: make function recursive;
                result.append(
                    {
                        "path": [obs_set_name, str(val)], 
                        "color": hex_to_rgb(color)
                    }
                )
        else:
            cmap_name, values = spec
            for val, color in zip(values, cmap_colors(cmap_name, len(values))):
                result.append({"path": [obs_set_name, str(val)], "color": color})
    return result

def make_obs_set_selection(specs):
    """Initial selection: all leaf paths for every obs set."""
    result = []
    for obs_set_name, spec in specs.items():
        if isinstance(spec, dict):
            values = list(spec.keys())
        else:
            _, values = spec
        for val in values:
            result.append([obs_set_name, str(val)])
    return result

def make_nested_obs_set_colors(root_name, color_tree):
    result = []
    for parent, spec in color_tree.items():
        if isinstance(spec, str):
            # Already a leaf — 2-level path: [root, parent]
            result.append({"path": [root_name, parent], "color": hex_to_rgb(spec)})
        elif isinstance(spec, dict):
            if "_color" in spec:
                result.append({"path": [root_name, parent], "color": hex_to_rgb(spec["_color"])})
            for child, color in spec.items():
                if child == "_color":
                    continue
                result.append({"path": [root_name, parent, child], "color": hex_to_rgb(color)})
    return result

def make_nested_obs_set_selection(root_name, color_tree):
    result = []
    for parent, spec in color_tree.items():
        if isinstance(spec, str):
            result.append([root_name, parent])
        elif isinstance(spec, dict):
            children = [k for k in spec if k != "_color"]
            if children:
                for child in children:
                    result.append([root_name, parent, child])
            else:
                result.append([root_name, parent])
    return result

def make_all_obs_set_colors(specs):
    """
    specs: {obs_set_name: color_def} where color_def is one of:
      - (cmap_name, [values])
      - nested dict of arbitrary depth
        leaves are "#hex"
        optional "_color" gives color for that node
    """
    result = []

    def walk(node, path_prefix):
        if isinstance(node, str):
            # Leaf color
            result.append({
                "path": path_prefix,
                "color": hex_to_rgb(node),
            })
            return

        if isinstance(node, dict):
            # Optional node-level color
            if "_color" in node:
                result.append({
                    "path": path_prefix,
                    "color": hex_to_rgb(node["_color"]),
                })

            for key, value in node.items():
                if key == "_color":
                    continue
                walk(value, path_prefix + [key])

    for obs_set_name, spec in specs.items():
        if isinstance(spec, tuple):
            cmap_name, values = spec
            colors = cmap_colors(cmap_name, len(values))
            for val, color in zip(values, colors):
                result.append({
                    "path": [obs_set_name, str(val)],
                    "color": color,
                })
        elif isinstance(spec, dict):
            walk(spec, [obs_set_name])

    return result

def make_all_obs_set_selection(specs, include=None):
    """
    specs: same structure as make_all_obs_set_colors
    include: optional set/list of obs_set_names to include
    """
    result = []

    def walk(node, path_prefix):
        if isinstance(node, str):
            # Leaf node
            result.append(path_prefix)
            return

        if isinstance(node, dict):
            children = [k for k in node if k != "_color"]

            # If node has no real children (only _color), treat as leaf
            if not children:
                result.append(path_prefix)
                return

            for key in children:
                walk(node[key], path_prefix + [key])

    for obs_set_name, spec in specs.items():
        if include is not None and obs_set_name not in include:
            continue

        if isinstance(spec, tuple):
            _, values = spec
            for val in values:
                result.append([obs_set_name, str(val)])

        elif isinstance(spec, dict):
            walk(spec, [obs_set_name])

    return result
