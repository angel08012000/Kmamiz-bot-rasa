import setting as s
import urllib.parse
from pygments import highlight
from pygments.lexers import TypeScriptLexer
from pygments.formatters import ImageFormatter
from io import BytesIO
from PIL import Image

def get_all_endpoints():
    url = f"{s.PREFIX}/api/v1/data/label"
    res = s.get_api(url)

    endpoint = []
    unique_label_name = []
    
    for r in res:
        label = r[1]
        service, namespace, version, method, path = r[0].split('\t')
        temp = f"{service}\t{namespace}\t{version}\t{method}\t{label}"

        endpoint.append(f"({version}) {method} {label}")
        unique_label_name.append(urllib.parse.quote(temp, safe=""))
    
    return {"endpoint": endpoint, "unique_label_name": unique_label_name}

def get_schema_text_of_endpoint(unique_label_name):
    url = f"{s.PREFIX}/api/v1/data/datatype/{unique_label_name}"
    res = s.get_api(url)["schemas"][0]

    return {"request_schema": res["requestSchema"], "response_schema": res["responseSchema"]}

def text_highlight(code, image_name):
    highlighted_code = highlight(code, TypeScriptLexer(), ImageFormatter(style="murphy"))
    with open(f"./images/{image_name}.png", "wb") as img_file:
        img_file.write(highlighted_code)

def get_schema_img_and_text_of_endpoint(unique_label_name):
    schema = get_schema_text_of_endpoint(unique_label_name)
    text_highlight(schema["request_schema"], "request_schema")
    text_highlight(schema["response_schema"], "response_schema")

    return schema

# print(get_schema_of_endpoint("ratings%09book%09v1%09GET%09%2Fratings%2F0"))