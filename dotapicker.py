import win32con
import win32gui
import win32ui
import time
import numpy as np
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import cv2 as cv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

chrome_driver_path = "C:\\Users\\Aik Jie Sheng\\OneDrive\\Documents\\Development\\chromedriver.exe"
URL = "http://dotapicker.com/counterpick"
METHOD = cv.TM_CCOEFF_NORMED
DIRE_RED_CV = cv.imread(os.path.join(BASE_DIR, "dire-red.jpg"))
DIRE_GREEN_CV = cv.imread(os.path.join(BASE_DIR, "dire-green.jpg"))

RADIANT_REGION = (205, 0, 625, 50)
DIRE_REGION = (1090, 0, 625, 50)
MAP_COOR = (250, 800, 200, 200)
# MAP_COOR = (100, 900, 200, 200)  # Radiant
DIRE_ICONS = (1090, 0, 625, 85)
RADIANT_ICONS = (205, 0, 625, 85)
HERO_ICONS = []

hero_icon_folder = os.path.join(BASE_DIR, "hero-icons")
for filename in os.listdir(hero_icon_folder):
    HERO_ICONS.append((cv.imread(os.path.join(BASE_DIR, f"hero-icons\\{filename}")), filename))


def screenshot(x, y, w, h):
    hwnd = None
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj = win32ui.CreateDCFromHandle(wDC)
    cDC = dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0, 0), (w, h), dcObj, (x, y), win32con.SRCCOPY)

    signedIntsArray = dataBitMap.GetBitmapBits(True)
    img = np.frombuffer(signedIntsArray, dtype='uint8').reshape((h, w, 4))
    # dataBitMap.SaveBitmapFile(cDC, "out.bmp")

    # Free Resources
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())

    return img


# time.sleep(2)
# screenshot(RADIANT_ICONS[0], RADIANT_ICONS[1], RADIANT_ICONS[2], RADIANT_ICONS[3])

def locate_on_screen(method, region, base_image):
    img = screenshot(region[0], region[1], region[2], region[3])
    img_cv = cv.cvtColor(img, cv.COLOR_BGRA2BGR)
    res = cv.matchTemplate(img_cv, base_image, method)
    # print(res)
    return (res >= 0.7).any()


file = open("skill-level.txt", "r")
skill_level = file.readline().title()

driver = webdriver.Chrome(executable_path=chrome_driver_path)
driver.get(URL)

skill_level_button = driver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div[2]/div[1]/div/div[3]/div/select')
skill_level_button.click()

if skill_level == "Normal":
    pass
elif skill_level == "High":
    skill_level_button.send_keys(Keys.UP)
elif skill_level == "Very High":
    skill_level_button.send_keys(Keys.UP)
    skill_level_button.send_keys(Keys.UP)
else:
    raise KeyError(f"Invalid skill level. Change the skill level in skill-level.txt to something valid i.e. "
                   f"\"Normal\", \"High\" or \"Very High\". You entered {skill_level}")

skill_level_button.send_keys(Keys.ENTER)

driver.set_window_size(600, 400)
driver.set_window_position(660, 650, windowHandle='current')

cookie_message = driver.find_element_by_id('cookieChoiceDismiss')
cookie_message.click()

count = 0
heroes_selected = []


while True:
    region = locate_on_screen(METHOD, MAP_COOR, DIRE_RED_CV)
    region1 = locate_on_screen(METHOD, MAP_COOR, DIRE_GREEN_CV)
    if region:
        icons = cv.imread(os.path.join(BASE_DIR, "dire-icons.jpg"))
        while True:
            start = time.time()
            for icon in HERO_ICONS:
                icon_present = locate_on_screen(METHOD, DIRE_ICONS, icon[0])
                if icon_present:
                    hero_name_list = icon[1].split("_icon")[0].split("_")
                    hero_name = " ".join(hero_name_list)

                    if hero_name not in heroes_selected:

                        search_hero = driver.find_element_by_id("setautofocus")
                        search_hero.send_keys(hero_name)
                        search_hero.send_keys(Keys.ENTER)

                        heroes_selected.append(hero_name)

                        print(hero_name)

                        count += 1

                        if count == 5:
                            break
            print(round(time.time() - start, 2))

            if count == 5:
                break
    if count == 5:
        break

    elif region1:
        icons = cv.imread(os.path.join(BASE_DIR, "radiant-icons.jpg"))
        while True:
            start = time.time()
            for icon in HERO_ICONS:
                icon_present = locate_on_screen(METHOD, RADIANT_ICONS, icon[0])
                if icon_present:
                    hero_name_list = icon[1].split("_icon")[0].split("_")
                    hero_name = " ".join(hero_name_list)

                    if hero_name not in heroes_selected:

                        search_hero = driver.find_element_by_id("setautofocus")
                        search_hero.send_keys(hero_name)
                        search_hero.send_keys(Keys.ENTER)

                        heroes_selected.append(hero_name)

                        print(hero_name)

                        count += 1

                        if count == 5:
                            break

            print(round(time.time() - start, 2))

            if count == 5:
                break
    if count == 5:
        break

# def timing(f):
#     def wrap(*args, **kwargs):
#         time1 = time.time()
#         ret = f(*args, **kwargs)
#         time2 = time.time()
#         print('{:s} function took {:.3f} ms'.format(
#             f.__name__, (time2-time1)*1000.0))
#
#         return ret
#     return wrap
#
#
# @timing
# def benchmark_pyautogui():
#     return pyautogui.locateOnScreen(DIRE_RED_PIL, confidence=0.7, region=MAP_COOR)
#
#
# @timing
# def benchmark_opencv_pil(method):
#     img = ImageGrab.grab(bbox=MAP_COOR_CV)
#     img_cv = cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)
#     res = cv.matchTemplate(img_cv, DIRE_RED_CV, method)
#     # print(res)
#     return (res >= 0.8).any()
#
#
# DIRE_RED_PIL = Image.open(".\\dire-red.jpg")
# benchmark_pyautogui()
# methods = ['cv.TM_CCOEFF_NORMED', 'cv.TM_CCORR_NORMED']
# for method in methods:
#         print(method)
#         im_opencv = benchmark_opencv_pil(eval(method))
#         print(im_opencv)
