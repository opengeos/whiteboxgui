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
    """
    Convert snake_case name to CamelCase name
    """
    return "".join(x.title() for x in name.split("_"))


def to_label(name):
    """
    Convert snake_case name to Title case label
    """
    return " ".join(x.title() for x in name.split("_"))


def to_snakecase(name):
    """
    Convert CamelCase name to snake_case name
    """
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def get_tool_params(tool_name):
    """
    Convert tool parameters output string to a dictionary
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

        # if tool_name == 'Divide':
        #     print("start debugging")

    return params_dict


def get_param_widget(param):

    data_type = widgets.Text()  # default data type
    data_filter = "[]"  # https://goo.gl/EaVNzg
    filter_type = '""'
    multi_value = False
    dependency_field = ""

    data_types = {
        "Boolean": widgets.Checkbox(),
        "Integer": widgets.IntText(),
        "Float": widgets.FloatText(),
        "String": widgets.Text(),
        "StringOrNumber": widgets.Text(),
        "Directory": FileChooser(),
        "Raster": FileChooser(),
        "Csv": FileChooser(),
        "Text": FileChooser(),
        "Html": FileChooser(),
        "Lidar": FileChooser(),
        "Vector": FileChooser(),
        "RasterAndVector": FileChooser(),
        "ExistingFileOrFloat": FileChooser(),
    }

    vector_filters = {
        "Point": '["Point"]',
        "Line": '["Polyline"]',
        "Polygon": '["Polygon"]',
        "LineOrPolygon": '["Polyline", "Polygon"]',
        "Any": "[]",
    }

    if type(param) is str and param in data_types.keys():
        data_type = data_types[param]
    else:
        for item in param:
            if item == "FileList":
                multi_value = True
            elif item == "OptionList":
                filter_type = '"ValueList"'
                data_filter = param[item]

            if param[item] == "Csv":
                data_filter = '["csv"]'
            elif param[item] == "Lidar":
                data_filter = '["las", "zip"]'
            elif param[item] == "Html":
                data_filter = '["html"]'

            if type(param[item]) is str:
                data_type = data_types[param[item]]
            elif type(param[item]) is dict:
                sub_item = param[item]
                for sub_sub_item in sub_item:
                    data_type = data_types[sub_sub_item]
                    if data_type == '"DEShapefile"':
                        data_filter = vector_filters[sub_item[sub_sub_item]]
            elif item == "VectorAttributeField":
                data_type = widgets.Text()
                dependency_field = param[item][1].replace("--", "")
            else:
                data_type = widgets.Text()

            if param == {"ExistingFileOrFloat": "Raster"}:
                data_type = FileChooser()

    return data_type


def get_data_type(param):
    """
    Convert WhiteboxTools data types to ArcGIS data types
    """
    data_type = '"GPString"'  # default data type
    data_filter = "[]"  # https://goo.gl/EaVNzg
    filter_type = '""'
    multi_value = False
    dependency_field = ""

    # ArcGIS data types: https://goo.gl/95JtFu
    data_types = {
        "Boolean": '"GPBoolean"',
        "Integer": '"GPLong"',
        "Float": '"GPDouble"',
        "String": '"GPString"',
        "StringOrNumber": '["GPString", "GPDouble"]',
        "Directory": '"DEFolder"',
        "Raster": '"DERasterDataset"',
        "Csv": '"DEFile"',
        "Text": '"DEFile"',
        "Html": '"DEFile"',
        "Lidar": '"DEFile"',
        "Vector": '"DEShapefile"',
        "RasterAndVector": '["DERasterDataset", "DEShapefile"]',
        "ExistingFileOrFloat": '["DERasterDataset", "GPDouble"]',
    }

    vector_filters = {
        "Point": '["Point"]',
        "Line": '["Polyline"]',
        "Polygon": '["Polygon"]',
        "LineOrPolygon": '["Polyline", "Polygon"]',
        "Any": "[]",
    }

    if type(param) is str:
        data_type = data_types[param]

    else:
        for item in param:
            if item == "FileList":
                multi_value = True
            elif item == "OptionList":
                filter_type = '"ValueList"'
                data_filter = param[item]

            if param[item] == "Csv":
                data_filter = '["csv"]'
            elif param[item] == "Lidar":
                data_filter = '["las", "zip"]'
            elif param[item] == "Html":
                data_filter = '["html"]'

            if type(param[item]) is str:
                data_type = data_types[param[item]]
            elif type(param[item]) is dict:
                sub_item = param[item]
                for sub_sub_item in sub_item:
                    data_type = data_types[sub_sub_item]
                    if data_type == '"DEShapefile"':
                        data_filter = vector_filters[sub_item[sub_sub_item]]
            elif item == "VectorAttributeField":
                data_type = '"Field"'
                dependency_field = param[item][1].replace("--", "")
            else:
                data_type = '"GPString"'

            if param == {"ExistingFileOrFloat": "Raster"}:
                data_type = '["DERasterDataset", "GPDouble"]'

    ret = {}
    ret["data_type"] = data_type
    ret["data_filter"] = data_filter
    ret["filter_type"] = filter_type
    ret["multi_value"] = multi_value
    ret["dependency_field"] = dependency_field

    return ret


def get_github_url(tool_name, category):
    """
    Generate source code link on Github
    """
    # prefix = "https://github.com/jblindsay/whitebox-tools/blob/master/src/tools"
    url = wbt.view_code(tool_name).strip()
    # url = "{}/{}/{}.rs".format(prefix, category, tool_name)
    return url


def get_github_tag(tool_name, category):
    """
    Get GitHub HTML tag
    """
    # prefix = "https://github.com/jblindsay/whitebox-tools/blob/master/src/tools"
    # url = "{}/{}/{}.rs".format(prefix, category, tool_name)
    url = wbt.view_code(tool_name).strip()
    html_tag = "<a href='{}' target='_blank'>GitHub</a>".format(url)
    return html_tag


def get_book_url(tool_name, category):
    """
    Get link to WhiteboxTools User Mannual
    """
    prefix = "https://jblindsay.github.io/wbt_book/available_tools"
    url = "{}/{}.html#{}".format(prefix, category, tool_name)
    return url


def get_book_tag(tool_name, category):
    """
    Get User Manual HTML tag
    """
    prefix = "https://jblindsay.github.io/wbt_book/available_tools"
    url = "{}/{}.html#{}".format(prefix, category, tool_name)
    html_tag = "<a href='{}' target='_blank'>WhiteboxTools User Manual</a>".format(url)
    return html_tag


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


def get_wbt_dict(reset=False):

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

                        github_tag = get_github_tag(func_title, github_cls[category])
                        book_tag = get_book_tag(func_name, book_cls[category])
                        full_desc = "{} View detailed help documentation on {} and source code on {}.".format(
                            func_desc, book_tag, github_tag
                        )

                        func_dict = {}
                        func_dict["name"] = func_name
                        func_dict["Name"] = to_camelcase(func_name)
                        func_dict["category"] = category
                        func_dict["label"] = func_label
                        func_dict["description"] = full_desc

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


def tool_gui(tool_dict):

    # tool_widget = widgets.Output()
    tool_widget = widgets.VBox()
    children = []
    args = {}

    header = widgets.Label(value=f'Current Tool: {tool_dict["name"]}')
    children.append(header)

    params = tool_dict["parameters"]
    for param in params:
        # print(param)
        items = params[param]
        required = ""   
        if items["optional"] == "false":
            required = "*"
        label = items["name"] + required
        param_type = items["parameter_type"]
        # print(param_type)
        default_value = None
        # if items["default_value"] == "null":
        #     items["default_value"] = None
        if (items["default_value"] != "null") and (len(items["default_value"]) > 0):
            if "false" in items["default_value"]:
                default_value = False
            elif "true" in items["default_value"]:
                default_value = True
            else:
                default_value = items["default_value"].replace('"', '')
        # print(default_value)
        style={"description_width": "initial"}
        layout = layout=widgets.Layout(width='500px')

        # data_types = {
        #     "Boolean": widgets.Checkbox(description=label, style=style),
        #     "Integer": widgets.IntText(description=label, style=style),
        #     "Float": widgets.FloatText(description=label, style=style),
        #     "String": widgets.Text(description=label, style=style),
        #     "StringOrNumber": widgets.Text(description=label, style=style),
        #     "Directory": FileChooser(title=label),
        #     "Raster": FileChooser(title=label),
        #     "Csv": FileChooser(title=label),
        #     "Text": FileChooser(title=label),
        #     "Html": FileChooser(title=label),
        #     "Lidar": FileChooser(title=label),
        #     "Vector": FileChooser(title=label),
        #     "RasterAndVector": FileChooser(title=label),
        #     "ExistingFileOrFloat": FileChooser(title=label),
        #     "ExistingFile": FileChooser(title=label),

        # }
        # print(label)
        # print(param_type)
        if isinstance(param_type, str):
            # display(data_types[param_type])
            
            if param_type == "Boolean":
                var_widget = widgets.Checkbox(description=label, style=style, layout=layout, value=default_value)
            # elif param_type == "Integer":
            #     var_widget = widgets.IntText(description=label, style=style, value=None)
            #     if default_value is not None:
            #         var_widget.value = int(default_value.replace('"', ''))
            # elif param_type == "Float":
            #     var_widget = widgets.FloatText(description=label, style=style, value=None)
            #     if default_value is not None:
            #         var_widget.value = float(default_value.replace('"', ''))     
            elif param_type in ["Directory", "Raster", "Csv", "Text", "Html", "Lidar", "Vector", "RasterAndVector", "ExistingFileOrFloat", "ExistingFile"]:
                var_widget = FileChooser(title=label)          
            else:
                var_widget = widgets.Text(description=label, style=style, layout=layout)
                if default_value is not None:
                    var_widget.value = str(default_value)                       

            args[param] = var_widget

            children.append(var_widget)
        else:
            var_widget = FileChooser(title=label)    
            args[param] = var_widget

            # if default_value is not None:
            #     var_widget.value = str(default_value)                
            # # print(param_type)
            # for item in param_type:
            #     if item == "FileList":
            #         multi_value = True
            #     # elif item == "OptionList":
            #     #     filter_type = '"ValueList"'
            #     #     # data_filter = param_type[item]

            #     # if param_type[item] == "Csv":
            #     #     data_filter = '["csv"]'
            #     # elif param_type[item] == "Lidar":
            #     #     data_filter = '["las", "zip"]'
            #     # elif param_type[item] == "Html":
            #     #     data_filter = '["html"]'

            #     if type(param_type[item]) is str:
            #         data_type = data_types[param_type[item]]
            #     elif type(param_type[item]) is dict:
            #         sub_item = param_type[item]
            #         for sub_sub_item in sub_item:
            #             data_type = data_types[sub_sub_item]
            #             # if data_type == '"DEShapefile"':
            #             #     data_filter = vector_filters[sub_item[sub_sub_item]]
            #     # elif item == "VectorAttributeField":
            #     #     data_type = widgets.Text(description=label, style=style)
            #         # dependency_field = param[item][1].replace("--", "")
            #     else:
            #         data_type = widgets.Text(description=label, style=style)

            #     if param_type == {"ExistingFileOrFloat": "Raster"}:
            #         data_type = FileChooser(title=label)
            
            children.append(var_widget)
            # display(FileChooser(title=label))
            # children.append(FileChooser(title=label))
            # chooser_types = [
            #     "Directory",
            #     "Raster",
            #     "Csv",
            #     "Text",
            #     "Html",
            #     "Lidar",
            #     "Vector",
            #     "RasterAndVector",
            #     "ExistingFileOrFloat"
            # ]
            # if param_type in chooser_types:
            #     print(label)
            #     display(FileChooser())  
            # elif param_type == "Boolean":
            #     bool_widget = widgets.Checkbox(description=label)
            # elif param_type = 

        # data_type = get_param_widget(items["parameter_type"])      
        # display(data_type)  

    run_btn = widgets.Button(description="Run", layout=widgets.Layout(width="100px"))
    cancel_btn = widgets.Button(description="Cancel", layout=widgets.Layout(width="100px"))
    help_btn = widgets.Button(description="Help", layout=widgets.Layout(width="100px"))
    # display(widgets.HBox([run_btn, cancel_btn, help_btn]))    
    children.append(widgets.HBox([run_btn, cancel_btn, help_btn]))
    tool_widget.children = children

    def run_button_clicked(b):
        args2 = []
        for arg in args:

            line = ""
            if isinstance(args[arg], FileChooser):
                if arg == 'i':
                    line = f"-{arg}={args[arg].selected}"
                else:
                    line = f"--{arg}={args[arg].selected}"
            elif isinstance(args[arg], widgets.Text):
                if args[arg].value is not None and len(args[arg].value)>0:
                    line = f"--{arg}={args[arg].value}"
            elif isinstance(args[arg], widgets.Checkbox):
                line = f"--{arg}={args[arg].value}"
            args2.append(line)        

        wbt.run_tool(tool_dict['name'], args2)

    run_btn.on_click(run_button_clicked)

    return tool_widget



def build_toolbox(tools_dict, folder_icon="folder", tool_icon="wrench"):

    left_widget = widgets.VBox()
    right_widget = widgets.VBox()
    full_widget = widgets.HBox([left_widget, right_widget])

    search_description = "Search tools ..."
    search_box = widgets.Text(placeholder=search_description)
    search_box.layout.width = "310px"
    tree_widget = widgets.Output()
    tree_widget.layout.max_width = "310px"
    tree_widget.overflow = "auto"

    left_widget.children = [search_box, tree_widget]
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
                # print(tool_name)
                # print(tools_dict[tool_name])
                # print("\n")

                tool_ui = tool_gui(tools_dict[tool_name])
                display(tool_ui)
                # params = tools_dict[tool_name]["parameters"]
                # for param in params:
                #     items = params[param]
                #     required = ""   
                #     if items["optional"] == "false":
                #         required = "*"
                #     print(items["name"] + required)     
                #     data_type = get_param_widget(items["parameter_type"])      
                #     display(data_type)  

                # run_btn = widgets.Button(description="Run", layout=widgets.Layout(width="100px"))
                # cancel_btn = widgets.Button(description="Cancel", layout=widgets.Layout(width="100px"))
                # help_btn = widgets.Button(description="Help", layout=widgets.Layout(width="100px"))
                # display(widgets.HBox([run_btn, cancel_btn, help_btn]))

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
            category_node =  categories[category]
            tool_node = Node(key, icon=tool_icon)    
            category_node.add_node(tool_node)    
            tree_dict[key] = tool_node
            tool_node.observe(handle_tool_clicked, "selected")

    with tree_widget:
        tree_widget.clear_output()
        display(tree)

    return full_widget

def show(reset=False, verbose=True):

    tools_dict = get_wbt_dict(reset=reset)
    # print(tools_dict.keys())
    # print(tools_dict["Slope"])

    if verbose:
        wbt.verbose = True
    else:
        wbt.verbose = False


    return build_toolbox(tools_dict)


if __name__ == "__main__":
    show(reset=False)
