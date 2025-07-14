# 제품간 유사도 시뮬레이터
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import seaborn as sns
import csv


# 텍스트 파일을 리스트로 불러오기
file_path = "collabo.txt"

# 각 줄을 리스트 요소로 저장, UTF8형식 불러오기
with open(file_path, "r", encoding='UTF8') as file:
    collabo_list = file.readlines()

# csv 파일을 리스트로 불러오기
file = open("AI_test_data02.csv", "r")
# file = open("AI_test_data01.csv", "r")

datas = csv.reader(file)


# --- 데이터 준비 ---
dict_data = { }
code_data = { }

for code in collabo_list :
    code_data[code.replace("\n", "")] = 0
print(code_data)

name = ""
for line in datas :
    
    if line[0] == "user_id" :
        continue
    
    user_id = line[0]
    item_code = line[5]
    
    # 만약 이 유저가 dict_data에 처음 등록되는 것이라면
    if user_id not in dict_data:
        # code_data의 복사본으로 초기화해준다.
        dict_data[user_id] = code_data.copy()   # 얕은 복사
        
    # 이제 해당 유저의 item_code 카운트를 1 증가시킨다.
    dict_data[user_id][item_code] += 1

file.close()
    
# 데이터를 표(DataFrame) 형태로 변환 (고객이 행, 상품이 열) .T는 행과 열을 바꿔주는 역할
df_shopping = pd.DataFrame(dict_data).T
print("--- 초기 구매 데이터 (고객-상품 매트릭스) ---")
print(df_shopping.head())
print("\n")

# 피클로 데이터 저장
df_shopping.to_pickle('shopping.pkl')

file.close()


# --- 아이템 간 유사도 계산 단계 ---
# 상품 간의 유사도 계산을 위해, 데이터를 "상품-고객 매트릭스" 형태로 변환
# 즉, 어떤 상품을 어떤 고객들이 구매했는지를 나타내는 표로 만듭니다.
# 이는 각 상품을 하나의 "벡터"로 보고, 그 벡터들 간의 유사도를 측정하기 위함입니다.
df_item_customer = df_shopping.T # 다시 행과 열을 바꿔서 상품이 행, 고객이 열로 오도록 함

print("--- 상품-고객 매트릭스 (유사도 계산용) ---")
print(df_item_customer)
print("\n")

# 상품 간의 코사인 유사도 계산하기
# 1에 가까울수록 두 상품이 함께 구매될 가능성이 높다는 의미!
item_similarity = cosine_similarity(df_item_customer, df_item_customer)

# 계산된 유사도 행렬을 보기 쉽게 DataFrame으로 변환
item_similarity_df = pd.DataFrame(
    data=item_similarity,
    index=df_item_customer.index, # 행 이름을 상품 이름으로
    columns=df_item_customer.index # 열 이름도 상품 이름으로
)

print("--- 상품 간 유사도 ---")
print(item_similarity_df)
print("\n")

# 피클로 유사도 저장
item_similarity_df.to_pickle('item_similarity.pkl')

# 유사도 확인용 파일
item_similarity_df.to_csv("item_similarity.csv", encoding="euc-kr")
print("파일 작성이 완료되었습니다.")
print("\n")



# Seaborn의 기본 스타일 설정 (그래프를 더 예쁘게 만들어줍니다)
plt.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지

plt.figure(figsize=(20,16))

sns.heatmap(item_similarity_df, 
            annot=False,           # 셀에 숫자 표시
            cmap='YlGnBu',        # 노란색-녹색-파란색 계열의 컬러맵
            linewidths=0.5,       # 셀 사이의 간격
            linecolor='white'     # 셀 사이의 선 색상
           )

# x축 레이블(영화 제목)의 글자 크기를 7로, 45도 회전
plt.xticks(fontsize=7, rotation=45)

# y축 레이블(사용자 이름)의 글자 크기를 7로 설정
plt.yticks(fontsize=7, rotation=45)


plt.title('상품 간 유사도 히트맵', fontsize=15)
plt.show()