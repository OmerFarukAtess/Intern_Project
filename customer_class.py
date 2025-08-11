from dataBaseConnection import DataBaseConnectionClass

class Customer:

    def __init__(self, customer_no, customer_daily_limit,card_no=None,
                 card_daily_limit=None):
        self.customer_no = customer_no
        self.customer_daily_limit = float(customer_daily_limit)

        # Kart bilgileri - bu sınıf bir kartın bilgilerini de tutabilir
        self.card_no = card_no if card_no is not None else None
        self.card_daily_limit = float(card_daily_limit) if card_daily_limit is not None else None

    def update_customer_limit(self, new_limit):
        if new_limit < 0:
            return False
        else:
            self.customer_daily_limit = new_limit
            database_object = DataBaseConnectionClass(self.customer_no)
            database_object.update_customer_info(self.customer_daily_limit)
            return True

    def update_card_limit(self, new_limit):
        if new_limit < 0:
            return False
        else:
            self.card_daily_limit = new_limit
            database_object = DataBaseConnectionClass(self.customer_no)
            database_object.update_customer_card_info(self.card_daily_limit, self.card_no)
            return True

    def withdraw_money(self, withdrawn_money,total_spend,card_spend):
        if withdrawn_money < 0:
            return {"error":"çekilecek miktar 0 dan az olamaz!!!!"}
        else:
            if (self.card_daily_limit-card_spend) < withdrawn_money:
                return {"error":"kartın kalan günlük para çekme limiti yetersiz"}
            else:
                if (self.customer_daily_limit-total_spend) < withdrawn_money:
                    return {"error": "müsterinin kalan günlük para çekme limiti yetersiz"}
                else:
                    database_object = DataBaseConnectionClass(self.customer_no)
                    database_object.update_customer_card_info(self.card_daily_limit,self.card_no,(int(card_spend) + int(withdrawn_money)))
                    database_object.last_withdrawn_time_update()
                    # Başarılı durumda güncel limitleri döndür
                    return {
                        "Cards": { # Burada tek bir kart döndürüyoruz çünkü işlem tek bir kart üzerinde yapılıyor
                            "CardNo": self.card_no,
                            "CardDailySpend": (card_spend + withdrawn_money)
                        }
                    }
