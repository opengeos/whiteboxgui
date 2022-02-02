"""Main module."""

import json
import os
import platform
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


def create_code_cell(code="", where="below"):
    """Creates a code cell in the IPython Notebook.

    Args:
        code (str, optional): Code to fill the new code cell with. Defaults to ''.
        where (str, optional): Where to add the new code cell. It can be one of the following: above, below, at_bottom. Defaults to 'below'.
    """

    import base64
    from IPython.display import Javascript, display

    encoded_code = (base64.b64encode(str.encode(code))).decode()
    display(
        Javascript(
            """
        var code = IPython.notebook.insert_cell_{0}('code');
        code.set_text(atob("{1}"));
    """.format(
                where, encoded_code
            )
        )
    )


def download_from_url(url, out_file_name=None, out_dir=".", unzip=True, verbose=False):
    """Download a file from a URL (e.g., https://github.com/giswqs/whitebox/raw/master/examples/testdata.zip)

    Args:
        url (str): The HTTP URL to download.
        out_file_name (str, optional): The output file name to use. Defaults to None.
        out_dir (str, optional): The output directory to use. Defaults to '.'.
        unzip (bool, optional): Whether to unzip the downloaded file if it is a zip file. Defaults to True.
        verbose (bool, optional): Whether to display or not the output of the function. Defaults to False.
    """
    import tarfile
    import urllib.request
    import zipfile

    in_file_name = os.path.basename(url)

    if out_file_name is None:
        out_file_name = in_file_name
    out_file_path = os.path.join(os.path.abspath(out_dir), out_file_name)

    if verbose:
        print("Downloading {} ...".format(url))

    try:
        urllib.request.urlretrieve(url, out_file_path)
    except Exception:
        raise Exception("The URL is invalid. Please double check the URL.")

    final_path = out_file_path

    if unzip:
        # if it is a zip file
        if ".zip" in out_file_name:
            if verbose:
                print("Unzipping {} ...".format(out_file_name))
            with zipfile.ZipFile(out_file_path, "r") as zip_ref:
                zip_ref.extractall(out_dir)
            final_path = os.path.join(
                os.path.abspath(out_dir), out_file_name.replace(".zip", "")
            )

        # if it is a tar file
        if ".tar" in out_file_name:
            if verbose:
                print("Unzipping {} ...".format(out_file_name))
            with tarfile.open(out_file_path, "r") as tar_ref:
                tar_ref.extractall(out_dir)
            final_path = os.path.join(
                os.path.abspath(out_dir), out_file_name.replace(".tart", "")
            )

    if verbose:
        print("Data downloaded to: {}".format(final_path))

    return


def clone_repo(out_dir=".", unzip=True):
    """Clones the whiteboxgui GitHub repository.

    Args:
        out_dir (str, optional): Output folder for the repo. Defaults to '.'.
        unzip (bool, optional): Whether to unzip the repository. Defaults to True.
    """
    url = "https://github.com/giswqs/whiteboxgui/archive/master.zip"
    filename = "whiteboxgui-master.zip"
    download_from_url(url, out_file_name=filename,
                      out_dir=out_dir, unzip=unzip)


def update_package():
    """Updates the whiteboxgui package from the GitHub repository without the need to use pip or conda.
    In this way, I don't have to keep updating pypi and conda-forge with every minor update of the package.

    """
    import shutil

    try:
        download_dir = os.getcwd()
        clone_repo(out_dir=download_dir)

        pkg_dir = os.path.join(download_dir, "whiteboxgui-master")
        work_dir = os.getcwd()
        os.chdir(pkg_dir)

        if shutil.which("pip") is None:
            cmd = "pip3 install ."
        else:
            cmd = "pip install ."

        os.system(cmd)
        os.chdir(work_dir)
        os.remove(pkg_dir + ".zip")
        shutil.rmtree(pkg_dir)

        print(
            "\nPlease comment out 'whiteboxgui.update_package()' and restart the kernel to take effect:\nJupyter menu -> Kernel -> Restart & Clear Output"
        )

    except Exception as e:
        raise Exception(e)


def get_github_url(tool_name):
    """Get the link to the source code of the tool on GitHub.

    Args:
        tool_name (str): The name of the tool.

    Returns:
        str: The URL to source code.
    """

    url = wbt.view_code(tool_name).strip()
    if "RUST_BACKTRACE" in url:
        url = "https://github.com/jblindsay/whitebox-tools/tree/master/whitebox-tools-app/src/tools"
    return url


def get_book_url(tool_name, category):
    """Get the link to the help documentation of the tool.

    Args:
        tool_name (str): The name of the tool.
        category (str): The category of the tool.

    Returns:
        str: The URL to help documentation.
    """
    prefix = "https://www.whiteboxgeo.com/manual/wbt_book/available_tools"
    if category == "Math and Stats Tools":
        category = "Mathand Stats Tools"
    url = "{}/{}.html#{}".format(
        prefix, category.lower().replace(" ", "_"), to_camelcase(tool_name)
    )

    return url


def search_api_tree(keywords, api_tree, tools_dict):
    """Search the WhiteboxTools API and return functions containing the specified keywords

    Args:
        keywords (str): The keywords to search for.
        api_tree (dict): The dictionary containing the WhiteboxTools API tree.
        tools_dict (dict): The dictionary containing the dict of all tools.

    Returns:
        object: An ipytree object/widget.
    """
    import warnings

    warnings.filterwarnings("ignore")

    sub_tree = Tree()
    for key in api_tree.keys():
        if (keywords.lower() in key.lower()) or (
            keywords.lower() in tools_dict[key]["description"].lower()
        ):
            sub_tree.add_node(api_tree[key])

    return sub_tree


def tool_categories():
    """Generate a dictionary containing the toolbox corresponds to each tool.

    Returns:
        dict: a dictionary containing the toolbox corresponds to each tool.
    """
    category_dict = {}
    tools = wbt.toolbox().split("\n")
    for tool in tools[:-1]:
        name = tool.split(":")[0]
        category = tool.split(":")[1].strip().split("/")[0]
        category_dict[to_snakecase(name)] = category

    return category_dict


def get_tool_params(tool_name):
    """Get parameters for a tool.

    Args:
        tool_name (str): The name of the tool.

    Returns:
        dict: The tool parameters as a dictionary.
    """
    params_dict = {}
    params = json.loads(wbt.tool_parameters(
        tool_name).replace("\n", ""))["parameters"]
    for param in params:
        flags = param["flags"]
        if isinstance(flags, list):
            if flags == ["-i", "--input"]:
                flag = "i"
            else:
                flag = flags[-1].replace("-", "")
        else:
            flag = flags.replace("-", "")
        params_dict[flag] = param
    return params_dict


def get_ext_dict(verbose=True, reset=False):
    """Generate a dictionary containing information for the general extension tools.

    Args:
        verbose (bool, optional): Whether to print out description info. Defaults to True.
        reset (bool, optional): Whether to recreate the json file containing the dictionary. Defaults to False.

    Returns:
        dict: The dictionary containing information for general extension tools.
    """
    import glob
    import shutil
    import urllib
    import zipfile

    os_links = {
        "Windows": "https://www.whiteboxgeo.com/GTE_Windows/GeneralToolsetExtension_win.zip",
        "Darwin": "https://www.whiteboxgeo.com/GTE_Darwin/GeneralToolsetExtension_MacOS_Intel.zip",
        "Linux": "https://www.whiteboxgeo.com/GTE_Linux/GeneralToolsetExtension_linux.zip",
    }

    pkg_dir = os.path.dirname(
        pkg_resources.resource_filename("whitebox", "whitebox.py")
    )

    plugin_dir = os.path.join(pkg_dir, "plugins")
    ext_dir = os.path.join(pkg_dir, "GeneralToolsetExtension")

    url = os_links[platform.system()]
    zip_name = os.path.join(pkg_dir, os.path.basename(url))

    if reset:
        if os.path.exists(zip_name):
            os.remove(zip_name)

    if not os.path.exists(zip_name):
        if verbose:
            print("Downloading General Toolset Extension, please wait ...")
        request = urllib.request.urlopen(url, timeout=500)
        with open(zip_name, "wb") as f:
            f.write(request.read())

        if verbose:
            print("Decompressing {} ...".format(os.path.basename(url)))
        with zipfile.ZipFile(zip_name, "r") as zip_ref:
            zip_ref.extractall(pkg_dir)

        shutil.copytree(ext_dir, plugin_dir, dirs_exist_ok=True)
        shutil.rmtree(ext_dir)

    files = glob.glob(os.path.join(plugin_dir, "*.json"))
    files.sort()

    ext_dict = {}

    for file in files:
        tool_dict = {}
        with open(file, encoding='utf-8') as f:
            tool = json.load(f)
        name = tool["exe"]
        tool_dict["name"] = tool["tool_name"]
        tool_dict["tool_name"] = name
        tool_dict["category"] = tool["toolbox"].split("/")[0]
        tool_dict["label"] = to_label(name)
        tool_dict["description"] = tool["short_description"]
        tool_dict["github"] = get_github_url(name)
        tool_dict["book"] = get_book_url(name, tool["toolbox"])

        params_dict = {}
        params = tool["parameters"]
        for param in params:
            flags = param["flags"]
            if isinstance(flags, list):
                if flags == ["-i", "--input"]:
                    flag = "i"
                else:
                    flag = flags[-1].replace("-", "")
            else:
                flag = flags.replace("-", "")
            params_dict[flag] = param
        tool_dict["parameters"] = params_dict

        ext_dict[tool["tool_name"]] = tool_dict

    return ext_dict


def get_wbt_dict(reset=False):
    """Generate a dictionary containing information for all tools.

    Args:
        reset (bool, optional): Whether to recreate the json file containing the dictionary. Defaults to False.

    Returns:
        dict: The dictionary containing information for all tools.
    """
    pkg_dir = os.path.dirname(
        pkg_resources.resource_filename("whiteboxgui", "whiteboxgui.py")
    )

    wbt_dict_json = os.path.join(pkg_dir, "data/whitebox_tools.json")

    if (not os.path.exists(wbt_dict_json)) or reset:

        wbt_dict = {}
        tools = wbt.list_tools()

        category_dict = tool_categories()

        for tool in tools.keys():
            tool_dict = {}
            name = to_snakecase(tool)
            tool_dict["name"] = to_camelcase(name)
            tool_dict["tool_name"] = name
            tool_dict["category"] = category_dict[name]
            tool_dict["label"] = to_label(name)
            tool_dict["description"] = tools[tool]
            tool_dict["github"] = get_github_url(name)
            tool_dict["book"] = get_book_url(name, category_dict[name])
            tool_dict["parameters"] = get_tool_params(name)

            wbt_dict[to_camelcase(name)] = tool_dict

        wbt_dict.update(get_ext_dict())

        with open(wbt_dict_json, "w", encoding='utf-8') as fp:
            json.dump(wbt_dict, fp, indent=4)
    else:

        with open(wbt_dict_json, encoding='utf-8') as fp:
            wbt_dict = json.load(fp)

    return wbt_dict


def tool_gui(tool_dict, max_width="420px", max_height="600px", sandbox_path=None):
    """Create a GUI for a tool based on the tool dictionary.

    Args:
        tool_dict (dict): The dictionary containing the tool info.
        max_width (str, optional): The max width of the tool dialog.
        max_height (str, optional): The max height of the tool dialog.
        sandbox_path (str, optional): The path to the sandbox directory. Defaults to None.

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
        if items["optional"] == "false" or (not items["optional"]):
            required = "*"
            required_inputs.append(param)
        label = items["name"] + required
        param_type = items["parameter_type"]
        default_value = None

        if items["default_value"] is not None:

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
                var_widget = FileChooser(
                    title=label, sandbox_path=sandbox_path)
            else:
                var_widget = widgets.Text(
                    description=label, style=style, layout=layout)
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
                var_widget = FileChooser(
                    title=label, sandbox_path=sandbox_path)
            else:
                var_widget = FileChooser(
                    title=label, sandbox_path=sandbox_path)
            args[param] = var_widget

            children.append(var_widget)

    run_btn = widgets.Button(
        description="Run", layout=widgets.Layout(width="100px"))
    cancel_btn = widgets.Button(
        description="Cancel", layout=widgets.Layout(width="100px")
    )
    help_btn = widgets.Button(
        description="Help", layout=widgets.Layout(width="100px"))
    import_btn = widgets.Button(
        description="Import",
        tooltip="Import the script to a new cell",
        layout=widgets.Layout(width="98px"),
    )
    tool_output = widgets.Output(
        layout=widgets.Layout(max_height="200px", overflow="scroll")
    )
    children.append(widgets.HBox([run_btn, cancel_btn, help_btn, import_btn]))
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
                elif arg in required_params:
                    required_params.remove(arg)
                if args[arg].selected is not None:
                    if arg == "i":
                        line = f"-{arg}={args[arg].selected}"
                    else:
                        line = f"--{arg}={args[arg].selected}"
            elif isinstance(args[arg], widgets.Text):
                if arg in required_params and len(args[arg].value) == 0:
                    with tool_output:
                        print(f"Please provide inputs for required parameters.")
                        break
                elif arg in required_params:
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

        tool_output.clear_output()
        with tool_output:
            html = widgets.HTML(
                value=f'<a href={tool_dict["book"]} target="_blank">{tool_dict["book"]}</a>'
            )
            display(html)
        webbrowser.open_new_tab(tool_dict["book"])

    def code_button_clicked(b):
        import webbrowser

        with tool_output:
            if "RUST_BACKTRACE" in tool_dict["github"]:
                tool_dict[
                    "github"
                ] = "https://github.com/jblindsay/whitebox-tools/tree/master/whitebox-tools-app/src/tools"
            html = widgets.HTML(
                value=f'<a href={tool_dict["github"]} target="_blank">{tool_dict["github"]}</a>'
            )
            display(html)
        webbrowser.open_new_tab(tool_dict["github"])

    def cancel_btn_clicked(b):
        tool_output.clear_output()

    def import_button_clicked(b):
        tool_output.clear_output()

        required_params = required_inputs.copy()
        args2 = []
        args3 = []

        for arg in args:

            line = ""
            if isinstance(args[arg], FileChooser):
                if arg in required_params and args[arg].selected is None:
                    with tool_output:
                        print(f"Please provide inputs for required parameters.")
                        break
                elif arg in required_params:
                    required_params.remove(arg)
                if arg == "i":
                    line = f"-{arg}={args[arg].selected}"
                else:
                    line = f"--{arg}={args[arg].selected}"
                if args[arg].selected is not None:
                    args3.append(f"{arg}='{args[arg].selected}'")
            elif isinstance(args[arg], widgets.Text):
                if arg in required_params and len(args[arg].value) == 0:
                    with tool_output:
                        print(f"Please provide inputs for required parameters.")
                        break
                elif arg in required_params:
                    required_params.remove(arg)
                if args[arg].value is not None and len(args[arg].value) > 0:
                    line = f"--{arg}={args[arg].value}"
                    args3.append(f"{arg}='{args[arg].value}'")
            elif isinstance(args[arg], widgets.Checkbox):
                line = f"--{arg}={args[arg].value}"
                args3.append(f"{arg}={args[arg].value}")
            args2.append(line)

        if len(required_params) == 0:
            content = []
            content.append("import whitebox")
            content.append("wbt = whitebox.WhiteboxTools()")
            content.append(
                f"wbt.{to_snakecase(tool_dict['name'])}({', '.join(args3)})")
            with tool_output:
                for line in content:
                    print(line)
            create_code_cell("\n".join(content))

    import_btn.on_click(import_button_clicked)
    run_btn.on_click(run_button_clicked)
    help_btn.on_click(help_button_clicked)
    code_btn.on_click(code_button_clicked)
    cancel_btn.on_click(cancel_btn_clicked)

    return tool_widget


def build_toolbox_tree(
    tools_dict, folder_icon="folder", tool_icon="wrench", sandbox_path=None
):
    """Build the toolbox for WhiteboxTools.

    Args:
        tools_dict (dict): A dictionary containing information for all tools.
        folder_icon (str, optional): The font-awesome icon for tool categories. Defaults to "folder".
        tool_icon (str, optional): The font-awesome icon for tools. Defaults to "wrench".
        sandbox_path (str, optional): The path to the sandbox folder. Defaults to None.

    Returns:
        object: An ipywidget representing the toolbox.
    """
    left_widget = widgets.VBox()
    right_widget = widgets.VBox()
    full_widget = widgets.HBox([left_widget, right_widget])

    search_description = f"{len(tools_dict)} tools available. Search tools ..."
    search_box = widgets.Text(placeholder=search_description)
    search_box.layout.width = "270px"

    close_btn = widgets.Button(
        icon="close", layout=widgets.Layout(width="32px"))

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
                sub_tree = search_api_tree(text.value, tree_dict, tools_dict)
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
                tool_ui = tool_gui(
                    tools_dict[tool_name], sandbox_path=sandbox_path)
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


def build_toolbox(
    tools_dict, max_width="1080px", max_height="600px", sandbox_path=None
):
    """Build the toolbox for WhiteboxTools.

    Args:
        tools_dict (dict): A dictionary containing information for all tools.
        max_width (str, optional): The maximum width of the widget.
        max_height (str, optional): The maximum height of the widget.
        sandbox_path (str, optional): The path to the sandbox folder. Defaults to None.

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
        options=options, layout=widgets.Layout(width="170px", height="175px")
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
                display(
                    tool_gui(
                        tool_dict, max_height=max_height, sandbox_path=sandbox_path
                    )
                )

    tools_widget.observe(tool_selected, "value")

    def search_changed(change):
        if change["new"]:
            keyword = change["owner"].value
            if len(keyword) > 0:
                selected_tools = []
                for tool in all_tools:
                    if (
                        keyword.lower() in tool.lower()
                        or keyword.lower() in tools_dict[tool]["description"]
                    ):
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
    left_widget.children = [category_widget,
                            search_widget, label_widget, close_btn]
    center_widget.children = [tools_widget]

    return full_widget


def in_colab_shell():
    """Tests if the code is being executed within Google Colab."""
    import sys

    if "google.colab" in sys.modules:
        return True
    else:
        return False


def show(verbose=True, tree=False, reset=False, sandbox_path=None):
    """Show the toolbox GUI.

    Args:
        verbose (bool, optional): Whether to show progress info when the tool is running. Defaults to True.
        tree (bool, optional): Whether to use the tree mode toolbox built using ipytree rather than ipywidgets. Defaults to False.
        reset (bool, optional): Whether to regenerate the json file with the dictionary containing the information for all tools. Defaults to False.
        sandbox_path (str, optional): The path to the sandbox directory. Defaults to None.
    Returns:
        object: A toolbox GUI.
    """
    tools_dict = get_wbt_dict(reset=reset)

    if verbose:
        wbt.verbose = True
    else:
        wbt.verbose = False

    # if in_colab_shell():
    #     tree = False

    if tree:
        return build_toolbox_tree(tools_dict, sandbox_path=sandbox_path)
    else:
        return build_toolbox(tools_dict, sandbox_path=sandbox_path)


if __name__ == "__main__":

    # Run this script (press F5) to regenerate whitebox_tools.json
    get_ext_dict(reset=True)
    get_wbt_dict(reset=True)
