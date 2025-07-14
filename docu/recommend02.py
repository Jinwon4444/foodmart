"""
pip install mlxtend pandas
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import pickle
import Collaborative_Filtering02 as sim

sim = sim.similarity()

# 연관규칙을 읽어 들인다.
def ReadRule(rulefile) :
    rules = None
    try :
        with open(rulefile,"rb") as f :
            rules = pickle.load(f)
            print(f"연관규칙 파일 {rulefile} 읽기 성공...")
    except :
        return None
    return rules   
        
# 주어진 CSV 파일에 대한 유사도를 분석한 후,
# rulefile로 연관규칙 데이터를 저장한다.
# 리턴값 : None 또는 연관규칙 데이터 
def ParseRecommand(csvname,rulefile) :
    # CSV 파일을 읽는다.
    df = pd.read_csv(csvname,encoding="euc-kr")
    print(df.info())
    print("=" * 40) 
    
    # 구매번호와 상품코드를 이용하여 분석 할 새로운 데이터 프레임을 
    # 생성하다.
    df_cart = df[["purchase_id", "class_code"]]
    print(df_cart.info())
    print("=" * 40) 

    # 분석대상 상품코드가 총 몇개 인지 확인한다.    
    code_list = set(df_cart["class_code"])
    
    print(f"상품갯수 : {len(code_list)} 개")
    print(code_list)
    print("=" * 40)
    
    # 구매번호에 해당하는 상품코드를 아래와 같은 구조로 변환한다.
    # [ ["A","B"], ["A","C"].. ]
    transactions = df_cart.groupby("purchase_id")["class_code"].apply(list).tolist()
    
    # mlxtend의 TransactionEncoder를 사용해 One-Hot 인코딩된 DataFrame으로 변환한다.
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    df_trans = pd.DataFrame(te_ary, columns=te.columns_)

    # 연관 규칙을 분석한다. 
    # min_support: 최소 지지도. 전체 거래 중 최소 이 비율 이상 
    #              나타나는 아이템 집합을 찾는다.
    # 예: 6건의 거래 중 2건 이상 나타나야 하면 2/6 = 0.33
    # 데이터의 양과 특성에 따라 이 값을 조절해야 한다.
    min_support = 0.01
    frequent_itemsets = apriori(df_trans, 
        min_support = min_support, 
        use_colnames = True)    
    
    if frequent_itemsets.empty:
        print(f"'{min_support}'의 최소 지지도(min_support)를 만족하는 빈번한 아이템 집합이 없습니다.")
        print("min_support 값을 더 낮추거나 데이터가 더 필요합니다.")
        return None
    else:  
        rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.0)
    
        if rules.empty:
            print("연관 규칙을 찾을 수 없습니다. (lift > 1.0 기준)")
            return None
        else:        
            with open(rulefile,"wb") as f :
                pickle.dump(rules,f)            
            return rules
    
# 주어진 상품코드에 대한 다른 상품 추천 함수
# N=3 : 3개의 상품을 추천. 비 설정시 기본수치
def GetRecommand(item_code: str, rules_df: pd.DataFrame, N=3):
    recommendations = []
    antecedent_set = frozenset([item_code])
    
    # 추천 후보 목록 생성 (아이템, 향상도 저장)
    candidate_rules = []
    
    # 모든 규칙을 순회하며 item_code가 조건에 포함된 경우를 찾습니다.
    for _, rule in rules_df.iterrows():
        if antecedent_set.issubset(rule['antecedents']):
            # 결과에서 조건을 제외한 순수 추천 아이템만 추출
            consequent_items = rule['consequents'] - rule['antecedents']
            if consequent_items: # 결과가 비어있지 않은 경우
                for item in consequent_items:
                    # 추천 아이템, 신뢰도, 향상도를 함께 저장
                    candidate_rules.append({
                        "item": item,
                        "lift": rule['lift']
                    })
    
    # 신뢰도와 향상도가 가장 높은 순으로 정렬하고, 중복 아이템은 첫 번째 것만 남김
    df_reco = pd.DataFrame(candidate_rules)
    df_reco = df_reco.sort_values(by=['lift'], ascending=False).drop_duplicates(subset=['item'])
    
    # 최종 추천 목록을 딕셔너리 리스트로 변환
    recommendations = df_reco.to_dict('records')
    
    return recommendations[:N]


# 연관 규칙을 이용하여 히트맵을 그린다.
def DrawHeatMap(rules) :
    # 시각화에서 한글이 깨지는 것을 방지하기 위한 설정
    # 사용하는 OS에 맞는 폰트 이름을 지정
    # (예: Windows: 'Malgun Gothic', macOS: 'AppleGothic')
    try:
        plt.rc("font", family="Malgun Gothic")
        # 마이너스 기호 깨짐 방지
        plt.rcParams["axes.unicode_minus"] = False
    except:
        print("한글 폰트를 설정할 수 없습니다. 'Malgun Gothic' 또는 'AppleGothic'과 같은 폰트가 시스템에 설치되어 있는지 확인해주세요.")
        print("그래프의 한글 레이블이 깨질 수 있습니다.")
        return
    
    if rules.empty:
        print("연관 규칙을 찾을 수 없습니다. (lift > 1.0 기준)")
    else:
        # --- 3. 상관관계 매트릭스 시각화 ---
        # 1:1 관계의 단순한 규칙만 필터링
        rules_simple = rules[
            (rules['antecedents'].apply(lambda x: len(x) == 1)) &
            (rules['consequents'].apply(lambda x: len(x) == 1))
        ].copy()

        # [핵심 수정] 시각화용 데이터(rules_simple)가 비어있는지 다시 한번 확인합니다.
        if rules_simple.empty:
            print("\n[알림] 1:1 연관 규칙이 없어 히트맵을 생성할 수 없습니다.")
            print("발견된 규칙은 모두 {A,B} -> {C} 와 같은 복잡한 형태입니다.")
        else:
            # 시각화 데이터가 있을 경우에만 피벗 및 히트맵 생성
            rules_simple["antecedents"] = rules_simple["antecedents"].apply(lambda x: list(x)[0])
            rules_simple["consequents"] = rules_simple["consequents"].apply(lambda x: list(x)[0])
            lift_matrix = rules_simple.pivot(index="antecedents", columns="consequents", values="lift")

            plt.figure(figsize=(10, 8))
            sns.heatmap(lift_matrix, annot=True, fmt=".2f", cmap="viridis", linewidths=.5, cbar_kws={"label": "Lift (향상도)"})
            plt.title("Class Code 연관성 매트릭스 (Lift 기준)", fontsize=16)
            plt.xlabel("결과 상품군 (Consequents)", fontsize=12)
            plt.ylabel("조건 상품군 (Antecedents)", fontsize=12)
            plt.xticks(rotation=45)
            plt.yticks(rotation=0)
            plt.tight_layout()
            plt.show()    
  
# 향상도(Lift)가 높은 순으로 연관 규칙을 막대그래프로 시각화하는 함수
def DrawLiftBarChart(reco_list):
    """
    연관 규칙을 향상도(lift) 기준으로 정렬하여 상위 N개의 규칙을 
    가로 막대그래프로 시각화합니다.

    Args:
        rules (pd.DataFrame): 연관규칙 DataFrame
        top_n (int): 시각화할 상위 규칙의 개수
    """
    # 한글 폰트 설정 (기존 코드와 동일)
    try:
        plt.rc("font", family="Malgun Gothic")
        plt.rcParams["axes.unicode_minus"] = False
    except:
        print("한글 폰트를 설정할 수 없습니다. 'Malgun Gothic' 또는 'AppleGothic'과 같은 폰트가 시스템에 설치되어 있는지 확인해주세요.")

    if rules.empty:
        print("시각화할 연관 규칙이 없습니다.")
        return
    
    # 딕셔너리로 그래프 작성 시 판다스 최적
    df_reco = pd.DataFrame(reco_list)

    # Seaborn을 이용한 가로 막대그래프 그리기
    plt.figure(figsize=(12, 8))  # 그래프 크기 설정
    
    # sns.barplot을 사용하여 막대그래프 생성
    # y축에 규칙 레이블, x축에 향상도 값을 지정합니다.
    barplot = sns.barplot(
        x = 'item',
        y = 'lift', 
        data = df_reco, 
        hue='item', legend=False,
        palette = 'viridis_r'  # 색상 팔레트 지정 (기존 히트맵과 통일),
    )
    
    # 막대 위에 실제 향상도 값 표시
    for p in barplot.patches:
        height = p.get_height()
        plt.text(p.get_x() + p.get_width() / 2,     # x축 위치
                 height + 0.05,                      # y축 위치
                 f'{height:.2f}', # 소수점 둘째 자리까지 표시
                 ha='center', va='bottom',
                 fontsize=15)
    
    # x축 눈금 이름 리스트로 가져오기
    tick_labels = plt.gca().get_xticklabels()
    # 눈금 이름만 추출하여 리스트로 만들기
    tick_names_list = [my_list[label.get_text()] for label in tick_labels]
    print(tick_names_list)
    
    # 4. 그래프 제목 및 레이블 설정
    plt.title(f'{target_item_name} 구매 시 추천 상품 (향상도 기준)', fontsize=20)
    plt.xticks(ticks=range(len(df_reco)), labels=tick_names_list, fontsize=14)
    plt.xlabel('추천 상품', fontsize=16)
    plt.ylabel('Lift (향상도)', fontsize=16)
    plt.grid(axis='x', linestyle='--', alpha=0.6) # x축 그리드 추가하여 가독성 향상
    plt.margins(x=0.05, y=0.1)  # 그래프 안쪽 여백
    plt.tight_layout() # 레이블이 잘리지 않도록 조정
    plt.show()  
  
    
# main 함수
if __name__ == "__main__":        
    
    # 소분류 표시용도 텍스트 파일을 리스트로 불러오기
    file_path = "test.txt"
    my_list = { }

    # 각 줄을 리스트 요소로 저장, UTF8형식 불러오기
    with open(file_path, "r", encoding='UTF8') as file:
        test_list = file.readlines()
    
    # 리스트 요소 [소분류, 제품코드]로 가공
    for data in test_list :
        value, key = data.split()
        my_list[key] = value
        
    
    # 연관규칙을 읽어 들인다.
    rulename = "rules.pkl"
    rules = ReadRule(rulename)
    if rules is None :
        # 연관규칙이 없으면 연관규칙을 생성한다.
        rules = ParseRecommand("AI_test_data02.csv",rulename)
        
    if rules is None :
        print("연관 규칙을 찾을 수 없습니다.")
    else :
        DrawHeatMap(rules)
    
        # 실제 상품 추천
        target_item = "PB"
        target_item_name = my_list[target_item]
        reco_list = GetRecommand(target_item, rules, N=7)
        print(f"\n--- {target_item_name} 구매 시 추천 상품군 ---")
        if not reco_list: # 리스트가 비었는지 확인
            print("추천상품 없음")
        else :
            for reco in reco_list:
                print(f"  - 추천 상품: {reco['item']}, 향상도: {reco['lift']:.2f}")
            DrawLiftBarChart(reco_list)

        
