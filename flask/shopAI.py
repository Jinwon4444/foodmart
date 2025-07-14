import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import csv
import os
from sklearn.metrics.pairwise import cosine_similarity
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

# shoppingAI 클래스
class shoppingAI :
    
    def similarity(self) :
        
        # 해당 자료가 이미 있는지 확인
        file_path1 = 'static\\save\\data\\shopping.pkl'
        file_path2 = 'static\\save\\data\\item_similarity.pkl'
        if os.path.exists(file_path1) and os.path.exists(file_path2) :
            print("자료파일이 존재합니다.")
            return
        else :
            # 소분류 텍스트 파일을 리스트로 불러오기
            file_path = "static\\save\\data\\class_code.txt"
            my_list = []

            # 각 줄을 리스트 요소로 저장, UTF8형식 불러오기
            with open(file_path, "r", encoding='UTF8') as file:
                test_list = file.readlines()
            
            # 리스트 요소 {코드 : 소분류}로 가공
            for data in test_list :
                value, code = data.split()
                my_list.append(value)

            # csv 파일을 리스트로 불러오기
            file = open("static\\save\\data\\purchase_AI_data.csv", "r")
            # file = open("AI_test_data01.csv", "r")

            datas = csv.reader(file)
            
            # --- 데이터 준비 ---
            dict_data = { }
            code_data = { }

            for code in my_list :
                code_data[code.replace("\n", "")] = 0
            print(code_data)

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
            df_shopping.to_pickle('static\\save\\data\\shopping.pkl')

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
            item_similarity_df.to_pickle('static\\save\\data\\item_similarity.pkl')

            # 유사도 확인용 파일
            item_similarity_df.to_csv("static\\save\\data\\item_similarity.csv", encoding="euc-kr")
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
    
    
    # 개인 유사도 계산 후 데이터 리턴
    def Calsimilarity(self, userid) :
        # Seaborn의 기본 스타일 설정 (그래프를 더 예쁘게 만들어줍니다)
        plt.rc('font', family='Malgun Gothic')
        plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지
        
        # 피클 파일에서 데이터프레임 불러오기
        df_shopping = pd.read_pickle('static\\save\\data\\shopping.pkl')
        item_similarity_df = pd.read_pickle('static\\save\\data\\item_similarity.pkl')
        
        # --- 추천 생성 단계 ---
        # '고객(추천대상)'에게 상품 추천하기
        target_customer_id = userid
        target_customer_purchases = df_shopping.loc[target_customer_id] # 고객의 구매 내역
        customer_shopping = target_customer_purchases[target_customer_purchases > 0]    # 구매한 상품
        print(target_customer_purchases)
        print(customer_shopping.index.tolist())  # 구매한 상품만 출력
        print(customer_shopping.nlargest(3))     # 구매한 상품 최대구매 두번째까지
        print(customer_shopping.mean())     # 구매한 상품 평균
        print(customer_shopping.mean() - customer_shopping.std())   # 구매한 상품 평균 - 표준편차
        print(customer_shopping.mean() + customer_shopping.std())   # 구매한 상품 평균 + 표준편차
        print("\n")
        
        # 추천 점수 계산
        recommendations = {} # 추천 상품과 예상 점수를 담을 딕셔너리
        
        # 고객이 구매한 모든 상품에 대해 반복
        for purchased_item in target_customer_purchases[target_customer_purchases > 0].index :
            
            # 해당 상품과 다른 모든 상품들의 유사도를 가져옴
            similar_items = item_similarity_df[purchased_item]
            
            # 구매량에 따른 중요도
            if target_customer_purchases[purchased_item] <= round(customer_shopping.mean() - customer_shopping.std()) : 
                increase = 0.5
            elif target_customer_purchases[purchased_item] <= customer_shopping.mean() :
                increase = 0.7
            elif target_customer_purchases[purchased_item] <= round(customer_shopping.mean() + customer_shopping.std()) :
                increase = 1.5
            else : 
                increase = 4
                
            # 유사한 상품들 중에서 고객6이 아직 구매하지 않은 상품을 찾음
            for item_to_recommend, similarity_score in similar_items.items():
                if target_customer_purchases[item_to_recommend] == 0 and similarity_score > 0.2: # 아직 안 샀고, 유사도가 0.2보다 크면
                    # 추천 점수 누적: 이미 추천 목록에 있으면 점수를 더하고, 없으면 새로 추가
                    # 여기서는 단순히 유사도 점수를 더하지만, 실제로는 구매한 상품의 중요도 등을 곱할 수도 있음(적용)
                    recommendations[item_to_recommend] = recommendations.get(item_to_recommend, 0) + ( similarity_score * increase )
                elif target_customer_purchases[item_to_recommend] == 0 and similarity_score > 0.1:  # 아직 안 샀고, 유사도가 0.1보다 크고 0.2보다 작으면
                    recommendations[item_to_recommend] = recommendations.get(item_to_recommend, 0) + ( similarity_score * increase )/4
           
        
        # 추천 결과 정렬 및 출력
        # 예상 점수가 높은 순으로 정렬
        sorted_recommendations = sorted(recommendations.items(), key=lambda item: item[1], reverse=True)
        
        
        print(f"--- '{target_customer_id}'에게 추천하는 상품 목록 (예상 점수 순) ---")
        if sorted_recommendations:
            # 추천 후보 목록 생성 (아이템, 추천점수 저장)
            score_list = []
            item_list = []
            count = 0
            for item, score in sorted_recommendations:
                if score > 2 and count < 5 :
                    score_list.append({
                        "item": item,
                        "lift": score
                    })
                    item_list.append(item)
                    print(f"상품: {item}, 추천 점수: {score:.2f}") # 소수점 둘째 자리까지
                    count += 1
            
            # 딕셔너리로 그래프 작성 시 판다스 최적
            df_score = pd.DataFrame(score_list)
            
            # Seaborn을 이용한 가로 막대그래프 그리기
            plt.figure(figsize=(15, 8))  # 그래프 크기 설정
            
            # sns.barplot을 사용하여 막대그래프 생성
            # y축에 규칙 레이블, x축에 향상도 값을 지정합니다.s
            barplot = sns.barplot(
                x='item',
                y='lift', 
                data=df_score,
                hue='item', legend=False,
                palette='viridis_r'  # 색상 팔레트 지정 (기존 히트맵과 통일)
            )
            
            # 막대 위에 실제 향상도 값 표시
            for p in barplot.patches:
                height = p.get_height()
                plt.text(p.get_x() + p.get_width() / 2,     # x축 위치
                         height + 0.05,                      # y축 위치
                         f'{height:.2f}', # 소수점 둘째 자리까지 표시
                         ha='center', va='bottom',
                         fontsize=15)
        
            # 그래프 제목 및 레이블 설정
            plt.title(f'{target_customer_id} 추천 상품 (유사도 기준)', fontsize=20)
            plt.xticks(fontsize=14, rotation=45)
            plt.xlabel('추천 상품', fontsize=16)
            plt.ylabel('유사도', fontsize=16)
            plt.grid(axis='x', linestyle='--', alpha=0.6) # x축 그리드 추가하여 가독성 향상
            plt.margins(x=0.05, y=0.1)  # 그래프 안쪽 여백
            plt.tight_layout() # 레이블이 잘리지 않도록 조정
            
            # 세이브폴더에 그래프 저장 후 show
            save_url = f'{userid}_similarity.png'
            save_path = os.path.join('static\\save\\histogram', save_url)
            plt.savefig(save_path, dpi=300)
            url = f'static\\save\\histogram\\{save_url}'
            
            plt.show()
        
        # 맨 마지막 부분 수정
        if sorted_recommendations:
            # 메인에 보낼 파라미터 리스트
            main_parameters = []
            main_parameters.append(item_list)
            main_parameters.append(url)
            print(main_parameters[0], main_parameters[1])
            
            return main_parameters
        else:
            print("추천할 상품이 없습니다.")
            # 추천 상품이 없을 때도 일관된 형태로 반환해주는 것이 좋습니다.
            return [[], None] # [빈 리스트, URL 없음]
        
        
    # 유사도 결과 출력
    def ResultSimilarity(self, userid) :
        # 유사도 파일 확인
        self.similarity()
        
        sorted_recommend_file = "static\\save\\data\\sorted_recommend.pkl"
        sorted_recommend = { }
        
        try:
            with open(sorted_recommend_file, 'rb') as file:
                sorted_recommend = pickle.load(file)
                print("파일에서 데이터를 성공적으로 불러왔습니다.")
                
        except (FileNotFoundError, EOFError) :
            print("정보 : 파일이 없거나 비어있어 새로 시작합니다.")
            # sorted_recommend는 맨 위에서 정의한 {}를 그대로 사용
        
        # 파일에 해당 유저의 데이터가 있는지 확인 (없으면 except에 이어진 빈 sort딕셔너리 그대로)
        if userid in sorted_recommend:
            print(f"{userid}의 추천상품 자료가 이미 존재합니다.")
            
            main_parameters = [
                sorted_recommend[userid],
                f'static\\save\\histogram\\{userid}_similarity.png'
            ]
            print(main_parameters[0], main_parameters[1])
            return main_parameters
        else:
            print(f"{userid}의 추천 데이터를 새로 계산합니다...")
            
            # Calsimilarity를 호출하여 계산만 수행
            main_parameters = self.Calsimilarity(userid)
            
            # Calsimilarity가 반환한 결과에서 item_list를 추출
            # 추천된 상품이 있을 경우에만 저장 로직 실행
            if main_parameters and main_parameters[0]:
                item_list = main_parameters[0]
                
                sorted_recommend[userid] = item_list
                
                with open(sorted_recommend_file, 'wb') as file:
                    pickle.dump(sorted_recommend, file)
                    print(f"'{sorted_recommend_file}' 파일에 {userid}의 데이터를 저장했습니다.")
            
            return main_parameters


class associatedRules :
    # 연관규칙을 읽어 들인다.
    def ReadRule(self, rulefile) :
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
    def ParseRecommand(self, csvname, rulefile) :
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
        min_support = 0.005
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
                    pickle.dump(rules, f)            
                return rules
        
    # 주어진 상품코드에 대한 다른 상품 추천 함수
    # N=3 : 3개의 상품을 추천. 비 설정시 기본수치
    def GetRecommand(self, item_code: str, rules_df: pd.DataFrame, N=3):
        recommendations = []
        antecedent_set = frozenset([item_code])
        
        # 추천 후보 목록 생성 (아이템, 향상도 저장)
        candidate_rules = []
        
        print(rules_df)
        
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
        
        
        # candidate_rules 리스트가 비어있는지 확인
        if not candidate_rules:
            return []
        
        # 신뢰도와 향상도가 가장 높은 순으로 정렬하고, 중복 아이템은 첫 번째 것만 남김
        df_reco = pd.DataFrame(candidate_rules)
        df_reco = df_reco.sort_values(by=['lift'], ascending=False).drop_duplicates(subset=['item'])
        
        # 최종 추천 목록을 딕셔너리 리스트로 변환
        recommendations = df_reco.to_dict('records')
        
        return recommendations[:N]


    # 연관 규칙을 이용하여 히트맵을 그린다.
    def DrawHeatMap(self, rules) :
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
    def DrawLiftBarChart(self, reco_list, my_list, target_item, target_item_class):
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

        # reco_list가 비어있으면 함수가 호출되지 않으므로, 이 조건문은 제거하거나
        # reco_list에 대한 검사로 바꾸는 것이 더 적절합니다.
        if not reco_list:
            print("시각화할 추천 목록이 없습니다.")
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
        plt.title(f'{target_item_class} 구매 시 추천 상품 (향상도 기준)', fontsize=20)
        plt.xticks(ticks=range(len(df_reco)), labels=tick_names_list, fontsize=14)
        plt.xlabel('추천 상품', fontsize=16)
        plt.ylabel('Lift (향상도)', fontsize=16)
        plt.grid(axis='x', linestyle='--', alpha=0.6) # x축 그리드 추가하여 가독성 향상
        plt.margins(x=0.05, y=0.1)  # 그래프 안쪽 여백
        plt.tight_layout() # 레이블이 잘리지 않도록 조정
        
        # 세이브폴더에 그래프 저장 후 show
        save_url = f'{target_item}_Lift.png'
        save_path = os.path.join('static\\save\\histogram', save_url)
        plt.savefig(save_path, dpi=300)
        url = f'static\\save\\histogram\\{save_url}'
        
        plt.show()
        
        return url
    
    
    def Recommendation(self, target_item) :     # 같은 클래스에서 다른 함수 사용 시 사용하는 함수에 self
        print(target_item)
        
        recommend_file = "static\\save\\data\\recommend.pkl"
        recommend = { }
        
        # 히스토그램 주소
        file_path = f'static\\save\\histogram\\{target_item}_Lift.png'
        
        try:
            with open(recommend_file, 'rb') as file:
                recommend = pickle.load(file)
                print("파일에서 데이터를 성공적으로 불러왔습니다.")
                
        except (FileNotFoundError, EOFError) :
            print("정보 : 파일이 없거나 비어있어 새로 시작합니다.")
            # sorted_recommend는 맨 위에서 정의한 {}를 그대로 사용
        
        # 파일에 해당 상품의 데이터가 있는지 확인 (없으면 except에 이어진 빈 sort딕셔너리 그대로)
        if target_item in recommend:
            print(f"{target_item}의 추천상품 자료가 이미 존재합니다.")
            
            return_list = [recommend[target_item], file_path]
            print(return_list[0], return_list[1])
            return return_list
        else:
            print(f"{target_item}의 추천 데이터를 새로 계산합니다...")
            
            # 소분류 텍스트 파일을 리스트로 불러오기
            file_path = "static\\save\\data\\class_code.txt"
            my_list = { }

            # 각 줄을 리스트 요소로 저장, UTF8형식 불러오기
            with open(file_path, "r", encoding='UTF8') as file:
                test_list = file.readlines()
            
            # 리스트 요소 {코드 : 소분류}로 가공
            for data in test_list :
                value, code = data.split()
                my_list[code] = value
            
            # 연관규칙을 읽어 들인다.
            rulename = "static\\save\\data\\rules.pkl"
            rules = self.ReadRule(rulename)
            if rules is None :
                # 연관규칙이 없으면 연관규칙을 생성한다.
                rules = self.ParseRecommand("static\\save\\data\\purchase_AI_data.csv", rulename)
                
            if rules is None :
                print("연관 규칙을 찾을 수 없습니다.")
            else :
                self.DrawHeatMap(rules)
            
                # 실제 상품 추천 클래스명
                target_item_class = my_list[target_item]
                # 해당 상품 reco_list를 받아옴
                reco_list = self.GetRecommand(target_item, rules, N=7)
                print(f"\n--- {target_item_class} 구매 시 추천 상품군 ---")
            
                
            # index 반환용
            item_list = []
            return_list = []
            
            # 리스트가 비었는지 확인 후 "None" 텍스트 저장
            if not reco_list : 
                recommend[target_item] = "None"
                return_list.append(recommend[target_item])
            else :
                for reco in reco_list:
                    print(f"  - 추천 상품: {reco['item']}, 향상도: {reco['lift']:.2f}")
                    item_list.append(reco["item"])
                url = self.DrawLiftBarChart(reco_list, my_list, target_item, target_item_class)
                return_list.append(item_list)
                return_list.append(url)
                
                print("상품별 추천 :", item_list)
            
                recommend[target_item] = item_list
                
            # 추천상품 있건 없건 저장
            with open(recommend_file, 'wb') as file:
                pickle.dump(recommend, file)
                print(f"'{recommend_file}' 파일에 {target_item}의 데이터를 저장했습니다.")
                
            return return_list
        