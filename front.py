import streamlit as st
import requests

# Session state başlatma (uygulama durumunu korumak için)
if 'current_customer_data' not in st.session_state:
    st.session_state.current_customer_data = None
if 'show_main_options' not in st.session_state:
    st.session_state.show_main_options = False
if 'show_update_options' not in st.session_state:
    st.session_state.show_update_options = False
if 'show_update_customer_limit_input' not in st.session_state:
    st.session_state.show_update_customer_limit_input = False
if 'show_update_card_limit_input' not in st.session_state:
    st.session_state.show_update_card_limit_input = False
if 'show_withdraw_input' not in st.session_state:
    st.session_state.show_withdraw_input = False
if 'selected_card_to_update' not in st.session_state:
    st.session_state.selected_card_to_update = None
if 'musteri_no_input' not in st.session_state:
    st.session_state.musteri_no_input = 0

def musteri_bilgileri_goster(data):
    st.subheader("Müşteri Bilgileri")
    st.write(f"Müşteri No: {data['Customer']['CustomerNo']}")
    st.write(f"Müşteri Günlük Limit: {data['Customer']['CustomerDailyLimit']}")
    total_spend = 0
    for temp_card in data['Cards']:
        total_spend += float(temp_card["CardDailySpend"])
    if (float(data["Customer"]["CustomerDailyLimit"]) - total_spend) < 0:
        st.write("Müşteri Kalan Günlük Limit: 0.00")
    else :
        st.write(f"Müşteri Kalan Günlük Limit: {(float(data['Customer']['CustomerDailyLimit']) - float(total_spend))}")

    st.subheader("Kart Bilgileri")
    for temp_card in data['Cards']:
        st.write(f"Kart No: {temp_card['CardNo']}")
        if float(temp_card['CardDailyLimit']) > float(data['Customer']['CustomerDailyLimit']):
            st.write(f"Kart Günlük Limit: {data['Customer']['CustomerDailyLimit']}")
            st.write(f"Kart Kalan Günlük Limit: {float(data['Customer']['CustomerDailyLimit']) - float(temp_card['CardDailySpend'])}")
        else:
            st.write(f"Kart Günlük Limit: {temp_card['CardDailyLimit']}")
            if float(temp_card['CardDailyLimit'])-float(temp_card['CardDailySpend']) >  float(data['Customer']['CustomerDailyLimit']) - total_spend:
                st.write(f"Kart Kalan Günlük Limit: {(float(data['Customer']['CustomerDailyLimit']) - float(total_spend))}")
            else:
                st.write(f"Kart Kalan Günlük Limit: {float(temp_card['CardDailyLimit']) - float(temp_card['CardDailySpend'])}")
        st.write("---")


st.title("VakıfBank Müşteri Kart Limit Uygulaması")

# Müşteri numarası girişi her zaman görünür olacak
customer_no = st.number_input("Müşteri Numarası Girin:", value=st.session_state.musteri_no_input, format="%d", key="musteri_no_input_widget")

# Müşteri numarasını onayla butonu
if st.button("Müşteri Numarasını Onayla"):
    if customer_no == 0:
        st.warning("Lütfen geçerli bir müşteri numarası girin.")
        st.session_state.show_main_options = False
        st.session_state.current_customer_data = None
    else:
        # Backend'den müşteri bilgilerini çekmeyi deneme (sadece varlığını kontrol etmek için)
        url = "http://localhost:5000/Onayla"
        data = {"CustomerNo": customer_no}
        response = requests.post(url, json=data)

        if response.status_code == 200:
            st.session_state.current_customer_data = response.json() # Veriyi şimdilik sakla
            st.session_state.show_main_options = True # Ana seçenekleri göster
            st.session_state.show_update_options = False # Limit güncelleme seçeneklerini gizle
            st.session_state.show_update_customer_limit_input = False
            st.session_state.show_update_card_limit_input = False
            st.session_state.show_withdraw_input = False # Para çekme formunu gizle
            st.session_state.selected_card_to_update = None
            st.session_state.musteri_no_input = customer_no # Giriş yapılan müşteri no'yu session state'e kaydet
            st.success(f"Müşteri {customer_no} bulundu. Lütfen bir seçenek belirleyin.")
        elif response.status_code == 404:
            st.error(f"{response.json()["error"]}")
            st.session_state.current_customer_data = None
            st.session_state.show_main_options = False
            st.session_state.show_update_options = False
            st.session_state.show_withdraw_input = False
        else:
            st.error(f"API çağrısı başarısız oldu: {response.status_code} - {response.text}")
            st.session_state.current_customer_data = None
            st.session_state.show_main_options = False
            st.session_state.show_update_options = False
            st.session_state.show_withdraw_input = False


# Müşteri numarası onaylandıysa ana seçenekleri göster
if st.session_state.show_main_options:
    st.markdown("---")
    st.subheader("Lütfen bir işlem seçin:")

    # Eski col1, col2, col3 yerine yeni düzen
    col1, col2, col3, col4 = st.columns(4) # 4 sütunlu yeni layout

    with col1:
        if st.button("Müşteri Bilgilerini Getir"):
            musteri_bilgileri_goster(st.session_state.current_customer_data)
            st.session_state.show_update_options = False # Diğer seçenekleri gizle
            st.session_state.show_update_customer_limit_input = False
            st.session_state.show_update_card_limit_input = False
            st.session_state.show_withdraw_input = False # Para çekme formunu gizle

    with col2:
        # Yeni Müşteri Limit Güncelle butonu
        if st.button("Müşteri Limit Güncelle"):
            st.session_state.show_update_customer_limit_input = True
            st.session_state.show_update_card_limit_input = False # Diğer formu gizle
            st.session_state.selected_card_to_update = None
            st.session_state.show_withdraw_input = False # Para çekme formunu gizle
            st.session_state.show_update_options = False # Eski menüyü gizle

    with col3:
        # Yeni Kart Limit Güncelle butonu
        if st.button("Kart Limit Güncelle"):
            st.session_state.show_update_card_limit_input = True
            st.session_state.show_update_customer_limit_input = False # Diğer formu gizle
            st.session_state.show_withdraw_input = False # Para çekme formunu gizle
            st.session_state.show_update_options = False # Eski menüyü gizle

    with col4:
        if st.button("Para Çekme"):
            st.session_state.show_withdraw_input = True
            st.session_state.show_update_options = False # Diğer seçenekleri gizle
            st.session_state.show_update_customer_limit_input = False
            st.session_state.show_update_card_limit_input = False


    # Müşteri Limit Güncelleme Formu
    if st.session_state.show_update_customer_limit_input:
        st.markdown("---")
        st.subheader("Müşteri Limitini Güncelle")
        # Mevcut limiti varsayılan değer olarak göster
        initial_customer_limit = float(st.session_state.current_customer_data['Customer']['CustomerDailyLimit']) if st.session_state.current_customer_data else 0.0
        yeni_musteri_limit = st.number_input("Yeni Müşteri Günlük Limit:", value=initial_customer_limit, format="%f", key="yeni_musteri_limit_input")

        if st.button("Müşteri Limitini Kaydet"):
            url = "http://localhost:5000/MüşteriLimit"
            data = {"CustomerNo": st.session_state.musteri_no_input, "NewLimit": yeni_musteri_limit}
            response = requests.post(url, json=data)

            if response.status_code == 200:
                st.success(response.json()['durum'])
                # Güncel bilgileri tekrar çekerek arayüzü yenile
                st.session_state.current_customer_data['Customer']['CustomerDailyLimit'] = response.json()['CustomerDailyLimit']
                musteri_bilgileri_goster(st.session_state.current_customer_data)
                st.session_state.show_update_customer_limit_input = False # Formu gizle
            else:
                st.error(response.json()["error"])

    # Kart Limit Güncelleme Formu
    if st.session_state.show_update_card_limit_input and st.session_state.current_customer_data:
        st.markdown("---")
        st.subheader("Kart Limitini Güncelle")

        kart_numaralari = [kart['CardNo'] for kart in st.session_state.current_customer_data['Cards']]

        if not kart_numaralari:
            st.warning("Bu müşteriye ait kart bulunamadı.")
        else:
            # Kullanıcının hangi kartı güncelleyeceğini seçmesi için selectbox
            selected_card_no = st.selectbox("Güncellenecek Kartı Seçin:", kart_numaralari, key='card_selector')

            # Seçilen kartın mevcut limitini bul
            current_card_limit = 0.0
            for card in st.session_state.current_customer_data['Cards']:
                if card['CardNo'] == selected_card_no:
                    current_card_limit = float(card['CardDailyLimit'])
                    break

            new_card_limit = st.number_input(f"Yeni {selected_card_no} Kart Günlük Limit:", value=current_card_limit, format="%f", key='new_card_limit_input')

            if st.button("Kart Limitini Kaydet"):
                url = "http://localhost:5000/KartLimit"
                data = {"CustomerNo": st.session_state.musteri_no_input, "CardNo": selected_card_no, "NewLimit": new_card_limit}
                response = requests.post(url, json=data)

                if response.status_code == 200:
                    if float(st.session_state.current_customer_data['Customer']['CustomerDailyLimit']) < new_card_limit:
                        st.warning(f"Kart Limitiniz Maximum {st.session_state.current_customer_data['Customer']['CustomerDailyLimit']} olabilir ve bu şekilde ayarlanmıştır")
                    else:
                        st.success(f"{selected_card_no} kart limiti başarıyla güncellendi!")
                    # Güncel bilgileri tekrar çekerek arayüzü yenile
                    # (Daha verimli: sadece ilgili kartı güncelle)
                    for i, card in enumerate(st.session_state.current_customer_data['Cards']):
                        if card['CardNo'] == selected_card_no:
                            st.session_state.current_customer_data['Cards'][i]['CardDailyLimit'] = response.json()['CardDailyLimit']
                            break
                    musteri_bilgileri_goster(st.session_state.current_customer_data)
                    st.session_state.show_update_card_limit_input = False # Formu gizle
                else:
                    st.error(response.json()["error"])

    # Para Çekme Formu
    if st.session_state.show_withdraw_input and st.session_state.current_customer_data:
        st.markdown("---")
        st.subheader("Para Çekme İşlemi")

        kart_numaralari = [kart['CardNo'] for kart in st.session_state.current_customer_data['Cards']]

        if not kart_numaralari:
            st.warning("Bu müşteriye ait kart bulunamadı.")
        else:
            selected_card_to_withdraw = st.selectbox("Para Çekilecek Kartı Seçin:", kart_numaralari, key='withdraw_card_selector')
            withdrawn_amount = st.number_input("Çekilecek Miktar:", format="%f", key='withdraw_amount_input')

            if st.button("Para Çek"):
                url = "http://localhost:5000/ParaCekme"
                data = {
                    "CustomerNo": st.session_state.musteri_no_input,
                    "CardNo": selected_card_to_withdraw,
                    "WithdrawnAmount": withdrawn_amount
                }
                response = requests.post(url, json=data)

                if response.status_code == 200:
                    st.success(f"{withdrawn_amount} TL {selected_card_to_withdraw} kartından başarıyla çekildi!")
                    # Backend'den gelen yeni limit bilgileriyle session state'i güncelle
                    for i, card in enumerate(st.session_state.current_customer_data['Cards']):
                        if card['CardNo'] == selected_card_to_withdraw:
                            st.session_state.current_customer_data['Cards'][i]["CardDailySpend"] = response.json()['Cards']["CardDailySpend"]
                            break
                    musteri_bilgileri_goster(st.session_state.current_customer_data) # Güncel bilgileri göster
                    st.session_state.show_withdraw_input = False # Formu gizle
                else:
                    try:
                        # Eğer yanıt JSON ise ayrıştır
                        error_message = response.json().get("error", "Bilinmeyen bir hata oluştu.")
                    except requests.exceptions.JSONDecodeError:
                        # Yanıt JSON değilse ham metni kullan
                        error_message = f"Backend'den geçersiz yanıt: {response.text}"
                    st.error(f"Para çekme işlemi başarısız oldu: {error_message}")