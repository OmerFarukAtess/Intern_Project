import pyodbc
from datetime import datetime ,date



class DataBaseConnectionClass:
    def __init__(self,customer_no):
        self.customer_no = customer_no
        self.conn_str = r'DRIVER={SQL Server};SERVER=DESKTOP-7PPE35F\MSSQLSERVER1;DATABASE=VakıfBank;Trusted_Connection=yes;'


    def get_customer_and_card_info(self):
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()

            # MüşteriLimit'ten bilgileri al
            cursor.execute(f"exec CustomerInfo @CustomerNo = {self.customer_no}")
            customer = cursor.fetchone()

            # Eğer müşteri bulunamazsa None döndür
            if not customer:
                return {"error": "Müşteri bulunamadı"}

            # KartLimit'ten bilgileri al
            cursor.execute(f"exec CardInfo @CustomerNo = {self.customer_no}")
            cards = cursor.fetchall()

            # Sonuçları dictionary olarak hazırla
            result = {
                "Customer": {
                    "CustomerNo": customer.CustomerNo,
                    "CustomerDailyLimit": customer.CustomerDailyLimit,
                    "CustomerRemainingDailyLimit": customer.CustomerRemainingDailyLimit
                },
                "Cards": [
                    {
                        "CardNo": card.CardNo,
                        "CardDailyLimit": card.CardDailyLimit,
                        "CardRemainingDailyLimit": card.CardRemainingDailyLimit
                    } for card in cards
                ]
            }

            return result

        except Exception as e:
            return f"Error: {e}"
        finally:
            if 'conn' in locals():
                conn.close()


    def update_customer_info(self,new_customer_daily_limit, new_customer_remaing_daily_limit):
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            cursor.execute(
                f"""exec UpdateCustomerInfo @CustomerNo = {self.customer_no} , @NewCustomerDailyLimit = {new_customer_daily_limit} ,
                @NewCustomerRemainingDailyLimit = {new_customer_remaing_daily_limit}""")
            conn.commit()

            return True

        except Exception as e:
            print(f"Müşteri limiti güncellenirken hata: {e}")
            return {"error": f"Müşteri limiti güncellenirken bir hata oluştu: {e}"}
        finally:
            if 'conn' in locals():
                conn.close()


    def update_customer_card_info(self,new_card_daily_limit, new_card_kalan_daily_limit, card_no):
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()

            cursor.execute(
                f"""exec UpdoteCustomerCardsInfo @CustomerNo = {self.customer_no} , @CardNo = {card_no},
                @NewCustomerCardDailyLimit = {new_card_daily_limit} ,@NewCustomerRemainingCardDailyLimit = {new_card_kalan_daily_limit} """)
            conn.commit()
            return True
        except Exception as e:
            return {"error": f"Kart limiti güncellenirken bir hata oluştu: {e}"}
        finally:
            if 'conn' in locals():
                conn.close()


    def last_withdrawn_time_update(self):
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()

            cursor.execute(
                f"exec UpdateLastTransactionTime @CustomerNo = {self.customer_no}")
            conn.commit()
            return True
        except Exception as e:
            return {"error": f"Bir hata oluştu: {e}"}
        finally:
            if 'conn' in locals():
                conn.close()

    def reset_limit(self):
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()

            cursor.execute(
                f"select LastTransaction from LastTransactions where CustomerNo = {self.customer_no}"
            )
            result = cursor.fetchone()
            last_transaction = result[0]
            today = date.today()

            if isinstance(last_transaction, str):
                last_transaction = datetime.strptime(last_transaction, "%Y-%m-%d").date()
            elif isinstance(last_transaction, datetime):
                last_transaction = last_transaction.date()

            if last_transaction < today:
                cursor.execute(
                    f"""exec ResetCustomerLimit @CustomerNo = {self.customer_no}
                        exec ResetCustomerCardLimit @CustomerNo = {self.customer_no}"""
                    )
                conn.commit()
                return True

        except Exception as e:
            return {"error": f"Bir hata oluştu: {e}"}
        finally:
            if 'conn' in locals():
                conn.close()