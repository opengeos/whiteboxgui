"""Main module."""

import ast
import json
import os
import pkg_resources
import re
import whitebox
import ipywidgets as widgets
from ipyfilechooser import FileChooser
from ipytree import Tree, Node
from IPython.display import display


wbt = whitebox.WhiteboxTools()


def to_camelcase(name):
    """Convert snake_case name to CamelCase name.

    Args:
        name (str): The name of the tool.

    Returns:
        str: The CamelCase name of the tool.
    """

    return "".join(x.title() for x in name.split("_"))


def to_label(name):
    """Convert snake_case name to Title case label.

    Args:
        name (str): The name of the tool.

    Returns:
        str: The Title case name of the tool.
    """
    return " ".join(x.title() for x in name.split("_"))


def to_snakecase(name):
    """Convert CamelCase name to snake_case name.

    Args:
        name (str): The name of the tool.

    Returns:
        str: The snakecase name of the tool.
    """
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def get_tool_params(tool_name):
    """Get parameters for a tool.

    Args:
        tool_name (str): The name of the tool.

    Returns:
        dict: The tool parameters as a dictionary.
    """

    out_str = wbt.tool_parameters(tool_name)
    start_index = out_str.index("[") + 1
    end_index = len(out_str.strip()) - 2
    params = out_str[start_index:end_index]

    sub_params = params.split('{"name"')
    param_list = []

    for param in sub_params:
        param = param.strip()
        if len(param) > 0:
            item = '"name"' + param
            item = item[: item.rfind("}")].strip()
            param_list.append(item)

    params_dict = {}
    for item in param_list:
        param_dict = {}
        item = item.replace(" (optional)", "")
        index_name = item.find("name")
        index_flags = item.find("flags")
        index_description = item.find("description")
        index_parameter_type = item.find("parameter_type")
        index_default_value = item.find("default_value")
        index_optional = item.find("optional")

        name = item[index_name - 1 : index_flags - 2].replace('"name":', "")
        name = name.replace('"', "")
        param_dict["name"] = name

        flags = item[index_flags - 1 : index_description - 2].replace('"flags":', "")

        if ('"-i"' in flags) and ("--inputs" in flags):
            flags = "inputs"
        elif (
            ('"-i"' in flags)
            and ("--input" in flags)
            and ("--dem" in flags)
            and (tool_name.lower() != "sink")
        ):
            flags = "dem"
        elif ('"-i"' in flags) and ("--input" in flags):
            flags = "i"
        elif flags.count("--") == 1:
            flags = flags.split("--")[1][:-2]
        elif flags.count("--") == 2:
            flags = flags.split("--")[2][:-2]
        else:
            flags = flags.split("-")[1][:-2]

        param_dict["flags"] = flags

        desc = item[index_description - 1 : index_parameter_type - 2].replace(
            '"description":', ""
        )
        desc = desc.replace('"', "")
        param_dict["description"] = desc

        param_type = item[index_parameter_type - 1 : index_default_value - 2].replace(
            '"parameter_type":', ""
        )
        param_type = ast.literal_eval(param_type)
        param_dict["parameter_type"] = param_type

        default_value = item[index_default_value - 1 : index_optional - 2].replace(
            '"default_value":', ""
        )
        param_dict["default_value"] = default_value

        optional = item[index_optional - 1 :].replace('"optional":', "")
        param_dict["optional"] = optional

        params_dict[flags] = param_dict

    return params_dict


def get_github_url(tool_name, category):
    """Get the link to the source code of the tool on GitHub.

    Args:
        tool_name (str): The name of the tool.
        category (str): The category of the tool.

    Returns:
        str: The URL to source code.
    """

    url = wbt.view_code(tool_name).strip()
    return url


def get_book_url(tool_name, category):
    """Get the link to the help documentation of the tool.

    Args:
        tool_name (str): The name of the tool.
        category (str): The category of the tool.

    Returns:
        str: The URL to help documentation.
    """
    prefix = "https://jblindsay.github.io/wbt_book/available_tools"
    url = "{}/{}.html#{}".format(prefix, category, tool_name)
    return url


def search_api_tree(keywords, api_tree):
    """Search Earth Engine API and return functions containing the specified keywords

    Args:
        keywords (str): The keywords to search for.
        api_tree (dict): The dictionary containing the Earth Engine API tree.

    Returns:
        object: An ipytree object/widget.
    """
    import warnings

    warnings.filterwarnings("ignore")

    sub_tree = Tree()

    for key in api_tree.keys():
        if keywords.lower() in key.lower():
            sub_tree.add_node(api_tree[key])

    return sub_tree


def get_wbt_dict(reset=False):
    """Generate a dictionary containing information for all tools.

    Args:
        reset (bool, optional): Whether to recreate the json file containing the dictionary. Defaults to False.

    Returns:
        dict: The dictionary containing information for all tools.
    """
    wbt_dir = os.path.dirname(
        pkg_resources.resource_filename("whitebox", "whitebox_tools.py")
    )

    wbt_py = os.path.join(wbt_dir, "whitebox_tools.py")

    wbt_dict = os.path.join(wbt_dir, "whitebox_tools.json")

    toolboxes = {
        "# Data Tools #": "Data Tools",
        "# GIS Analysis #": "GIS Analysis",
        "# Geomorphometric Analysis #": "Geomorphometric Analysis",
        "# Hydrological Analysis #": "Hydrological Analysis",
        "# Image Processing Tools #": "Image Processing Tools",
        "# LiDAR Tools #": "LiDAR Tools",
        "# Math and Stats Tools #": "Math and Stats Tools",
        "# Stream Network Analysis #": "Stream Network Analysis",
    }

    github_cls = {
        "Data Tools": "data_tools",
        "GIS Analysis": "gis_analysis",
        "Geomorphometric Analysis": "terrain_analysis",
        "Hydrological Analysis": "hydro_analysis",
        "Image Processing Tools": "image_analysis",
        "LiDAR Tools": "lidar_analysis",
        "Math and Stats Tools": "math_stat_analysis",
        "Stream Network Analysis": "stream_network_analysis",
    }

    book_cls = {
        "Data Tools": "data_tools",
        "GIS Analysis": "gis_analysis",
        "Geomorphometric Analysis": "geomorphometric_analysis",
        "Hydrological Analysis": "hydrological_analysis",
        "Image Processing Tools": "image_processing_tools",
        "LiDAR Tools": "lidar_tools",
        "Math and Stats Tools": "mathand_stats_tools",
        "Stream Network Analysis": "stream_network_analysis",
    }

    tools_dict = {}
    if (not os.path.exists(wbt_dict)) or reset:

        tool_labels = []
        category = ""

        tool_index = 1

        with open(wbt_py) as f:
            lines = f.readlines()

            for index, line in enumerate(lines):
                if index > 500:
                    line = line.strip()

                    if line in toolboxes:
                        category = toolboxes[line]

                    if line.startswith("def"):
                        func_title = line.replace("def", "", 1).strip().split("(")[0]
                        func_name = to_camelcase(func_title)

                        func_label = to_label(func_title)
                        tool_labels.append(func_label)
                        func_desc = lines[index + 1].replace('"""', "").strip()

                        func_dict = {}
                        func_dict["name"] = func_name
                        func_dict["Name"] = to_camelcase(func_name)
                        func_dict["category"] = category
                        func_dict["label"] = func_label
                        func_dict["description"] = func_desc

                        github_url = get_github_url(func_name, github_cls[category])
                        book_url = get_book_url(func_name, book_cls[category])

                        func_dict["github"] = github_url
                        func_dict["book"] = book_url

                        tool_index = tool_index + 1
                        func_params = get_tool_params(func_name)
                        func_dict["parameters"] = func_params
                        tools_dict[func_name] = func_dict

        with open(wbt_dict, "w") as fp:
            json.dump(tools_dict, fp)
    else:

        with open(wbt_dict) as fp:
            tools_dict = json.load(fp)

    return tools_dict


def tool_gui(tool_dict, max_width="420px", max_height="600px"):
    """Create a GUI for a tool based on the tool dictionary.

    Args:
        tool_dict (dict): The dictionary containing the tool info.
        max_width (str, optional): The max width of the tool dialog.
        max_height (str, optional): The max height of the tool dialog.

    Returns:
        object: An ipywidget object representing the tool interface.
    """
    tool_widget = widgets.VBox(
        layout=widgets.Layout(max_width=max_width, max_height=max_height)
    )
    children = []
    args = {}
    required_inputs = []
    style = {"description_width": "initial"}
    max_width = str(int(max_width.replace("px", "")) - 10) + "px"

    header_width = str(int(max_width.replace("px", "")) - 104) + "px"
    header = widgets.Label(
        value=f'Current Tool: {tool_dict["name"]}',
        style=style,
        layout=widgets.Layout(width=header_width),
    )
    code_btn = widgets.Button(
        description="View Code", layout=widgets.Layout(width="100px")
    )

    children.append(widgets.HBox([header, code_btn]))

    desc = widgets.Textarea(
        value=f'Description: {tool_dict["description"]}',
        layout=widgets.Layout(width="410px", max_width=max_width),
        disabled=True,
    )
    children.append(desc)

    params = tool_dict["parameters"]
    for param in params:
        items = params[param]
        required = ""
        if items["optional"] == "false":
            required = "*"
            required_inputs.append(param)
        label = items["name"] + required
        param_type = items["parameter_type"]
        default_value = None

        if (items["default_value"] != "null") and (len(items["default_value"]) > 0):
            if "false" in items["default_value"]:
                default_value = False
            elif "true" in items["default_value"]:
                default_value = True
            else:
                default_value = items["default_value"].replace('"', "")

        layout = widgets.Layout(width="500px", max_width=max_width)

        if isinstance(param_type, str):
            # display(data_types[param_type])

            if param_type == "Boolean":
                var_widget = widgets.Checkbox(
                    description=label, style=style, layout=layout, value=default_value
                )
            elif param_type in [
                "Directory",
                "ExistingFile",
                "ExistingFileOrFloat",
                "FileList",
                "NewFile",
            ]:
                var_widget = FileChooser(title=label)
            else:
                var_widget = widgets.Text(description=label, style=style, layout=layout)
                if default_value is not None:
                    var_widget.value = str(default_value)

            args[param] = var_widget

            children.append(var_widget)
        elif isinstance(param_type, dict):

            if "OptionList" in param_type:
                var_widget = widgets.Dropdown(
                    options=param_type["OptionList"],
                    description=label,
                    style=style,
                    layout=layout,
                )
            elif list(param_type.keys())[0] in [
                "Directory",
                "ExistingFile",
                "ExistingFileOrFloat",
                "FileList",
                "NewFile",
            ]:
                var_widget = FileChooser(title=label)
            else:
                var_widget = FileChooser(title=label)
            args[param] = var_widget

            children.append(var_widget)

    run_btn = widgets.Button(description="Run", layout=widgets.Layout(width="100px"))
    cancel_btn = widgets.Button(
        description="Cancel", layout=widgets.Layout(width="100px")
    )
    help_btn = widgets.Button(description="Help", layout=widgets.Layout(width="100px"))
    tool_output = widgets.Output(layout=widgets.Layout(max_height="200px"))
    children.append(widgets.HBox([run_btn, cancel_btn, help_btn]))
    children.append(tool_output)
    tool_widget.children = children

    def run_button_clicked(b):
        tool_output.clear_output()

        required_params = required_inputs.copy()
        args2 = []
        for arg in args:

            line = ""
            if isinstance(args[arg], FileChooser):
                if arg in required_params and args[arg].selected is None:
                    with tool_output:
                        print(f"Please provide inputs for required parameters.")
                        break
                else:
                    required_params.remove(arg)
                if arg == "i":
                    line = f"-{arg}={args[arg].selected}"
                else:
                    line = f"--{arg}={args[arg].selected}"
            elif isinstance(args[arg], widgets.Text):
                if arg in required_params and len(args[arg].value) == 0:
                    with tool_output:
                        print(f"Please provide inputs for required parameters.")
                        break
                else:
                    required_params.remove(arg)
                if args[arg].value is not None and len(args[arg].value) > 0:
                    line = f"--{arg}={args[arg].value}"
            elif isinstance(args[arg], widgets.Checkbox):
                line = f"--{arg}={args[arg].value}"
            args2.append(line)

        if len(required_params) == 0:
            with tool_output:
                wbt.run_tool(tool_dict["name"], args2)

    def help_button_clicked(b):
        import webbrowser

        webbrowser.open_new_tab(tool_dict["book"])

    def code_button_clicked(b):
        import webbrowser

        webbrowser.open_new_tab(tool_dict["github"])

    def cancel_btn_clicked(b):
        tool_output.clear_output()

    run_btn.on_click(run_button_clicked)
    help_btn.on_click(help_button_clicked)
    code_btn.on_click(code_button_clicked)
    cancel_btn.on_click(cancel_btn_clicked)

    return tool_widget


def build_toolbox_tree(tools_dict, folder_icon="folder", tool_icon="wrench"):
    """Build the toolbox for WhiteboxTools.

    Args:
        tools_dict (dict): A dictionary containing information for all tools.
        folder_icon (str, optional): The font-awesome icon for tool categories. Defaults to "folder".
        tool_icon (str, optional): The font-awesome icon for tools. Defaults to "wrench".

    Returns:
        object: An ipywidget representing the toolbox.
    """
    left_widget = widgets.VBox()
    right_widget = widgets.VBox()
    full_widget = widgets.HBox([left_widget, right_widget])

    search_description = f"{len(tools_dict)} tools available. Search tools ..."
    search_box = widgets.Text(placeholder=search_description)
    search_box.layout.width = "270px"

    close_btn = widgets.Button(icon="close", layout=widgets.Layout(width="32px"))

    def close_btn_clicked(b):
        full_widget.close()

    close_btn.on_click(close_btn_clicked)

    tree_widget = widgets.Output()
    tree_widget.layout.max_width = "310px"
    tree_widget.overflow = "auto"

    left_widget.children = [widgets.HBox([search_box, close_btn]), tree_widget]
    output = widgets.Output(layout=widgets.Layout(max_width="760px"))
    right_widget.children = [output]

    tree = Tree(multiple_selection=False)
    tree_dict = {}

    def search_box_callback(text):

        with tree_widget:
            if text.value == "":
                print("Loading...")
                tree_widget.clear_output(wait=True)
                display(tree)
            else:
                tree_widget.clear_output()
                print("Searching...")
                tree_widget.clear_output(wait=True)
                sub_tree = search_api_tree(text.value, tree_dict)
                display(sub_tree)

    search_box.on_submit(search_box_callback)

    root_name = "WhiteboxTools"
    root_node = Node(root_name)
    tree.add_node(root_node)

    categories = {}

    def handle_tool_clicked(event):
        if event["new"]:
            cur_node = event["owner"]
            tool_name = cur_node.name
            with output:
                output.clear_output()
                tool_ui = tool_gui(tools_dict[tool_name])
                display(tool_ui)

    for key in tools_dict.keys():
        category = tools_dict[key]["category"]
        if category not in categories.keys():
            category_node = Node(category, icon=folder_icon, opened=False)
            root_node.add_node(category_node)
            categories[category] = category_node
            tool_node = Node(key, icon=tool_icon)
            category_node.add_node(tool_node)
            tree_dict[key] = tool_node
            tool_node.observe(handle_tool_clicked, "selected")
        else:
            category_node = categories[category]
            tool_node = Node(key, icon=tool_icon)
            category_node.add_node(tool_node)
            tree_dict[key] = tool_node
            tool_node.observe(handle_tool_clicked, "selected")

    with tree_widget:
        tree_widget.clear_output()
        display(tree)

    return full_widget


def build_toolbox(tools_dict, max_width="1080px", max_height="600px"):
    """Build the toolbox for WhiteboxTools.

    Args:
        tools_dict (dict): A dictionary containing information for all tools.
        max_width (str, optional): The maximum width of the widget.
        max_height (str, optional): The maximum height of the widget.

    Returns:
        object: An ipywidget representing the toolbox.
    """
    left_widget = widgets.VBox(layout=widgets.Layout(min_width="175px"))
    center_widget = widgets.VBox(
        layout=widgets.Layout(min_width="200px", max_width="200px")
    )
    right_widget = widgets.Output(
        layout=widgets.Layout(width="630px", max_height=max_height)
    )
    full_widget = widgets.HBox(
        [left_widget, center_widget, right_widget],
        layout=widgets.Layout(max_width=max_width, max_height=max_height),
    )

    search_widget = widgets.Text(
        placeholder="Search tools ...", layout=widgets.Layout(width="170px")
    )
    label_widget = widgets.Label(layout=widgets.Layout(width="170px"))
    label_widget.value = f"{len(tools_dict)} Available Tools"
    close_btn = widgets.Button(
        description="Close Toolbox", icon="close", layout=widgets.Layout(width="170px")
    )

    categories = {}
    categories["All Tools"] = []
    for key in tools_dict.keys():
        category = tools_dict[key]["category"]
        if category not in categories.keys():
            categories[category] = []
        categories[category].append(tools_dict[key]["name"])
        categories["All Tools"].append(tools_dict[key]["name"])

    options = list(categories.keys())
    all_tools = categories["All Tools"]
    all_tools.sort()
    category_widget = widgets.Select(
        options=options, layout=widgets.Layout(width="170px", height="165px")
    )
    tools_widget = widgets.Select(
        options=[], layout=widgets.Layout(width="195px", height="400px")
    )

    def category_selected(change):
        if change["new"]:
            selected = change["owner"].value
            options = categories[selected]
            options.sort()
            tools_widget.options = options
            label_widget.value = f"{len(options)} Available Tools"

    category_widget.observe(category_selected, "value")

    def tool_selected(change):
        if change["new"]:
            selected = change["owner"].value
            tool_dict = tools_dict[selected]
            with right_widget:
                right_widget.clear_output()
                display(tool_gui(tool_dict, max_height=max_height))

    tools_widget.observe(tool_selected, "value")

    def search_changed(change):
        if change["new"]:
            keyword = change["owner"].value
            if len(keyword) > 0:
                selected_tools = []
                for tool in all_tools:
                    if keyword.lower() in tool.lower():
                        selected_tools.append(tool)
                if len(selected_tools) > 0:
                    tools_widget.options = selected_tools
                label_widget.value = f"{len(selected_tools)} Available Tools"
        else:
            tools_widget.options = all_tools
            label_widget.value = f"{len(tools_dict)} Available Tools"

    search_widget.observe(search_changed, "value")

    def close_btn_clicked(b):
        full_widget.close()

    close_btn.on_click(close_btn_clicked)

    category_widget.value = list(categories.keys())[0]
    tools_widget.options = all_tools
    left_widget.children = [category_widget, search_widget, label_widget, close_btn]
    center_widget.children = [tools_widget]

    return full_widget


def in_colab_shell():
    """Tests if the code is being executed within Google Colab."""
    import sys

    if "google.colab" in sys.modules:
        return True
    else:
        return False


def show(verbose=True, tree=False, reset=False):
    """Show the toolbox GUI.

    Args:
        verbose (bool, optional): Whether to show progress info when the tool is running. Defaults to True.
        tree (bool, optional): Whether to use the tree mode toolbox built using ipytree rather than ipywidgets. Defaults to False.
        reset (bool, optional): Whether to regenerate the json file with the dictionary containing the information for all tools. Defaults to False.

    Returns:
        object: A toolbox GUI.
    """
    tools_dict = get_wbt_dict(reset=reset)

    if verbose:
        wbt.verbose = True
    else:
        wbt.verbose = False

    if in_colab_shell():
        tree = False

    if tree:
        return build_toolbox_tree(tools_dict)
    else:
        return build_toolbox(tools_dict)


# if __name__ == "__main__":
#     show(reset=False)
