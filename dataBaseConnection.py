import pyodbc


class DataBaseConnectionClass:
    def __init__(self,customer_no):
        self.customer_no = customer_no
        self.conn_str = r'DRIVER={SQL Server};SERVER=DESKTOP-7PPE35F\MSSQLSERVER1;DATABASE=VakıfBank;Trusted_Connection=yes;'


    def get_customer_and_card_info(self):
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()

            # MüşteriLimit'ten bilgileri al
            cursor.execute("exec CustomerInfo @CustomerNo = ?", self.customer_no)
            customer = cursor.fetchone()

            # Eğer müşteri bulunamazsa None döndür
            if not customer:
                return {"error": "Müşteri bulunamadı"}

            # KartLimit'ten bilgileri al
            cursor.execute("SELECT CardNo, CardDailyLimit, CardRemainingDailyLimit FROM CardsLimit WHERE CustomerNo=?",
                           self.customer_no)
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
                "UPDATE CustomersLimit SET CustomerDailyLimit = ?, CustomerRemainingDailyLimit = ? WHERE CustomerNo = ?",
                new_customer_daily_limit, new_customer_remaing_daily_limit, self.customer_no)
            conn.commit()

            return True

        except Exception as e:
            print(f"Müşteri limiti güncellenirken hata: {e}")
            return {"error": f"Müşteri limiti güncellenirken bir hata oluştu: {e}"}
        finally:
            if 'conn' in locals():
                conn.close()


    def update_customer_card_info(self,new_card_daily_limit, new_card_kalan_daily_limit, card_no):
        conn_str = r'DRIVER={SQL Server};SERVER=DESKTOP-7PPE35F\MSSQLSERVER1;DATABASE=VakıfBank;Trusted_Connection=yes;'
        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE CardsLimit SET CardDailyLimit = ?, CardRemainingDailyLimit = ? WHERE CustomerNo = ? AND CardNo = ?",
                new_card_daily_limit, new_card_kalan_daily_limit, self.customer_no, card_no)
            conn.commit()
            return True
        except Exception as e:
            return {"error": f"Kart limiti güncellenirken bir hata oluştu: {e}"}
        finally:
            if 'conn' in locals():
                conn.close()
