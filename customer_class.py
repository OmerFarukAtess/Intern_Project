from dataBaseConnection import update_customer_info, update_customer_card_info


class Customer:

    def __init__(self, customer_no, customer_daily_limit, customer_remaining_daily_limit,
                 card_no=None, card_daily_limit=None, card_remaining_daily_limit=None):
        self.customer_no = customer_no
        self.customer_daily_limit = float(customer_daily_limit)
        self.customer_remaining_daily_limit = float(customer_remaining_daily_limit)

        # Kart bilgileri - bu sınıf bir kartın bilgilerini de tutabilir
        self.card_no = card_no
        self.card_daily_limit = float(card_daily_limit) if card_daily_limit is not None else None
        self.card_remaining_daily_limit = float(card_remaining_daily_limit) if card_remaining_daily_limit is not None else None

    def update_customer_limit(self, new_limit):
        if new_limit < 0:
            return False
        else:
            self.customer_remaining_daily_limit = (new_limit - self.customer_daily_limit) + self.customer_remaining_daily_limit
            self.customer_daily_limit = new_limit
            update_customer_info(self.customer_daily_limit, self.customer_remaining_daily_limit, self.customer_no)
            return True

    def update_card_limit(self, new_limit):
        if new_limit < 0:
            return False
        else:
            self.card_remaining_daily_limit = (new_limit - self.card_daily_limit) + self.card_remaining_daily_limit
            self.card_daily_limit = new_limit
            update_customer_card_info(self.card_daily_limit, self.card_remaining_daily_limit, self.card_no, self.customer_no)
            return True

    def withdraw_money(self, withdrawn_money):
        if withdrawn_money < 0:
            return {"error":"çekilecek miktar 0 dan az olamaz!!!!"}
        else:
            if self.customer_daily_limit < withdrawn_money:
                return {"error":"müşterinin kalan günlük para çekme limiti yetersiz"}
            else:
                if self.card_remaining_daily_limit < withdrawn_money:
                    return {"error": "kartın kalan günlük para çekme limiti yetersiz"}
                else:
                    if self.card_remaining_daily_limit < 0 or self.customer_remaining_daily_limit < 0:
                        return{"error": "limitiniz yetersiz"}
                    else:
                        self.card_remaining_daily_limit = self.card_remaining_daily_limit - withdrawn_money
                        self.customer_remaining_daily_limit = self.customer_remaining_daily_limit - withdrawn_money
                        update_customer_card_info(self.card_daily_limit, self.card_remaining_daily_limit, self.card_no, self.customer_no)
                        update_customer_info(self.customer_daily_limit, self.customer_remaining_daily_limit, self.customer_no)
                        # Başarılı durumda güncel limitleri döndür
                        return {
                            "Customer": {
                                "CustomerNo": self.customer_no,
                                "CustomerDailyLimit": self.customer_daily_limit,
                                "CustomerRemainingDailyLimit": self.customer_remaining_daily_limit
                            },
                            "Cards": { # Burada tek bir kart döndürüyoruz çünkü işlem tek bir kart üzerinde yapılıyor
                                "CardNo": self.card_no,
                                "CardDailyLimit": self.card_daily_limit,
                                "CardRemainingDailyLimit": self.card_remaining_daily_limit
                            }
                        }