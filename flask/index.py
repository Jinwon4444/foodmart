from flask import Flask, session, request, redirect, url_for, render_template
import shopAI as AI
import shoppingDTO as DTO

app = Flask(__name__)
shopDTO = DTO.itemDTO()
shop = AI.shoppingAI()
rules = AI.associatedRules()

# 세션을 사용하려면 반드시 secret_key를 설정해야 합니다.
# 이 키는 세션 데이터를 암호화하는데 사용됩니다.
app.secret_key = 'ezen'

# 링크 시 함수 이름으로
# 메인화면 보기
@app.route("/")
def home() :
    if session.get("userid") :
        main_parameters = shop.ResultSimilarity(session["userid"])
        items = shopDTO.list(main_parameters[0])
        login = session.get("userid")
        return render_template("main.html", login=login, items=items, url=main_parameters[1])
    else :
        login = None
        test = ["삼겹살", "팽이버섯"]
        items = shopDTO.list(test)
        return render_template("main.html", login=login, items=items)

@app.route("/login")
def login() :
    if session.get("userid") :
        error_message = "비정상적인 접근입니다."
        return render_template('alert.html', message=error_message, redirect="/")
    else :
        return render_template("login.html")

@app.route("/loginok", methods=['POST'])
def loginok() :
    if session.get("userid") :
        error_message = "비정상적인 접근입니다."
        return render_template('alert.html', message=error_message, redirect="/")
    
    userid = request.form['userid'].strip()
    userpw = request.form['userpw'].strip()
    
    loginOK = shopDTO.loginok(userid, userpw)
    print(loginOK)
    
    # 로그인 성공 시, 세션에 사용자 정보 저장
    if loginOK is True :
        session['userid'] = userid
    else :
        loginCheck("아이디 또는 비밀번호가 다릅니다.")
    
    return redirect("/")

@app.route('/logout')
def logout():
    session.pop('userid', None)
    return redirect("/")

# 소분류 창 보기
@app.route("/subclass")
def subclass() :
    if session.get("userid") :
        login = session.get("userid")
    else :
        login = None

    clss  = request.args.get("clss")
    items = shopDTO.subclass(clss)
    return render_template("subclass.html", login=login, items=items, clss=clss)

# 제품 검색
@app.route("/search")
def search() :
    if session.get("userid") :
        login = session.get("userid")
    else :
        login = None
        
    name = request.args.get("pname")
    
    # 함수 한번 호출로 해결하기
    items = shopDTO.search(name)
    if not items :
        error_message = "검색된 제품이 없습니다."
        return render_template('alert.html', message=error_message, redirect="/")
    
    # 클래스 저장용 리스트
    select_list = [items[0].clss]
    for i in range(1, len(items)) :
        if items[i].clss not in select_list :
            select_list.append(items[i].clss)
    
    return render_template("search.html", login=login, items=items, name=name, clss=select_list, clss_len=len(select_list))

# 제품 상세 창 보기
@app.route("/detail")
def detail() :
    if session.get("userid") :
        login = session.get("userid")
    else :
        login = None
    
    code = request.args.get("code")
    select_code = code[:2]
    vo = shopDTO.view(code)
    
    # 해당 제품의 코드만 받아와 연관규칙 확인
    return_list = rules.Recommendation(select_code)    # 첫번째는 리스트, 두번째는 url
    
    # 추천상품이 비었을 경우
    if return_list is [] :
        return render_template("detail.html", vo=vo)
    
    # 추천상품이 빈 데이터 저장을 확인했을 경우
    if return_list[0] == "None" :
        itemlist = shopDTO.recommend(select_code)
        return render_template("detail.html", vo=vo, itemlist=itemlist)
    else :
        itemlist = shopDTO.recommend(return_list[0])
    
    return render_template("detail.html", login=login, vo=vo, itemlist=itemlist, url=return_list[1])

# 장바구니 창 보기
@app.route("/basket")
def basket() :
    login = loginCheckUrl("로그인이 필요합니다", "login")
    if login :
        return login
    
    login = session.get("userid")
    
    items = shopDTO.basketView(login)
    return render_template("basket.html", login=login, userid=login, items=items)

# 장바구니 추가
@app.route("/basketinsert")
def basketInsert() :
    login = loginCheckUrl("로그인이 필요합니다", "login")
    if login :
        return login
    
    login = session.get("userid")
    
    code = request.args.get("code")
    num = request.args.get("num")
    
    if shopDTO.basketCheck(login, code) is True :
        error_message = "제품이 장바구니에 이미 들어있습니다."
        redirect_url = url_for('basket')
        return render_template('alert.html', message=error_message, redirect=redirect_url)
    
    shopDTO.basketInsert(login, code, num)
    
    message = "제품을 장바구니에 추가했습니다."
    return render_template('alert.html', login=login, message=message)

# 장바구니 삭제
@app.route("/basketdelete")
def basketDelete() :
    login = loginCheckUrl("로그인이 필요합니다", "login")
    if login :
        return login
    
    login = session.get("userid")
    
    if login != request.args.get("id") :
        error_message = "비정상적인 접근입니다."
        redirect_url = url_for('logout')
        return render_template('alert.html', message=error_message, redirect=redirect_url)
    
    code_list = []
    try:
        # 쉼표로 분리해서 리스트 화
        code_list = request.args.get("codelist").split(',')
    except ValueError:
        print("잘못된 형식의 데이터가 수신되었습니다")
    
    shopDTO.basketDelete(login, code_list) 
    
    return redirect("/basket")

# 제품 주문
@app.route("/basketorder")
def basketOrder() :
    login = loginCheckUrl("로그인이 필요합니다", "login")
    if login :
        return login
    
    login = session.get("userid")
    
    if login != request.args.get("id") :
        error_message = "비정상적인 접근입니다."
        redirect_url = url_for('logout')
        return render_template('alert.html', message=error_message, redirect=redirect_url)
    
   
    orderlist_str = request.args.get('orderlist')
    order_items = orderlist_str.split(',')

    processed_orders = []
    code_list = []
    for item in order_items:
        try:
            product_id, quantity, price = item.split(':')
            
            # 주문내역 파라미터
            processed_orders.append({
                'product_id': product_id,
                'quantity': quantity,
                'price': price
            })
            
            # 장바구니 삭제 파라미터
            code_list.append(product_id)
        except ValueError:
            # "1:2:3" 형식이 아닌 데이터가 들어왔을 때의 예외 처리
            print(f"잘못된 형식의 데이터가 수신되었습니다: {item}")
            continue
    
    # 제품 주문 후 장바구니에서 소거
    shopDTO.basketOrder(login, processed_orders)
    shopDTO.basketDelete(login, code_list)
    
    print(f"사용자 ID {login}의 주문 내역 :", processed_orders)
    
    message = "제품을 장바구니에 추가했습니다."
    redirect_url = url_for('basket')
    return render_template('alert.html', message=message, redirect=redirect_url)

# 주문 내역 리스트 보기
@app.route("/orderlist")
def orderList() :
    login = loginCheckUrl("로그인이 필요합니다", "login")
    if login :
        return login
    
    login = session.get("userid")
    
    try :
        items = shopDTO.orderList(login)    
    
        order_list = []
        order_data = {
            "orderno": items[0].orderno,
            "orderdate": items[0].orderdate,
            "productsid": items[0].productsid,
            "productsname": items[0].productsname,
            "totalprice": items[0].orderprice,
            "productscount" : 1
        }
        
        for i in range(1, len(items)) :
            item = items[i]
            
            # 주문번호가 같은경우 가격과 카운트 누적
            if item.orderno == order_data["orderno"]:
                order_data["totalprice"] += item.orderprice
                order_data["productscount"] += 1
                
            # 주문번호가 다른 경우 (새로운 그룹 시작)
            else:
                order_list.append(order_data)

                # 현재 아이템으로 새로운 그룹(current_group)을 시작
                order_data = {
                    "orderno": item.orderno,
                    "orderdate": item.orderdate,
                    "productsid": item.productsid,
                    "productsname": item.productsname,
                    "totalprice": item.orderprice,
                    "productscount" : 1
                }
                
        # 반복문이 끝난 후, 마지막으로 작업 중이던 그룹을 최종 리스트에 추가
        order_list.append(order_data)
    except :
        order_list = None

    return render_template('orderlist.html', login=login, items=order_list)

# 주문 내역 상세 보기
@app.route("/orderdetail")
def orderDetail() :
    login = loginCheckUrl("로그인이 필요합니다", "login")
    if login :
        return login
    
    login = session.get("userid")
    
    orderno = request.args.get('orderno')
    order_detail = shopDTO.orderDetail(login, orderno)
    
    return render_template('orderdetail.html', login=login, items=order_detail)


# 로그인 체크
def loginCheck(messagem) :
    if session.get("userid") is None :
        error_message = messagem
        return render_template('alert.html', message=error_message, redirect=url_for('home'))
    
    return None

# 로그인 체크 후 이동    
def loginCheckUrl(messagem, url) :
    if session.get("userid") is None :
        error_message = messagem
        redirect_url = url_for(url)
        return render_template('alert.html', message=error_message, redirect=redirect_url)
    
    return None
    

if __name__ == "__main__" :
    app.run(host="0.0.0.0", port=8000)