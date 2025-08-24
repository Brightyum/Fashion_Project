import pymysql
import os


class UserManager():
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
    
    def get_user_by_email(self, email):
        conn = self.get_db_connection()
        try:
            with conn.cursor() as cursor:
                select_sql = "SELECT * FROM users WHERE email = %s"
                cursor.execute(select_sql, (email))
                user = cursor.fetchone()
                return user
        except Exception as e:
            print(f"에러 발생: {e}")
            return None
        finally:
            conn.close()
    
    def get_user_id_by_email(self, email):
        conn = self.get_db_connection()
        try:
            with conn.cursor() as cursor:
                select_sql = "SELECT userId FROM users WHERE email = %s"
                cursor.execute(select_sql, (email))
                user = cursor.fetchone()

                if user:
                    return user["userId"]
                else:
                    return None
        except Exception as e:
            print(f"에러 발생: {e}")
            return None
        finally:
            conn.close()

    def create_user(self, user_data):
        print(f"user_data: {user_data}")
        conn = self.get_db_connection()
        try: 
            with conn.cursor() as cursor:
                insert_sql = """
                    INSERT INTO users (email, name, phoneNumber, gender, password)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (
                    user_data.get("email"),
                    user_data.get("name"),
                    user_data.get("phone"),
                    user_data.get("gender"),
                    user_data.get("password")
                ))
            conn.commit()
            print("신규 사용자 생성 완료")

            return self.get_user_by_email(user_data.get("email"))
        except Exception as e:
            print(f"에러 발생: 신규 사용자 생성 불가 - {e}")
            return None
        finally:
            conn.close()
        
            
