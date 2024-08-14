# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import requests
import json

from .setting import *
from .insights import *
from .dependencies import *
from .schema import *

import os
from rasa.shared.utils.io import read_file
from datetime import datetime # 為了解決 Rasa 會緩存舊圖片的問題

from PIL import Image
from base64 import encodebytes
import io

def call_function_by_name(function_name, *args, **kwargs):
  global_symbols = globals()

  # 檢查 function 是否存在＆可用
  if function_name in global_symbols and callable(global_symbols[function_name]):
    # 呼叫
    function_to_call = global_symbols[function_name]
    return function_to_call(*args, **kwargs)
  else:
    # 丟出錯誤
    raise ValueError(f"Function '{function_name}' not found or not callable.")
def GET_IMAGE_BASE64(image_path):
  pil_img = Image.open(image_path, mode='r') # reads the PIL image
  byte_arr = io.BytesIO()
  pil_img.save(byte_arr, format='PNG') # convert the PIL image to byte array
  encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii') # encode as base64
  return encoded_img

#--- insight START ---#
class ActionFillInsightSlot(Action):

    def name(self) -> Text:
        return "action_fill_insight_slot"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get("text")

        for i in INSIGHTS:
            if user_message.find(i)!=-1: #代表有找到
                return[SlotSet("insight", i)]
        
        dispatcher.utter_message(text="The insight you want to watch isn't exist. Please check the name of insight or use the buttons.")
        return []
class ActionRespondBasedOnInsightValue(Action):

    def name(self) -> Text:
        return "action_respond_based_on_insight_value"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        insight = tracker.get_slot('insight')

        if insight == "all insights":
            buttons = [{'title': s, 'payload': f'/choose_services_of_insights{{"services":"{s}"}}'}
            for s in get_all_services()]

            dispatcher.utter_message(text=f"which service do you want to watch?", buttons = buttons)
        else:
            dispatcher.utter_message(response="utter_type_of_display")
        return []
#--- insight END ---#


#--- dependency START ---#
class ActionFillDependencySlot(Action):

    def name(self) -> Text:
        return "action_fill_dependency_slot"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dependency = tracker.get_slot('dependency')
        print(f"抓取到 dependency: {dependency}")
        user_message = tracker.latest_message.get("text")

        for d in DEPENDENCIES:
            if user_message.find(d)!=-1: #代表有找到
                return[SlotSet("dependency", d)]
        
        dispatcher.utter_message(text="The dependency you want to watch isn't exist. Please check the name of dependency or use the buttons.")
        return []
#--- dependency END ---#


#--- swagger START ---#
class ActionDisplaySwagger(Action):

    def name(self) -> Text:
        return "action_display_swagger"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        service_origin = tracker.get_slot('service')
        service = service_origin.replace(".", "%09")

        if service == None:
            dispatcher.utter_message(text=f"The service you choose donesn't exit.")
        dispatcher.utter_message(text=f"[swagger of {service_origin}]({PREFIX}/swagger/{service})")

        return []
class ActionGetServiceOfSwagger(Action):

    def name(self) -> Text:
        return "action_get_service_of_swagger"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        buttons = [{'title': s, 'payload': f'/choose_services_of_swagger{{"services":"{s}"}}'}
        for s in get_all_services()]
        dispatcher.utter_message(text=f"Which service do you want to watch?", buttons = buttons)

        return []
#--- swagger END ---#


#--- schema START ---#
class ActionChooseSchema(Action):

    def name(self) -> Text:
        return "action_choose_schema"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


        buttons = [{'title': e, 'payload': f'/choose_endpoint{{"endpoint":"{e}"}}'}
        for e in get_all_endpoints()]

        dispatcher.utter_message(text=f"which endpoint do you want to watch?", buttons = buttons)
        
        return []
class ActionDisplaySchema(Action):

    def name(self) -> Text:
        return "action_display_schema"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        endpoint = tracker.get_slot('endpoint')
        data = get_all_endpoints()
        endpoints = data["endpoint"]
        unique_label_names = data["unique_label_name"]

        for index, item in enumerate(endpoints):
            if endpoint == item:
                break
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        schemas = get_schema_img_and_text_of_endpoint(unique_label_names[index])
        
        dispatcher.utter_message(text="**view as image**")
        dispatcher.utter_message(text="request schema:\n")
        image = GET_IMAGE_BASE64(f"{IMAGES_PATH}/request_schema.png")
        #dispatcher.utter_message(image=f"{IMAGES_PATH}/request_schema.png?timestamp={timestamp}")
        dispatcher.utter_message(image=f"data:image/png;base64,{image}")

        dispatcher.utter_message(text="response schema:\n")
        image = GET_IMAGE_BASE64(f"{IMAGES_PATH}/response_schema.png")
        dispatcher.utter_message(image=f"data:image/png;base64,{image}")

        output = ""
        output += "**original text**\n\n"
        output += "request schema:\n"
        output += "```react\n"
        output += schemas["request_schema"]
        output += "\n```\n\n"

        output += "response schema:\n"
        output += "```react\n"
        output += schemas["response_schema"]
        output += "\n```\n"
        
        dispatcher.utter_message(text=output)
        return []
#--- schema END ---#


class ActionRespondBasedOnFunctionValue(Action):

    def name(self) -> Text:
        return "action_respond_based_on_function_value"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        function = tracker.get_slot('function')
        print(f"已抓取到 function 為 {function}")

        if function == "insight":
            dispatcher.utter_message(response="utter_choose_insights")
        elif function == "dependency":
            dispatcher.utter_message(response="utter_choose_dependencies")
        elif function == "swagger":
            dispatcher.utter_message(text=f"not done")
        elif function == "schema":
            buttons = [{'title': e, 'payload': f'/choose_endpoint_of_schema{{"endpoint": "{e}"}}'}
            for e in get_all_endpoints()["endpoint"]]
            dispatcher.utter_message(text=f"which endpoint do you want to watch?", buttons = buttons)
        else:
            dispatcher.utter_message(response="utter_start_kmamiz_bot")

        return []
class ActionGetOutput(Action):

    def name(self) -> Text:
        return "action_get_output"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        function = tracker.get_slot('function')
        # print(f"您選擇的功能為 {function}")
        display = tracker.get_slot('display')

        if function=="insight":
            insight = tracker.get_slot('insight')
            service = tracker.get_slot('service') if insight == "all insights" else None
            
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            
            # print(f'insight {insight}\nservice {service}')

            if display == "text":
                if insight == "all insights":
                    dispatcher.utter_message(text=f"The insight of {service} which view as table is ...")
                    data = get_all_insights(service)
                    create_all_insights_table(data)
                else:
                    dispatcher.utter_message(text=f"The {insight} is ...")
                    data = get_insight_data(insight)
                    create_insight_table(data)
                
                image = GET_IMAGE_BASE64(f"{IMAGES_PATH}/table.png")
                dispatcher.utter_message(image=f"data:image/png;base64,{image}")
            elif display == "image":
                get_insight_image(insight, service) #去抓新的圖片
                if insight == "all insights":
                    dispatcher.utter_message(text=f"The insight of {service} is ...")
                    for i in INSIGHTS[:3]:
                        image = GET_IMAGE_BASE64(f"{IMAGES_PATH}/{i}.png")
                        dispatcher.utter_message(image=f"data:image/png;base64,{image}")
                else:
                    dispatcher.utter_message(text=f"The {insight} is ...")
                    image = GET_IMAGE_BASE64(f"{IMAGES_PATH}/{insight}.png")
                    dispatcher.utter_message(image=f"data:image/png;base64,{image}")
            elif display == "url":
                dispatcher.utter_message(text=f"[more information]({PREFIX}/insights)")
            else:
                dispatcher.utter_message(text="the way you chose is not exist.")
        
        elif function=="dependency":
            dependency = tracker.get_slot('dependency')
            dependency_type = dependency.replace(" ", "_")
            print(f"圖片為：{dependency_type}")

            if display == "text":
                if dependency_type=="direct_service_dependencies":
                    dispatcher.utter_message(text = get_dependencies_text(NAMESPACE, "direct"))
                elif dependency_type=="indirect_service_dependencies":
                    dispatcher.utter_message(text = get_dependencies_text(NAMESPACE, "indirect"))
                else:
                    dispatcher.utter_message(text="The dependency would be clearer with an image or URL.")
            elif display == "image":
                if dependency_type=="service_dependency_graph":
                    get_service_graph_image()
                elif dependency_type=="endpoint_dependency_graph":
                    get_endpoint_graph_image()
                elif dependency_type=="direct_service_dependencies" or dependency_type=="indirect_direct_service_dependencies":
                    get_dependency_image()

                dispatcher.utter_message(text=f"The {dependency} is ...")
                image = GET_IMAGE_BASE64(f"{IMAGES_PATH}/{dependency_type}.png")
                dispatcher.utter_message(image=f"data:image/png;base64,{image}")
            elif display == "url":
                if dependency_type=="service_dependency_graph" or dependency_type=="endpoint_dependency_graph":
                    dispatcher.utter_message(text=f"[more information]({PREFIX})")
                elif dependency_type=="direct_service_dependencies" or dependency_type=="indirect_direct_service_dependencies":
                    dispatcher.utter_message(text=f"[more information]({PREFIX}/insights)")
                else:
                    dispatcher.utter_message(text=f"something wrong, please retry in few seconds")
            else:
                dispatcher.utter_message(text="the way you chose is not exist.")
        return []
