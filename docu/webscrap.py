from selenium import webdriver
from selenium.webdriver.common.by import By

# 명시적 대기를 위한 import
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# 텍스트 파일을 리스트로 불러오기
file_path = "test.txt"
my_list = []

# 각 줄을 리스트 요소로 저장, UTF8형식 불러오기
with open(file_path, "r", encoding='UTF8') as file:
    test_list = file.readlines()  

# 리스트 요소 [소분류, 제품코드]로 가공
for data in test_list :
    my_list.append(data.split())

print(my_list)

import pandas as pd

# 딕셔너리를 이용하여 데이터프레임 생성
dict_data = {
    "제품코드" : [],
    "소분류" : [],
    "제품명" : [],
    "이미지" : [],
    "가격" : []
    }

#웹 문서를 지정해서 브라우저를 실행한다.

#셀레니움으로 크롬브라우저를 다루는 
#웹드라이버 객체 생성
driver = webdriver.Chrome()
driver.get("https://www.jangboja.com/")
time.sleep(4)
selector = "//*[@id='checkCategory']//button[contains(text(), '농수축산')]"

for data in my_list :
    if data[0] == "---" :
        selector = "//*[@id='checkCategory']//button[contains(text(), '가공식품')]"
        continue
    driver.execute_script(f"window.location.href = 'https://www.jangboja.com/goods/searchItemList?keyword={data[0]}'")
    
    try:
        # WebDriverWait를 사용하여 최대 10초까지 기다립니다.
        # 어떤 것을 기다릴지 EC(expected_conditions)로 지정합니다.
        # By.CSS_SELECTOR를 사용해 '#itemList .item' 요소가 나타날 때까지 기다립니다.
        # '.item'은 각 상품 하나하나를 감싸는 클래스입니다. 이 요소가 나타나면 상품 로딩이 완료된 것입니다.
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#itemList .item"))
        )
        print("상품 목록 로딩 완료!")
        time.sleep(3)   # 사이트 과부하 방지
        
        # 정확한 수집을 위해 카테고리 클릭
        if data[0] in ("햄", "골뱅이", "김") :
            driver.find_element(By.XPATH, "//*[@id='checkCategory']//button[contains(text(), '가공식품')]").click()
        else :
            categoly = driver.find_element(By.XPATH, selector)
            categoly.click()
        
        time.sleep(2)

        # 로딩이 완료되었으므로 이제 page_source를 가져옵니다.
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        
        # select를 사용해서 요소 여러개 리스트로
        items = soup.select("#itemList a.item-info-tit") # 제품명
        images = soup.select("#itemList img.itemImg") # 이미지
        prices = soup.select("#itemList div.info > div.price > span.price-tag > strong") # 가격

        if not items:
            print("상품명을 찾을 수 없습니다.")
        else:
            # 모든 상품명 출력
            print("="*40)
            print("크롤링된 상품명 목록")
            print("="*40)
            count = 0
            for item in items:
                if count < 5 :
                    # 제품명 추가
                    title = item.text.strip().replace("#", "").replace("$", "")
                    dict_data['제품명'].append(title)
                    print(title)
                    
                    # 이미지 링크 추가
                    link = images[count].get('src')
                    dict_data['이미지'].append(link)
                    print(link)
                    
                    # 가격 추가
                    won = prices[count].text.strip()
                    dict_data['가격'].append(won)
                    print(won)
                    
                    # 소분류, 제품코드 추가
                    dict_data['소분류'].append(data[0])
                    dict_data['제품코드'].append(data[1]+f"{count:02d}")
                    print(data[0], data[1]+f"{count:02d}")
                    
                    count += 1
                else :
                    break
    except Exception as e:
        print("오류가 발생했습니다:", e)

    finally:
        count = 0
        
# 작업이 끝나면 브라우저를 닫아줍니다.
driver.quit()
df = pd.DataFrame(dict_data)

try:
    # csv 파일로 저장
    df.to_csv("cooking.csv", encoding="euc-kr")

    # 엑셀파일로 저장
    df.to_excel("cooking.xlsx")
    print("파일 저장을 완료했습니다.")
    
except Exception as e:
    print("오류가 발생했습니다:", e)
