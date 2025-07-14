import pandas as pd
import random
import datetime

# 1. 데이터 로드 및 정리
try:
    raw_df = pd.read_csv('cooking.csv', index_col=0, encoding='euc-kr')
except FileNotFoundError:
    print("cooking.csv 파일을 찾을 수 없습니다. 파일 경로를 확인해주세요.")
    exit()

df = raw_df.rename(columns={
    'product': '상품코드',
    'class': '소분류_한글명',
    'code': '소분류(품목)',
    'name': '상품명'
})

personas = {
    "건강지향_1인가구": {
        "preferences": [
            {"소분류(품목)": ['CR', 'PT', 'SP'], "preference_weight": 5},  # 채소
            {"소분류(품목)": ['LM', 'AP'],       "preference_weight": 2},  # 과일
            {"소분류(품목)": ['SO', 'SH', 'SQ'],       "preference_weight": 2},  # 해산물
            {"소분류(품목)": ['CB', 'EG'],               "preference_weight": 3},  # 닭가슴살, 계란
        ],
        "prob_persona_choice": 0.95
    },

    "육류_매니아": {
        "preferences": [
            {"소분류(품목)": ['PB', 'BF', 'CT'],       "preference_weight": 6},  # 돼지고기, 소고기
            {"소분류(품목)": ['GA', 'ON', 'GO', 'LE', 'PL', 'CR', 'PT', 'KM', 'SM'], "preference_weight": 3},  # 곁들임 채소
            {"소분류(품목)": ['GP', 'SE'],               "preference_weight": 2},  # 조미료
            {"소분류(품목)": ['SA'],               "preference_weight": 1},  # 소금
        ],
        "prob_persona_choice": 0.95
    },

    "해산물_애호가": {
        "preferences": [
            {"소분류(품목)": ['MK', 'PO', 'YC', 'SH', 'SQ', 'AC', 'SO', 'SC', 'WK', 'CL', 'MU', 'LV', 'SW', 'KE', 'FR'], "preference_weight": 5}, # 모든 수산물
            {"소분류(품목)": ['MK', 'PO', 'YC'], "preference_weight": 4},  # 물고기류
            {"소분류(품목)": ['SH', 'SC', 'CL', 'MU'], "preference_weight": 3},  # 갑각류/조개류
            {"소분류(품목)": ['SS', 'GP', 'CP', 'FS', 'SE'], "preference_weight": 3},  # 조미료
            {"소분류(품목)": ['SA', 'CW'],               "preference_weight": 2},  # 소금 외
        ],
        "prob_persona_choice": 0.95
    },

    "요리초보_간편식선호": {
        "preferences": [
            {"소분류(품목)": ['DS', 'MS', 'GP'], "preference_weight": 3},  # 초보 조미료
            {"소분류(품목)": ['HA', 'PB', 'EG', 'LV', 'PT', 'TF'], "preference_weight": 5},  # 초보 요리재료
            {"소분류(품목)": ['SA', 'CW', 'SU', 'SE'],               "preference_weight": 1},  # 소금 외
        ],
        "prob_persona_choice": 0.9
    },

    "대가족_주부": {
        "preferences": [
            {"소분류(품목)": ['RI', 'MG'],     "preference_weight": 4},  # 쌀, 잡곡
            {"소분류(품목)": ['TF', 'PB', 'CT', 'EG', 'BF', 'MK'],     "preference_weight": 5},  # 주재료
            {"소분류(품목)": ['ON', 'GA', 'GO', 'NC', 'LE', 'SN', 'CR', 'PT', 'KM', 'SM', 'BS', 'ZU', 'LV', 'SW'],     "preference_weight": 4},  # 반찬재료
            {"소분류(품목)": ['SS', 'GP', 'DP', 'SA', 'CP'],   "preference_weight": 3},  # 조미료
            {"소분류(품목)": ['SA', 'SU', 'FS', 'VI', 'CW', 'SU', 'SE', 'MS', 'DS'],               "preference_weight": 2},  # 소금 외
        ],
        "prob_persona_choice": 0.9
    },

    "베이킹_디저트매니아": {
        "preferences": [
            {"소분류(품목)": ['EG', 'HO', 'SU', 'SY'], "preference_weight": 5}, # 꿀, 설탕, 시럽
            {"소분류(품목)": ['AP', 'LM'],       "preference_weight": 3},  # 사과, 레몬
            {"소분류(품목)": ['GA', 'HA'],     "preference_weight": 1}, # 보조재료
        ],
        "prob_persona_choice": 0.95
    },

    "전통음식_선호": {
        "preferences": [
            {"소분류(품목)": ['ON', 'GA', 'GO', 'CH', 'LE', 'NC', 'PL', 'CR', 'SP', 'EM', 'KM', 'SM', 'TF', 'BS', 'ZU'],       "preference_weight": 6},  # 채소
            {"소분류(품목)": ['SS', 'GP', 'DP', 'CP'],   "preference_weight": 3},  # 조미료
            {"소분류(품목)": ['SA', 'CW', 'SU', 'SE', 'FS', 'VI'],               "preference_weight": 1},  # 소금 외
            {"소분류(품목)": ['RI', 'CT', 'BF'],   "preference_weight": 3},  # 쌀, 육류
            {"소분류(품목)": ['PO', 'YC', 'SQ', 'AC', 'CL', 'MU', 'LV', 'SW', 'KE'],               "preference_weight": 5},  # 수산물
        ],
        "prob_persona_choice": 0.95
    },

    "매운맛_중독자": {
        "preferences": [
            {"소분류(품목)": ['GP', 'CH'],               "preference_weight": 6},  # 고추 재료
            {"소분류(품목)": ['PB', 'SO', 'MU', 'CT'],   "preference_weight": 4},  # 주재료
            {"소분류(품목)": ['GA', 'ON', 'GO', 'EG'],   "preference_weight": 2},  # 마늘, 양파, 대파, 계란
            {"소분류(품목)": ['BS', 'TF'],               "preference_weight": 1},  # 보조재료
            
        ],
        "prob_persona_choice": 0.95
    },

    "자취생_대학생": {
        "preferences": [
            {"소분류(품목)": ['LV', 'EG', 'HA', 'PB'],             "preference_weight": 4},  # 간편재료
            {"소분류(품목)": ['EM', 'TF'],             "preference_weight": 2},  # 간편부재료
            {"소분류(품목)": ['GP', 'SE', 'MS'],     "preference_weight": 1},  # 간편조미료
        ],
        "prob_persona_choice": 1
    },

    "캠핑족": {
        "preferences": [
            {"소분류(품목)": ['PB', 'BF', 'CT'], "preference_weight": 4},    # 고기
            {"소분류(품목)": ['LE', 'PL'],             "preference_weight": 2},  # 고기채소
            {"소분류(품목)": ['ON', 'GA', 'PT', 'KM', 'SM'],     "preference_weight": 1},  # 요리채소
            {"소분류(품목)": ['GP', 'SE', 'SA'],     "preference_weight": 1},  # 조미료
        ],
        "prob_persona_choice": 0.95
    }
}
# --------------------------------------------------------------------------
# (이하 코드는 변경 없음)
# --------------------------------------------------------------------------

# 3. 시뮬레이션 설정
NUM_USERS = 10000
NUM_PURCHASES = 10
ITEMS_MIN = 2
ITEMS_MAX = 5

user_map = {f"user{i+1}": random.choice(list(personas.keys())) for i in range(NUM_USERS)}

# 4. 구매 기록 생성 함수
def generate_logs(products, personas_map, user_map, num_purchases, min_items, max_items):
    all_logs = []
    timestamp = datetime.datetime(2023, 1, 1, 10, 0, 0)
    EXPLORATION_RATE = 0.15
    purchase_id_counter = 1

    for user_id, persona_name in user_map.items():
        persona = personas_map[persona_name]
        
        for _ in range(num_purchases):
            num_items = random.randint(min_items, max_items)
            cart = []
            cart_codes = set()

            for _ in range(num_items):
                selected_item = None
                use_persona = (random.random() < persona["prob_persona_choice"])

                if use_persona and random.random() > EXPLORATION_RATE:
                    rule = random.choices(
                        persona["preferences"], 
                        weights=[p.get("preference_weight", 1) for p in persona["preferences"]], 
                        k=1
                    )[0]
                    
                    candidates = products.copy()
                    
                    if rule.get("소분류(품목)"):
                        codes = rule["소분류(품목)"]
                        filter_cond = candidates['소분류(품목)'].isin(codes) if isinstance(codes, list) else candidates['소분류(품목)'] == codes
                        candidates = candidates[filter_cond]

                    if rule.get("상품명_키워드") and not candidates.empty:
                        keywords = '|'.join(rule["상품명_키워드"])
                        candidates = candidates[candidates['상품명'].str.contains(keywords, case=False, na=False)]
                    
                    options = candidates[~candidates['상품코드'].isin(cart_codes)]
                    if not options.empty:
                        selected_item = options.sample(1).iloc[0]
                
                if selected_item is None:
                    options = products[~products['상품코드'].isin(cart_codes)]
                    if not options.empty:
                         selected_item = options.sample(1).iloc[0]
                    else:
                        break
                
                cart.append({
                    "상품코드": selected_item['상품코드'], "상품명": selected_item['상품명'],
                    "소분류(품목)": selected_item['소분류(품목)'], "소분류_한글명": selected_item['소분류_한글명']
                })
                cart_codes.add(selected_item['상품코드'])
            
            if cart:
                all_logs.append({
                    "user_id": user_id, 
                    "persona": persona_name, 
                    "purchase_id": purchase_id_counter,
                    "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"), 
                    "items": cart
                })
                purchase_id_counter += 1
                
            timestamp += datetime.timedelta(minutes=random.randint(5, 180))
    return all_logs

# 5. 데이터 생성 실행 및 저장
print("--- 구매 기록 시뮬레이션 시작 ---")
logs = generate_logs(
    products=df,
    personas_map=personas,
    user_map=user_map,
    num_purchases=NUM_PURCHASES,
    min_items=ITEMS_MIN,
    max_items=ITEMS_MAX
)
print(f"총 {len(logs)} 건의 구매(장바구니) 기록 생성 완료.\n")

print("--- 최종 학습용 데이터프레임 생성 시작 ---")
rows = []
for log in logs:
    for item in log['items']:
        rows.append({
            'user_id': log['user_id'], 'persona': log['persona'], 'purchase_id': log['purchase_id'],
            'timestamp': log['timestamp'], '소분류(품목)': item['소분류(품목)'],
            '소분류_한글명': item['소분류_한글명'], '상품코드': item['상품코드'],
        })

result_df = pd.DataFrame(rows)
outfile = "final_learning.csv"
result_df.to_csv(outfile, index=False, encoding='euc-kr')

print(f"\n최종 학습용 데이터가 '{outfile}' 파일로 저장되었습니다.")
print("\n--- 최종 학습용 데이터 샘플 (상위 5개) ---")
print(result_df.head())
print("\n--- 페르소나별 주요 구매 소분류(한글명) Top 5 ---")
for p_name in sorted(personas.keys()):
    top_items = result_df[result_df['persona'] == p_name]['소분류_한글명'].value_counts().nlargest(5)
    print(f"\n# {p_name}:")
    print(top_items if not top_items.empty else "구매 기록 없음")