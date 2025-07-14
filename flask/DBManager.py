# DBManager 클래스 구현부
import pymysql
import pandas as pd

class DBManager:
    # 생성자
    def __init__(self) :
        self.con = None
        
    # 데이터베이스에 연결한다.
    # 리턴값 : True - 연결성공, False - 실패
    def DBOpen(self,host,user,pw,db) :
        try:
            self.con = pymysql.connect(host=host,
                          user=user,
                          password=pw,
                          db=db,
                          charset="utf8")
            return True
        except :
            return False
    
    # 데이터베이스 연결을 종료한다.
    def DBClose(self) :
        self.con.close()
        
        
    # INSERT, DELETE, UPDATE 처리
    def RunSQL(self, sql, param) :
        cursor = self.con.cursor()        
        cursor.execute(sql, param)
        self.con.commit()
        cursor.close()
        
    # SELECT 처리
    def OpenQuery(self, sql, param) :
        self.cursor = self.con.cursor()
        total = self.cursor.execute(sql, param)
        if total > 0 :
            # 모든 데이터를 일단 몽땅 얻는다.
            self.data = self.cursor.fetchall()
        return total
    
    # SELECT 처리(파라미터없음)
    def OpenQueryS(self, sql) :
        self.cursor = self.con.cursor()
        total = self.cursor.execute(sql)
        if total > 0 :
            # 모든 데이터를 일단 몽땅 얻는다.
            self.data = self.cursor.fetchall()
        return total
        
    # SELECT 닫기
    def CloseQuery(self) :
        self.cursor.close()
        
    # 행 값 얻기
    def GetRow(self,row) :
        #self.data = ( (a,b,c), (a,b,c), (a,b,c) )
        return self.data[row]
        
    # 값 얻기
    def GetValue(self,row,column) :
        data = self.data[row]
        for idx, item in enumerate(self.cursor.description) :
            if column == item[0] :
                # 원하는 컬럼 이름 찾음
                return data[idx]
        return None
        
    def GetAll(self) :
        columns = []
        for item in self.cursor.description :
            columns.append(item[0])
        print(columns)
        df = pd.DataFrame(self.data)
        # colums를 데이터프레임의 컬럼이름으로 지정
        df.columns = columns;
        return df
