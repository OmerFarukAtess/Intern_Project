from flask import Flask, request, jsonify
from customer_class import Customer
from dataBaseConnection import DataBaseConnectionClass

app = Flask(__name__)

@app.route('/GetCustomerInfo', methods=['GET'])
def get_customer_info():
    data = request.json
    customer_no = data.get("CustomerNo", 0)
    database_object = DataBaseConnectionClass(customer_no)
    database_object.reset_limit()
    customer_info = database_object.get_customer_info()

    if isinstance(customer_info, dict) and "error" in customer_info:
        return jsonify(customer_info), 404
    elif isinstance(customer_info, dict):  # Başarılı dönüş durumu (customer_class'tan gelen güncel bilgiler)
        return jsonify(customer_info) , 200
    else:  # Beklenmedik bir durum veya None dönmesi halinde
        return jsonify({"error": "Bilinmeyen bir hata oluştu veya işlem başarısız oldu."}), 500

@app.route('/GetCardInfo', methods=['GET'])
def get_card_info():
    data = request.json
    customer_no = data.get("CustomerNo", 0)
    database_object = DataBaseConnectionClass(customer_no)
    database_object.reset_limit()
    card_info = database_object.get_card_info()

    if isinstance(card_info, dict) and "error" in card_info:
        return jsonify(card_info), 404
    elif isinstance(card_info, dict):  # Başarılı dönüş durumu (customer_class'tan gelen güncel bilgiler)
        return jsonify(card_info) ,200
    else:  # Beklenmedik bir durum veya None dönmesi halinde
        return jsonify({"error": "Bilinmeyen bir hata oluştu veya işlem başarısız oldu."}), 500


@app.route('/SetCustomerLimit', methods=['POST'])
def set_customer_limit():
    data = request.json
    new_limit = data.get("NewLimit", 0)
    customer_no = data.get("CustomerNo", 0)
    database_object = DataBaseConnectionClass(customer_no)
    database_object.reset_limit()
    customer_info = database_object.get_customer_info()

    if not customer_info or "error" in customer_info:
        return jsonify({"error": "Müşteri bulunamadı"}), 404

    # Customer objesini oluştur ve bir değişkene ata
    customer_object = Customer(
        customer_info["Customer"]["CustomerNo"],
        customer_info["Customer"]["CustomerDailyLimit"]
    )

    return customer_object.update_customer_limit(new_limit)

@app.route('/SetCardLimit', methods=['POST'])
def set_card_limit():
    data = request.json
    new_limit = data.get('NewLimit', 0)
    customer_no = data.get('CustomerNo', 0)
    card_no = data.get('CardNo', 0)
    database_object = DataBaseConnectionClass(customer_no)
    database_object.reset_limit()
    card_info = database_object.get_card_info()

    if not card_info or "error" in card_info:
        return jsonify({"error": "Müşteri bulunamadı"}), 404

    selected_card_data = None
    for card in card_info['Cards']:
        if card['CardNo'] == card_no:
            selected_card_data = card
            break

    if not selected_card_data:
        return jsonify({"error": "Belirtilen müsteri numarasına sahip kart bulunamadı"}), 404

    card_object = Customer(
        customer_no,
        card_no = selected_card_data["CardNo"],
        card_daily_limit = selected_card_data["CardDailyLimit"]
    )

    return card_object.update_card_limit(new_limit)



@app.route('/WithdrawnMoney', methods=['POST'])
def withdraw_money():
    data = request.json
    customer_no = data.get('CustomerNo', 0)
    card_no = data.get('CardNo', 0)
    withdrawn_amount = data.get('WithdrawnAmount', 0)
    database_object = DataBaseConnectionClass(customer_no)
    database_object.reset_limit()
    customer_and_card_info = database_object.get_customer_and_card_info()

    if not customer_and_card_info or "error" in customer_and_card_info:
        return jsonify({"error": "Müşteri bulunamadı"}), 404

    total_spend = 0
    selected_card_data = None
    for card in customer_and_card_info['Cards']:
        total_spend += float(card["CardDailySpend"])
        if card['CardNo'] == card_no:
            selected_card_data = card

    if not selected_card_data:
        return jsonify({"error": "Belirtilen müsteri numarasına sahip kart bulunamadı"}), 404

    withdrawn_object = Customer(
        customer_no,
        customer_daily_limit = customer_and_card_info["Customer"]['CustomerDailyLimit'],
        card_no = selected_card_data["CardNo"],
        card_daily_limit = selected_card_data["CardDailyLimit"],
    )

    durum = withdrawn_object.withdraw_money(withdrawn_amount,total_spend,selected_card_data["CardDailySpend"])

    # durum'un bir dictionary olup olmadığını kontrol et
    if isinstance(durum, dict) and "error" in durum:
        return jsonify(durum), 400
    elif isinstance(durum, dict): # Başarılı dönüş durumu (customer_class'tan gelen güncel bilgiler)
        return jsonify(durum) , 200
    else: # Beklenmedik bir durum veya None dönmesi halinde
        return jsonify({"error": "Bilinmeyen bir hata oluştu veya işlem başarısız oldu."}), 500


if __name__ == '__main__':
    app.run(debug=True,port = 5000)