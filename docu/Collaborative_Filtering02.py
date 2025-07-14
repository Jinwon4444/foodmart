import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

class similarity :
    def ResultSimilarity(self, userid) :
        
        # Seaborn의 기본 스타일 설정 (그래프를 더 예쁘게 만들어줍니다)
        plt.rc('font', family='Malgun Gothic')
        plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지
        
        # 피클 파일에서 데이터프레임 불러오기
        df_shopping = pd.read_pickle('shopping.pkl')
        item_similarity_df = pd.read_pickle('item_similarity.pkl')
        
        '''
        dict_nlargest = { }
        code_list = [ ]
        for i in range(len(item_similarity_df.columns)) :
            nlargest = item_similarity_df.iloc[i].nlargest(6)
            
            count = 1   # 첫번째는 제목이므로 1부터 시작
            c_list = code_list.copy()
            for num in nlargest :
                if num > 0.2 and num < 0.99 :
                    c_list.append(nlargest.index.tolist()[count]) 
                    count += 1
            dict_nlargest[nlargest.index.tolist()[0]] = c_list
            # 추가한 키와 값 출력
            print(nlargest.index.tolist()[0], dict_nlargest[nlargest.index.tolist()[0]])            
        
        
        # 피클로 딕셔너리 저장
        # try-catch 대신 쓸 수 있음. 자동으로 닫아줌
        with open("dict_simple.pkl", "wb") as f :
            pickle.dump(dict_nlargest, f)
        print("파일에 dict_nlargest 데이터를 저장하였습니다.")
        print("\n")
        '''
        
        
        # --- 추천 생성 단계 ---
        # '고객(추천대상)'에게 상품 추천하기
        target_customer_id = userid
        target_customer_purchases = df_shopping.loc[target_customer_id] # 고객333의 구매 내역
        customer_shopping = target_customer_purchases[target_customer_purchases > 0]    # 구매한 상품
        print(target_customer_purchases)
        print(customer_shopping.index.tolist())  # 구매한 상품만 출력
        print(customer_shopping.nlargest(3))     # 구매한 상품 최대구매 두번째까지
        print(customer_shopping.mean())     # 구매한 상품 평균
        print(customer_shopping.mean() - customer_shopping.std())   # 구매한 상품 평균 - 표준편차
        print(customer_shopping.mean() + customer_shopping.std())   # 구매한 상품 평균 + 표준편차
        print("\n")
        
        # 추천 점수 계산
        #  - 고객6이 이미 구매한 상품들과 유사도가 높은 다른 상품들을 찾는다.
        #  - 고객6이 아직 구매하지 않은 상품에 대해서만 추천 점수를 계산한다.
        #  - 간단한 방법: 고객6이 구매한 각 상품 A에 대해, A와 다른 상품 B의 유사도를 가져와서 아직 구매하지 않은 B에 대한 점수로 누적한다
        
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
            count = 0
            for item, score in sorted_recommendations:
                if score > 2 and count < 5 :
                    score_list.append({
                        "item": item,
                        "lift": score
                    })
                    print(f"상품: {item}, 추천 점수: {score:.2f}") # 소수점 둘째 자리까지
                    count += 1
            
            # 딕셔너리로 그래프 작성 시 판다스 최적
            df_score = pd.DataFrame(score_list)
            
            # Seaborn을 이용한 가로 막대그래프 그리기
            plt.figure(figsize=(15, 8))  # 그래프 크기 설정
            
            # sns.barplot을 사용하여 막대그래프 생성
            # y축에 규칙 레이블, x축에 향상도 값을 지정합니다.
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
        
            # 4. 그래프 제목 및 레이블 설정
            plt.title(f'{target_customer_id} 추천 상품 (유사도 기준)', fontsize=20)
            plt.xticks(fontsize=14, rotation=45)
            plt.xlabel('추천 상품', fontsize=16)
            plt.ylabel('유사도', fontsize=16)
            plt.grid(axis='x', linestyle='--', alpha=0.6) # x축 그리드 추가하여 가독성 향상
            plt.margins(x=0.05, y=0.1)  # 그래프 안쪽 여백
            plt.tight_layout() # 레이블이 잘리지 않도록 조정
            plt.show()
            
            save_path = os.path.join('D:\jin\python\14.Project\flask\static\img', f'{userid}_similarity.png')
            plt.savefig(save_path)
            
        else:
            print("추천할 상품이 없습니다.")


