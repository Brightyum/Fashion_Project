import pymysql
import os


class TokenManager():
    def __init__(self):
        self.db_host = os.getenv("DB_HOST")
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.db_name = os.getenv("DB_NAME")
        self.db_port = int(os.getenv("DB_PORT"))

    def get_db_connection(self):
        db_connection = pymysql.connect(
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_password,
            db=self.db_name,
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor
        )
        return db_connection
    
    def save_refresh_token(self, user_id, refresh_token):
        conn = self.get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 기존 토큰 삭제
                delete_sql = "DELETE FROM tokens where userId=%s"
                cursor.execute(delete_sql, (user_id,))

                insert_sql = "INSERT INTO tokens (userId, refreshToken) VALUES (%s, %s)"
                cursor.execute(insert_sql, (user_id, refresh_token))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"에러 발생: 토큰 저장 실패 - {e}")
            return False
        finally:
            conn.close()

    def verify_refresh_token(self, user_id, refresh_token):
        conn = self.get_db_connection()
        try:
            with conn.cursor() as cursor:
                select_sql = "SELECT * FROM tokens WHERE userId = %s AND refreshToken = %s"
                cursor.execute(select_sql (user_id, refresh_token))
                # 토큰 결과가 없으면 None 있으면 값을 가져옴
                token_record = cursor.fetchone()
                if token_record is not None:
                    return True
                else:
                    return False
        except Exception as e:
            print(f"에러 발생: 토큰 가져오기 실패 - {e}")
            return False
        finally:
            conn.close()