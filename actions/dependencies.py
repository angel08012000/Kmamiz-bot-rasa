import json

import sys
sys.path.append("modules")
sys.path.append("actions")
import screen_circle as sc
import setting as s

def get_dependencies_text(namespace, way):
    res = s.get_api(f"{s.PREFIX}/api/v1/graph/chord/{way}/{namespace}")
    data = res["links"]
    format_data = {}

    for d in data:
        service_from = d["from"]
        if service_from not in format_data:
            format_data[service_from] = f"service {service_from} depends on\n\n"
        
        val = d['value']
        format_data[service_from] += f"{d['to']} {val} {'time' if val<=1 else 'times'}\n\n"

    output = ""
    # print(f"keys們：{list(format_data.keys())[-1]}")
    for service in format_data.keys():
        output += format_data[service]
        if service != list(format_data.keys())[-1]:
            output += ".\n\n"

    # print(f"結果：{output}")

    return output


def get_service_graph_image():
    data = {
        "CHROMEDRIVER_PATH" : "./chromedriver",
        "WAY" : "url",
        "URL_or_HTML" : s.PREFIX,
        "WINDOW_SIZE" : {
            "WIDTH": "700",
            "HEIGHT": "700"
        },
        "HIDDEN_CSS_SELECTOR": [
            ".MuiPaper-root.MuiPaper-elevation.MuiPaper-elevation4.MuiAppBar-root.MuiAppBar-colorPrimary.MuiAppBar-positionFixed.mui-fixed.css-5poeop"
        ],
        "CSS_SELECTOR" : "canvas",
        "TOGGLE_CSS_SELECTOR" : [
            "#root > div.jss3 > div.MuiPaper-root.MuiPaper-elevation.MuiPaper-rounded.MuiPaper-elevation1.MuiCard-root.jss4.css-s18byi > div > label > span.MuiSwitch-root.MuiSwitch-sizeMedium.css-ecvcn9 > span.MuiSwitch-switchBase.MuiSwitch-colorPrimary.Mui-checked.MuiButtonBase-root.MuiSwitch-switchBase.MuiSwitch-colorPrimary.Mui-checked.PrivateSwitchBase-root.Mui-checked.css-1nr2wod"
        ],
        "IMAGES_PATH" : "./images",
        "IMAGES_PARAM" : [
            {
                "IMAGE_NAME": "service_dependency_graph"
            }
        ]
    }

    with open('./settings/KMamiz.json', 'w') as json_file:
        json.dump(data, json_file)

    h = sc.Highlighted()
    h.screenshot_with_highlighted("../settings/KMamiz", False)

def get_endpoint_graph_image():
    data = {
        "CHROMEDRIVER_PATH" : "./chromedriver",
        "WAY" : "url",
        "URL_or_HTML" : s.PREFIX,
        "WINDOW_SIZE" : {
            "WIDTH": "900",
            "HEIGHT": "900"
        },
        "HIDDEN_CSS_SELECTOR": [
            ".MuiPaper-root.MuiPaper-elevation.MuiPaper-elevation4.MuiAppBar-root.MuiAppBar-colorPrimary.MuiAppBar-positionFixed.mui-fixed.css-5poeop"
        ],
        "CSS_SELECTOR" : "canvas",
        "IMAGES_PATH" : "./images",
        "IMAGES_PARAM" : [
            {
                "IMAGE_NAME": "endpoint_dependency_graph"
            }
        ]
    }

    with open('./settings/KMamiz.json', 'w') as json_file:
        json.dump(data, json_file)

    h = sc.Highlighted()
    h.screenshot_with_highlighted("../settings/KMamiz", False)

def get_dependency_image():
    data = {
        "CHROMEDRIVER_PATH" : "./chromedriver",
        "WAY" : "url",
        "URL_or_HTML" : f"{s.PREFIX}/insights",
        "WINDOW_SIZE" : {
            "WIDTH": "1200",
            "HEIGHT": "772"
        },
        "HIDDEN_CSS_SELECTOR": [
            ".MuiPaper-root.MuiPaper-elevation.MuiPaper-elevation4.MuiAppBar-root.MuiAppBar-colorPrimary.MuiAppBar-positionFixed.mui-fixed.css-5poeop"
        ],
        "CSS_SELECTOR" : ".MuiPaper-root.MuiPaper-outlined.MuiPaper-rounded.MuiCard-root.css-1okfn8i",
        "IMAGES_PATH" : "./images",
        "IMAGES_PARAM" : [
            {
                "IMAGE_NAME": "direct_service_dependencies"
            },
            {
                "IMAGE_NAME": "indirect_service_dependencies"
            }
        ]
    }

    with open('./settings/KMamiz.json', 'w') as json_file:
        json.dump(data, json_file)

    h = sc.Highlighted()
    h.screenshot_with_highlighted("../settings/KMamiz", False)
