# import requests
import json
import sys

from .setting import *
# from setting import *

from time import sleep

sys.path.append("modules")
import screen_circle as sc

# 如果用 \t，button 會壞掉！
# def service_format(services):
#     services_tab = []
#     for s in services:
#         temp = s.split('.')
#         services_tab.append('\t'.join(temp))
#     return services_tab


# data 的形式為
# {"<<service_name>>" : {"SIUC", <<value>>, ...}, ...}

def get_cohesion():
    url = url = f"{PREFIX}/api/v1/graph/cohesion/{NAMESPACE}"
    response = get_api(url)

    cohesion = {
        "service": [],
        "SIDC": [],
        "SIUC": [],
        "TSIC": [],
    }
    for data in response:
        cohesion["service"].append(data["uniqueServiceName"].replace('\t', '.'))
        cohesion["SIDC"].append(data["dataCohesion"])
        cohesion["SIUC"].append(data["usageCohesion"])
        cohesion["TSIC"].append(data["totalInterfaceCohesion"])
    
    return cohesion

def get_coupling():
    url = url = f"{PREFIX}/api/v1/graph/coupling/{NAMESPACE}"
    response = get_api(url)

    coupling = {
        "service": [],
        "AIS": [],
        "ADS": [],
        "ACS": [],
    }
    for data in response:
        coupling["service"].append(data["uniqueServiceName"].replace('\t', '.'))
        coupling["AIS"].append(data["ais"])
        coupling["ADS"].append(data["ads"])
        coupling["ACS"].append(data["acs"])
    
    return coupling

def get_instability():
    url = url = f"{PREFIX}/api/v1/graph/instability/{NAMESPACE}"
    response = get_api(url)

    instability = {
        "service": [],
        "FanOut": [],
        "FanIn": [],
        "SDP": [],
    }
    for data in response:
        instability["service"].append(data["uniqueServiceName"].replace('\t', '.'))
        instability["FanOut"].append(data["dependingOn"])
        instability["FanIn"].append(data["dependingBy"])
        instability["SDP"].append(data["instability"])
    
    return instability

def get_insight_data(insight):
    data = None
    if insight == "cohesion":
        data = get_cohesion()
    elif insight == "coupling":
        data = get_coupling()
    elif insight == "instability":
        data = get_instability()
    return data

# 好像其實是 endpoint 不是 service??
def get_all_services():
    url = f"{PREFIX}/api/v1/data/label"
    res_default = get_api(url)

    services = []
    for service in res_default:
        temp = service[0].split('\t')
        services.append('.'.join(temp[:3]))

    # 暴力處理順序不同的問題 START
    services[0], services[1], services[2], services[3], services[4], services[5] = services[3], services[4], services[2], services[0], services[5], services[1]
    # END
    
    return services


def set_image_param(service):
  with open('./settings/insight.json', 'r') as file:
    json_data = file.read()

  param = json.loads(json_data)
  param['URL_or_HTML'] = f"{PREFIX}/insights"

  if service!=None:
    services = get_all_services() 
    num = len(services)
    target = services.index(service)
    for p in param['IMAGES_PARAM']:
      p['SUM'] = str(num)
      p['TARGET'] = str(target)

  with open('./settings/insight.json', 'w') as json_file:
    json.dump(param, json_file)

def get_insight_image(insight, service):
    highlighted = True if insight == "all insights" else False
    if(highlighted):
        set_image_param(service)
    
    print(f"highlight: {highlighted}")
    
    h = sc.Highlighted()
    h.screenshot_with_highlighted("insight", highlighted)

# def get_target_para(service):
#     para = {}
#     temp = 0
#     services = get_all_services()
#     para["num"] = len(services)

#     for s in services:
#         if s == service:
#             para["target"] = temp
#             break
#         temp += 1
#     return para

def get_all_insights(service):
    insights = {}

    temp = get_cohesion()
    index = temp["service"].index(service)
    insights["cohesion"] = {
        "SIDC": temp["SIDC"][index],
        "SIUC": temp["SIUC"][index],
        "TSIC": temp["TSIC"][index],
    }

    temp = get_coupling()
    index = temp["service"].index(service)
    insights["coupling"] = {
        "AIS": temp["AIS"][index],
        "ADS": temp["ADS"][index],
        "ACS": temp["ACS"][index],
    }

    temp = get_instability()
    index = temp["service"].index(service)
    insights["instability"] = {
        "FanOut": temp["FanOut"][index],
        "FanIn": temp["FanIn"][index],
        "SDP": temp["SDP"][index],
    }

    print(f"all insights: {insights}") 

    return insights

def get_insight_output(namespace, insight, service, display):
    # output = f"The insight of {service} is ...\n\n" if insight == "all insights" else f"The {insight} is ...\n\n"
    output = ""

    if display == "text":
        if insight == "all insights":
            for key, value in get_all_insights(namespace, service).items():
                output += f"The {key} is "
                for k, v in value.items():
                    output += f"{k} : {v}\n"
                output += "\n"
            return output
    
    elif display == "image":
        set_image_param(service)
        highlighted = False if insight == "all insights" else True
        print(f"highlight: {highlighted}")

        h = sc.Highlighted()
        h.screenshot_with_highlighted("insight", highlighted)

    elif display == "url":
        return
    else:
        return

# get_insight_output("book", "cohesion", None, "text")
