from flask import Flask, request, jsonify
from customer_class import Customer
from dataBaseConnection import DataBaseConnectionClass

app = Flask(__name__)

@app.route('/Onayla', methods=['POST'])
def customer_info():
    data = request.json
    customer_no = data.get("CustomerNo", 0)
    database_object = DataBaseConnectionClass(customer_no)
    database_object.reset_limit()
    customer_and_card_info = database_object.get_customer_and_card_info()

    if isinstance(customer_and_card_info, dict) and "error" in customer_and_card_info:
        return jsonify({"error": customer_and_card_info["error"]}), 404
    elif isinstance(customer_and_card_info, dict):  # Başarılı dönüş durumu (customer_class'tan gelen güncel bilgiler)
        return jsonify(customer_and_card_info)
    else:  # Beklenmedik bir durum veya None dönmesi halinde
        return jsonify({"error": "Bilinmeyen bir hata oluştu veya işlem başarısız oldu."}), 500


@app.route('/MüşteriLimit', methods=['POST'])
def customer_limit():
    data = request.json
    new_limit = data.get('NewLimit', 0)
    customer_no = data.get('CustomerNo', 0)
    database_object = DataBaseConnectionClass(customer_no)
    database_object.reset_limit()
    customer_and_card_info = database_object.get_customer_and_card_info()

    if not customer_and_card_info:
        return jsonify({"error": "Müşteri bulunamadı veya bilgiler alınamadı"}), 404

    # Customer objesini oluştur ve bir değişkene ata
    customer_object = Customer(
        customer_and_card_info["Customer"]["CustomerNo"],
        customer_and_card_info["Customer"]["CustomerDailyLimit"]
    )

    if customer_object.update_customer_limit(new_limit):
        # Güncellenmiş müşteri limitini tekrar çekerek döndür (veya Customer objesinden al)
        current_customer_info = database_object.get_customer_and_card_info()
        return jsonify({
            "durum": "Müşteri günlük limiti başarıyla güncellendi.",
            "CustomerDailyLimit": current_customer_info["Customer"]["CustomerDailyLimit"],
        })
    else:
        return jsonify({"error": "Müşteri limiti güncelleme başarısız oldu. Geçersiz limit değeri!!!."}), 400

@app.route('/KartLimit', methods=['POST'])
def card_limit():
    data = request.json
    new_limit = data.get('NewLimit', 0)
    customer_no = data.get('CustomerNo', 0)
    card_no = data.get('CardNo', 0)
    database_object = DataBaseConnectionClass(customer_no)
    database_object.reset_limit()
    customer_and_card_info = database_object.get_customer_and_card_info()

    if not customer_and_card_info:
        return jsonify({"error": "Müşteri bulunamadı veya bilgiler alınamadı"}), 404

    selected_card_data = None
    for card in customer_and_card_info['Cards']:
        if card['CardNo'] == card_no:
            selected_card_data = card
            break

    if not selected_card_data:
        return jsonify({"error": "Belirtilen kart numarasına sahip kart bulunamadı"}), 404

    card_object = Customer(
        customer_no,
        customer_and_card_info["Customer"]["CustomerDailyLimit"],
        selected_card_data["CardNo"],
        selected_card_data["CardDailyLimit"]
    )

    if card_object.update_card_limit(new_limit):
        # Güncellenmiş kart limitini tekrar çekerek döndür (veya Customer objesinden al)
        current_customer_info = database_object.get_customer_and_card_info()
        current_customer_card_info = next((kart for kart in current_customer_info['Cards'] if kart['CardNo'] == card_no), None)
        return jsonify({
            "durum": "Kart günlük limiti başarıyla güncellendi.",
            "CardDailyLimit": current_customer_card_info["CardDailyLimit"]
        })
    else:
        return jsonify({"error": "Kart limiti güncelleme başarısız oldu. Geçersiz limit değeri."}), 400


@app.route('/ParaCekme', methods=['POST'])
def withdraw_money():
    data = request.json
    customer_no = data.get('CustomerNo', 0)
    card_no = data.get('CardNo', 0)
    withdrawn_amount = data.get('WithdrawnAmount', 0)
    database_object = DataBaseConnectionClass(customer_no)
    database_object.reset_limit()
    customer_and_card_info = database_object.get_customer_and_card_info()

    if not customer_and_card_info:
        return jsonify({"error": "Müşteri bulunamadı veya bilgiler alınamadı"}), 404
    total_spend = 0
    selected_card_data = None
    for card in customer_and_card_info['Cards']:
        total_spend += float(card["CardDailySpend"])
        if card['CardNo'] == card_no:
            selected_card_data = card

    if not selected_card_data:
        return jsonify({"error": "Belirtilen kart numarasına sahip kart bulunamadı"}), 404

    withdrawn_object = Customer(
        customer_no,
        customer_and_card_info["Customer"]["CustomerDailyLimit"],
        selected_card_data["CardNo"],
        selected_card_data["CardDailyLimit"],
    )

    durum = withdrawn_object.withdraw_money(withdrawn_amount,total_spend,selected_card_data["CardDailySpend"])

    # durum'un bir dictionary olup olmadığını kontrol et
    if isinstance(durum, dict) and "error" in durum:
        return jsonify({"error": durum["error"]}), 500
    elif isinstance(durum, dict): # Başarılı dönüş durumu (customer_class'tan gelen güncel bilgiler)
        return jsonify(durum)
    else: # Beklenmedik bir durum veya None dönmesi halinde
        return jsonify({"error": "Bilinmeyen bir hata oluştu veya işlem başarısız oldu."}), 500


if __name__ == '__main__':
    app.run(debug=True,port = 5000)