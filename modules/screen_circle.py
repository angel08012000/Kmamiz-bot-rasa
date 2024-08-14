#2023.08.30 screen_circle
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from PIL import Image, ImageDraw
from io import BytesIO
from time import sleep
import time
import os

class Highlighted():
    def screenshot_with_highlighted(self, file_name, highlighted):
        with open(f'./settings/{file_name}.json', 'r') as file:
            param = json.load(file)
            CHROMEDRIVER_PATH = param["CHROMEDRIVER_PATH"]
            WAY = param["WAY"]
            URL_or_HTML = param["URL_or_HTML"]
            WINDOW_SIZE = param["WINDOW_SIZE"]
            CSS_SELECTOR = param["CSS_SELECTOR"]
            IMAGES_PARAM = param["IMAGES_PARAM"]

        # 新建 ChromeOptions 對象，並設定成 headless 模式
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument(f"--window-size={WINDOW_SIZE['WIDTH']},{WINDOW_SIZE['HEIGHT']}")
        
        # 設置瀏覽器並打開網頁
        # driver = webdriver.Chrome(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(options=chrome_options)
        
        if WAY=="url":
            driver.get(URL_or_HTML)
        elif WAY=="html":
            parent_dir = os.path.dirname(os.path.abspath(__file__))
            driver.get(f"file://{parent_dir}/{URL_or_HTML}")
            # print(f"檔案路徑: {parent_dir}/{URL_or_HTML}")
        else:
            print("您只能用「url」或「html」方式開啟")
            print("意即 WAY 這個參數只能填 url 或 html")
            return
        driver.implicitly_wait(10)
        
        # 取得元素資訊
        elements = self.find_elements(driver, param)
        if len(elements)!=len(IMAGES_PARAM):
            print("「欲抓取之元素數量」＆「參數數量」不符！")
            print(f"「欲抓取之元素數量」: {len(elements)}")
            print(f"「參數數量」: {len(IMAGES_PARAM)}")
            return

        try:
            self.find_and_hide_elements(driver, param)
            self.find_and_toggle_element(driver, param)
        except Exception as e:
            print("錯誤訊息：", e)
        
        i=0
        for e in elements:
            if highlighted:
                self.adjust_frame_size(driver, e, param, i)
            else:
                self.screenshot(driver, e, param, i)
            i+=1
        
        driver.quit()
    
    def find_elements(self, driver, param):
        CSS_SELECTOR = param["CSS_SELECTOR"]
        # IFRAME_SELECTOR = param["CUSTOM"]
        # iframe_element = driver.find_element(By.CSS_SELECTOR, IFRAME_SELECTOR) 
        # driver.switch_to.frame(iframe_element)

        elements = driver.find_elements(By.CSS_SELECTOR, CSS_SELECTOR)
        return elements
    
    def find_and_hide_elements(self, driver, param):
        if "HIDDEN_CSS_SELECTOR" in param:
            for name in param["HIDDEN_CSS_SELECTOR"]:
                # print(f"name: {name}")
                hidden_ele = driver.find_elements(By.CSS_SELECTOR, name)
                # print(f"隱藏元素長度：{len(hidden_ele)}")
                driver.execute_script("arguments[0].style.display='none';", hidden_ele[0])

    def find_and_toggle_element(self, driver, param):
        if "TOGGLE_CSS_SELECTOR" in param:
            for name in param["TOGGLE_CSS_SELECTOR"]:
                toggle_ele = driver.find_element(By.CSS_SELECTOR, name)
                # is_checked = toggle_ele.is_selected()
                # print("現在狀態:", is_checked)

                # 點擊元素以切換狀態
                toggle_ele.click()

    # 截圖拉出來是因為有只需要截圖的情況
    def screenshot(self, driver, element, param, i):
        IMAGES_PARAM = param["IMAGES_PARAM"]
        IMAGES_PATH = param["IMAGES_PATH"]
        IMAGE_NAME = IMAGES_PARAM[i]["IMAGE_NAME"]

        driver.execute_script("arguments[0].scrollIntoView();", element)
        time.sleep(0.3)

        os.makedirs(f"{IMAGES_PATH}", exist_ok=True)
        element.screenshot(f"{IMAGES_PATH}/{IMAGE_NAME}.png")

    def adjust_frame_size(self, driver, element, param, i):
        self.screenshot(driver, element, param, i)

        IMAGES_PARAM = param["IMAGES_PARAM"]
        IMAGES_PATH = param["IMAGES_PATH"]
        IMAGE_NAME = IMAGES_PARAM[i]["IMAGE_NAME"]

        # print(f"my path --- {IMAGES_PATH}/{IMAGE_NAME}.png")
        image = Image.open(f"{IMAGES_PATH}/{IMAGE_NAME}.png")

        # 系統提供之參數
        WIDTH = element.size["width"]
        HEIGHT = element.size["height"]

        # print(f"寬: {WIDTH}")
        # print(f"高: {HEIGHT}")

        # 使用者給定之參數
        DIRECTION = IMAGES_PARAM[i]["DIRECTION"]
        TOP_RATIO = eval(IMAGES_PARAM[i]["TOP_RATIO"])
        BOTTOM_RATIO = eval(IMAGES_PARAM[i]["BOTTOM_RATIO"])
        LEFT_RATIO = eval(IMAGES_PARAM[i]["LEFT_RATIO"])
        RIGHT_RATIO = eval(IMAGES_PARAM[i]["RIGHT_RATIO"])
        SUM = eval(IMAGES_PARAM[i]["SUM"])
        TARGET = eval(IMAGES_PARAM[i]["TARGET"])

        #---------- 如果是 KMamiz.html 的話 START ----------#
        # LEFT_SIZE = eval(IMAGES_PARAM[i]["LEFT_SIZE"])
        # RIGHT_SIZE = eval(IMAGES_PARAM[i]["RIGHT_SIZE"])
        #---------- 如果是 KMamiz.html 的話 END ----------#
        
        if DIRECTION=="vertical":
            frame_width = WIDTH * (1 - (LEFT_RATIO+RIGHT_RATIO) ) / SUM
            frame_height = HEIGHT * (1 - (TOP_RATIO+BOTTOM_RATIO))
            x = LEFT_RATIO*WIDTH + TARGET*frame_width
            y = TOP_RATIO*HEIGHT
        elif DIRECTION=="horizontal":
            frame_width = WIDTH * (1 - (LEFT_RATIO+RIGHT_RATIO) )
            frame_height = HEIGHT * (1 - (TOP_RATIO+BOTTOM_RATIO))/ SUM
            x = LEFT_RATIO*WIDTH
            y = TOP_RATIO*HEIGHT + TARGET*frame_height

        # 使用 ImageDraw 库將圓形圈起重要信息
        # cohesion
        # x, y, frame_width, frame_height = 68, 50, 657, 518
        # x, y, frame_width, frame_height = 60, 50, 663, 518
        # x, y, frame_width, frame_height = 118, 50, 605, 518

        draw = ImageDraw.Draw(image)
        draw.rectangle((x, y, x+frame_width, y+frame_height), outline='red', width=5)

        #---------- 如果是 KMamiz.html 的話 START ----------#
        # draw.rectangle((x-LEFT_SIZE, y, x+frame_width+RIGHT_SIZE, y+frame_height), outline='red', width=5)
        #---------- 如果是 KMamiz.html 的話 END ----------#

        # 將處理後的圖像保存到本地
        image.save(f"{IMAGES_PATH}/{IMAGE_NAME}.png")

# highlighted = Highlighted()
# highlighted.screenshot_with_highlighted("insight", False)