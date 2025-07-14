import DBManager as db
import random

dbms = db.DBManager()

class itemVO:
    def __init__(self) :
        self.name  = None
        self.id    = None
        self.desc  = None
        self.price = None
        self.clss  = None
        
class cartVO:
    def __init__(self) :
        self.userid     = None
        self.productsid = None
        self.quantity   = None
        self.name       = None
        self.price      = None

class orderVO:
    def __init__(self) :
        self.orderno      = None
        self.userid       = None
        self.orderdate    = None
        self.productsid   = None
        self.productsname = None
        self.quantity     = None
        self.orderprice   = None
        
class itemDTO:
    def __init__(self) :
        self.host = "192.168.0.69"
        self.user = "root"
        self.pw   = "ezen"
        self.db   = "shopdb"

    
    # 로그인
    def loginok(self, userid, userpw):
        dbms = db.DBManager()
        flag = dbms.DBOpen(self.host,self.user,self.pw,self.db)
        if flag == False :
            print("DB 연결 실패.....")
        else :
            sql  = "select userid from user where userid = %s and userpw = md5( %s );"
            params = (userid, userpw)
            userid = dbms.OpenQuery(sql, params)
            if userid == 0:
                userid = False
            else:
                userid = True
        dbms.DBClose()
        
        return userid
    
    
    def view(self, name):
        vo = itemVO()
        flag = dbms.DBOpen(self.host,self.user,self.pw,self.db)
        if flag == False :
            print("DB 연결 실패.....")
        else :
            sql  = "select * from products where productsid = %s;"
            params = (name)
            dbms.OpenQuery(sql, params)
            vo.id  = dbms.GetValue(0, "productsid")
            vo.name  = dbms.GetValue(0, "productsname")
            vo.desc = dbms.GetValue(0, "description")
            vo.price = dbms.GetValue(0, "price")
            vo.clss = dbms.GetValue(0, "class")
            dbms.CloseQuery()
        dbms.DBClose()

        return vo


    def recommend(self, items):
       flag = dbms.DBOpen(self.host,self.user,self.pw,self.db)
       itemlist = []
       for item in items:
           rno = random.randint(0, 4)
           if flag == False :
               print("DB 연결 실패.....")
           else :
               vo = itemVO()
               proid = f"{item}{rno:02d}"
               print(proid)
               sql  = "select * from products where productsid = %s;"
               params = (proid)
               dbms.OpenQuery(sql, params)
               vo.id  = dbms.GetValue(0, "productsid")
               vo.name  = dbms.GetValue(0, "productsname")
               vo.desc = dbms.GetValue(0, "description")
               vo.price = dbms.GetValue(0, "price")
               vo.clss = dbms.GetValue(0, "class")
               itemlist.append(vo)
               dbms.CloseQuery()

       dbms.DBClose()
       
       return itemlist

    
    def list(self, vo):
        flag = dbms.DBOpen(self.host,self.user,self.pw,self.db)
        if flag == False :
            print("DB 연결 실패.....")
        else :
            items = []
            for data in vo:
                sql  = "select * from products where class = %s;"
                params = (data)
                total = dbms.OpenQuery(sql, params)
                item = []
                for i in range(0, total) :
                    vo = itemVO()
                    vo.id  = dbms.GetValue(i, "productsid")
                    vo.name  = dbms.GetValue(i, "productsname")
                    vo.desc = dbms.GetValue(i, "description")
                    vo.price = dbms.GetValue(i, "price")
                    vo.clss = dbms.GetValue(i, "class")
                    item.append(vo)
                items.append(item)
                dbms.CloseQuery()
        dbms.DBClose()
        return items
    
    
    def subclass(self, clss):
        flag = dbms.DBOpen(self.host,self.user,self.pw,self.db)
        if flag == False :
            print("DB 연결 실패.....")
        else :
            sql  = "select * from products where class = %s;" 
            params = (clss)
            total = dbms.OpenQuery(sql, params)
            items = []
            for i in range(0, total) :
                vo = itemVO()
                vo.id  = dbms.GetValue(i, "productsid")
                vo.name  = dbms.GetValue(i, "productsname")
                vo.desc = dbms.GetValue(i, "description")
                vo.price = dbms.GetValue(i, "price")
                vo.clss = dbms.GetValue(i, "class")
                items.append(vo)
            dbms.CloseQuery()
        dbms.DBClose()
        return items
    
    
    # 장바구니에 품목이 있는지 체크
    # 리턴값 : True, False
    def basketCheck(self, userid, code) :
        flag = dbms.DBOpen(self.host,self.user,self.pw,self.db)
        if flag == False :
            print("DB 연결 실패.....")
        else :
            sql  = "select * from cart where userid = %s and productsid = %s;"
            params = (userid, code)
            product = dbms.OpenQuery(sql, params)
            if product == 0:
                product = False
            else:
                product = True
        dbms.DBClose()
        return product
    
    
    # 장바구니에 추가
    def basketInsert(self, userid, code, num) :
        flag = dbms.DBOpen(self.host,self.user,self.pw,self.db)
        if flag == False :
            print("DB 연결 실패.....")
        else :
            sql = "insert into cart (userid, productsid, quantity) values (%s, %s, %s);"
            params = (userid, code, num)
            dbms.RunSQL(sql, params)
            print("장바구니에 제품을 추가했습니다")
            
        dbms.DBClose()


    # 장바구니 보기
    def basketView(self, userid) :
        flag = dbms.DBOpen(self.host,self.user,self.pw,self.db)
        
        if flag == False :
            print("DB 연결 실패.....")
        else :
            sql  = "select c.userid, c.productsid, c.quantity, p.productsname, p.price from cart c left join products p on c.productsid = p.productsid where userid = %s;"
            params = (userid)
            total = dbms.OpenQuery(sql, params)
            items = []
            for i in range(0, total) :
                cvo = cartVO()
                cvo.userid      = dbms.GetValue(i, "userid")
                cvo.productsid  = dbms.GetValue(i, "productsid")
                cvo.quantity    = dbms.GetValue(i, "quantity")
                cvo.name        = dbms.GetValue(i, "productsname")
                cvo.price       = dbms.GetValue(i, "price")
                print(cvo.productsid, cvo.quantity)
                items.append(cvo)
            dbms.CloseQuery()
            
        dbms.DBClose()
        return items
    
    
    # 장바구니에서 제품 삭제
    def basketDelete(self, userid, code_list) :
        flag = dbms.DBOpen(self.host,self.user,self.pw,self.db)
        
        if flag == False :
            print("DB 연결 실패.....")
        else :
            for i in range(0, len(code_list)) :
                code = code_list[i]
                sql  = "delete from cart where userid = %s and productsid = %s;"
                param = (userid, code)
                dbms.RunSQL(sql, param)
            print("장바구니에서 제품을 삭제했습니다.")
            
        dbms.DBClose()
        
    
    # 장바구니에서 제품 주문
    def basketOrder(self, userid, order_list) :
        flag = dbms.DBOpen(self.host,self.user,self.pw,self.db)
        
        if flag == False :
            print("DB 연결 실패.....")
        else :
            sql = "insert into orderinfo (userid) values (%s);"
            param = (userid)
            dbms.RunSQL(sql, param)
            
            sql = "select LAST_INSERT_ID() as idx from orderinfo"
            dbms.OpenQueryS(sql)
            idx = dbms.GetValue(0, "idx")
            idx = str(idx)
            
            for i in range(0, len(order_list)) :
                productsid = order_list[i]["product_id"]
                quantity = order_list[i]["quantity"]    
                price = order_list[i]["price"]
                
                sql = "insert into orderitem (productsid, quantity, orderprice, orderno) values (%s, %s, %s, %s); "
                param = (productsid, quantity, price, idx)
                dbms.RunSQL(sql, param)
            print("장바구니에서 제품을 주문했습니다.")
            
        dbms.DBClose()
        
    
    # 주문내역 리스트 확인
    def orderList(self, userid) :
        flag = dbms.DBOpen(self.host,self.user,self.pw,self.db)
        
        if flag == False :
            print("DB 연결 실패.....")
        else :
            sql  = "select o.orderno, o.userid, o.orderdate, i.productsid, i.quantity, i.orderprice, p.productsname "
            sql += "from orderinfo o left join orderitem i on o.orderno = i.orderno "
            sql += "left join products p on i.productsid = p.productsid where userid = %s;"
            params = (userid)
            total = dbms.OpenQuery(sql, params)
            items = []
            
            for i in range(0, total) :
                vo = orderVO()
                        
                vo.orderno      = dbms.GetValue(i, "orderno")
                vo.userid       = dbms.GetValue(i, "userid")
                vo.orderdate    = dbms.GetValue(i, "orderdate")
                vo.productsid   = dbms.GetValue(i, "productsid")
                vo.productsname = dbms.GetValue(i, "productsname")
                vo.orderprice   = dbms.GetValue(i, "orderprice")
                
                items.append(vo)
            
        dbms.DBClose()
        return items
    
    
    # 주문내역 상세 확인
    def orderDetail(self, userid, orderno) :
        flag = dbms.DBOpen(self.host,self.user,self.pw,self.db)
        
        if flag == False :
            print("DB 연결 실패.....")
        else :
            sql  = "select o.orderno, i.productsid, i.quantity, i.orderprice, p.productsname "
            sql += "from orderinfo o left join orderitem i on o.orderno = i.orderno "
            sql += "left join products p on i.productsid = p.productsid where userid = %s and o.orderno = %s;"
            params = (userid, orderno)
            total = dbms.OpenQuery(sql, params)
            
            items = []
            
            for i in range(0, total) :
                vo = orderVO()
                        
                vo.orderno      = dbms.GetValue(i, "orderno")
                vo.productsid   = dbms.GetValue(i, "productsid")
                vo.quantity     = dbms.GetValue(i, "quantity")
                vo.productsname = dbms.GetValue(i, "productsname")
                vo.orderprice   = dbms.GetValue(i, "orderprice")
                
                items.append(vo)
            
        dbms.DBClose()
        return items
    
    
    # 제품 검색
    def search(self, name):
        flag = dbms.DBOpen(self.host,self.user,self.pw,self.db)
        if flag == False :
            print("DB 연결 실패.....")
        else :
            sql  = "select * from products where productsname like %s"
            params = ('%'+name.strip()+'%')
            total = dbms.OpenQuery(sql, params)
            items = []
            for i in range(0, total) :
                vo = itemVO()
                vo.id  = dbms.GetValue(i, "productsid")
                vo.name  = dbms.GetValue(i, "productsname")
                vo.price = dbms.GetValue(i, "price")
                vo.clss = dbms.GetValue(i, "class")
                items.append(vo)
            dbms.CloseQuery()
        dbms.DBClose()
        
        return items
    
    
    
    
    
    
    
    
    
    
    
    