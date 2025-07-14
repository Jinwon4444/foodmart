import DBManager as db
import csv

dbms = db.DBManager()
flag = dbms.DBOpen("192.168.0.69", "root", "ezen", "shopdb")


# DB추가(products)
file = open("cooking.csv", "r")

datas = csv.reader(file)

if flag == False :
    print("DB연결에 실패했습니다.")
else :
    for line in datas :
        
        if line[0] == "" :
            continue
        
        product = line[1]
        product_class = line[2]
        product_name = line[4]
        product_description = f"식자재마트에서 판매하는 {product_name} 입니다."
        product_price = line[6].replace(",", "").replace("원", "")
        
        # DB-API의 파라미터 바인딩 사용
        # SQL 쿼리문의 모든 형식 지정자를 %s로 통일합니다
        # sql % params 형태로 직접 쿼리를 만들지 않습니다. 대신 cursor.execute() 메소드에 sql과 params를 각각 인자로 전달합니다.
        sql = "insert into products (productsid, productsname, description, class, price) values (%s, %s, %s, %s, %s); "
        params = (product, product_name, product_description, product_class, product_price)
        dbms.RunSQL(sql, params)    
        
    print("상품을 추가했습니다")
    
    sql = "select * from products"
    dbms.OpenQuery(sql)
    productsid = dbms.GetValue(0, "productsid")
    print(productsid)
    

'''
# DB추가(user)    
if flag == False :
    print("DB연결에 실패했습니다.")
else :
    for i in range(1, 101) :
        userid = f"user{ i }"
        userpw = f"user{ i }"
        sql = "insert into user (userid, userpw) values (%s, md5(%s)); "
        params = (userid, userpw)
        dbms.RunSQL(sql, params)
    
    print("유저를 추가했습니다")
    
dbms.DBClose()
'''