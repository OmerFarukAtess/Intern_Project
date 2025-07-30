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
if 'selected_card_to_update' not in st.session_state:
    st.session_state.selected_card_to_update = None
if 'musteri_no_input' not in st.session_state:
    st.session_state.musteri_no_input = 0

def musteri_bilgileri_goster(data):
    st.subheader("Müşteri Bilgileri")
    st.write(f"Müşteri No: {data['müşteri']['MüşteriNo']}")
    st.write(f"Müşteri Günlük Limit: {data['müşteri']['MüşteriGünlükLimit']}")
    st.write(f"Müşteri Kalan Günlük Limit: {data['müşteri']['MüşteriKalanGünlükLimit']}")

    st.subheader("Kart Bilgileri")
    for kart in data['kartlar']:
        st.write(f"Kart No: {kart['KartNo']}")
        if float(kart['KartGünlükLimit']) > float(data['müşteri']['MüşteriGünlükLimit']):
            st.write(f"Kart Günlük Limit: {data['müşteri']['MüşteriGünlükLimit']}")
            st.write(f"Kart Kalan Günlük Limit: {float(data['müşteri']['MüşteriGünlükLimit'])-(float(kart['KartGünlükLimit'])-float(kart['KartKalanGünlükLimit']))}")
        else:
            st.write(f"Kart Günlük Limit: {kart['KartGünlükLimit']}")
            st.write(f"Kart Kalan Günlük Limit: {kart['KartKalanGünlükLimit']}")
        st.write("---")

st.title("VakıfBank Müşteri Kart Limit Uygulaması")

# Müşteri numarası girişi her zaman görünür olacak
musteri_no = st.number_input("Müşteri Numarası Girin:", value=st.session_state.musteri_no_input, format="%d", key="musteri_no_input_widget")

# Müşteri numarasını onayla butonu
if st.button("Müşteri Numarasını Onayla"):
    if musteri_no == 0:
        st.warning("Lütfen geçerli bir müşteri numarası girin.")
        st.session_state.show_main_options = False
        st.session_state.current_customer_data = None
    else:
        # Backend'den müşteri bilgilerini çekmeyi deneme (sadece varlığını kontrol etmek için)
        url = "http://localhost:5000/Onayla"
        veri = {"müsteriNo": musteri_no}
        response = requests.post(url, json=veri)

        if response.status_code == 200:
            st.session_state.current_customer_data = response.json()
            st.session_state.show_main_options = True
            st.session_state.show_update_options = False
            st.session_state.show_update_customer_limit_input = False
            st.session_state.show_update_card_limit_input = False
            st.session_state.selected_card_to_update = None
            st.session_state.musteri_no_input = musteri_no
            st.success(f"Müşteri {musteri_no} bulundu. Lütfen bir seçenek belirleyin.")
        elif response.status_code == 404:
            st.error("Müşteri bulunamadı. Lütfen doğru bir müşteri numarası girin.")
            st.session_state.current_customer_data = None
            st.session_state.show_main_options = False
            st.session_state.show_update_options = False
        else:
            st.error(f"API çağrısı başarısız oldu: {response.status_code} - {response.text}")
            st.session_state.current_customer_data = None
            st.session_state.show_main_options = False
            st.session_state.show_update_options = False


# Müşteri numarası onaylandıysa ana seçenekleri göster
if st.session_state.show_main_options:
    st.markdown("---")
    st.subheader("Lütfen bir işlem seçin:")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Müşteri Bilgilerini Getir"):
            musteri_bilgileri_goster(st.session_state.current_customer_data)
            st.session_state.show_update_options = False # Diğer seçenekleri gizle
            st.session_state.show_update_customer_limit_input = False
            st.session_state.show_update_card_limit_input = False

    with col2:
        if st.button("Limit Güncelleme"):
            st.session_state.show_update_options = True # Limit güncelleme seçeneklerini göster
            st.session_state.show_main_options = True # Ana seçenekleri göstermeye devam et
            st.session_state.show_update_customer_limit_input = False # Alt formları gizle
            st.session_state.show_update_card_limit_input = False

    # Limit Güncelleme seçenekleri
    if st.session_state.show_update_options:
        st.markdown("---")
        st.subheader("Limit Güncelleme Seçenekleri:")
        col_limit1, col_limit2 = st.columns(2)

        with col_limit1:
            if st.button("Müşteri Limit Güncelle"):
                st.session_state.show_update_customer_limit_input = True
                st.session_state.show_update_card_limit_input = False # Diğer formu gizle
                st.session_state.selected_card_to_update = None

        with col_limit2:
            if st.button("Kart Limit Güncelle"):
                st.session_state.show_update_card_limit_input = True
                st.session_state.show_update_customer_limit_input = False # Diğer formu gizle

        # Müşteri Limit Güncelleme Formu
        if st.session_state.show_update_customer_limit_input:
            st.markdown("---")
            st.subheader("Müşteri Limitini Güncelle")
            # Mevcut limiti varsayılan değer olarak göster
            initial_customer_limit = float(st.session_state.current_customer_data['müşteri']['MüşteriGünlükLimit']) if st.session_state.current_customer_data else 0.0
            yeni_musteri_limit = st.number_input("Yeni Müşteri Günlük Limit:", value=initial_customer_limit, format="%f", key="yeni_musteri_limit_input")

            if st.button("Müşteri Limitini Kaydet"):
                url = "http://localhost:5000/MüşteriLimit"
                veri = {"müşteriNo": st.session_state.musteri_no_input, "yeniLimit": yeni_musteri_limit}
                response = requests.post(url, json=veri)

                if response.status_code == 200:
                    st.success(response.json()['durum'])
                    # Güncel bilgileri tekrar çekerek arayüzü yenile
                    st.session_state.current_customer_data['müşteri']['MüşteriGünlükLimit'] = response.json()['MüşteriGünlükLimit']
                    st.session_state.current_customer_data['müşteri']['MüşteriKalanGünlükLimit'] = response.json()['MüşteriKalanGünlükLimit']
                    musteri_bilgileri_goster(st.session_state.current_customer_data)
                    st.session_state.show_update_customer_limit_input = False # Formu gizle
                else:
                    st.error(response.json()["error"])

        # Kart Limit Güncelleme Formu
        if st.session_state.show_update_card_limit_input and st.session_state.current_customer_data:
            st.markdown("---")
            st.subheader("Kart Limitini Güncelle")

            kart_numaralari = [kart['KartNo'] for kart in st.session_state.current_customer_data['kartlar']]

            if not kart_numaralari:
                st.warning("Bu müşteriye ait kart bulunamadı.")
            else:
                # Kullanıcının hangi kartı güncelleyeceğini seçmesi için selectbox
                selected_card_no = st.selectbox("Güncellenecek Kartı Seçin:", kart_numaralari, key='card_selector')

                # Seçilen kartın mevcut limitini bul
                current_card_limit = 0.0
                for kart in st.session_state.current_customer_data['kartlar']:
                    if kart['KartNo'] == selected_card_no:
                        current_card_limit = float(kart['KartGünlükLimit'])
                        break

                yeni_kart_limit = st.number_input(f"Yeni {selected_card_no} Kart Günlük Limit:", value=current_card_limit, format="%f", key='new_card_limit_input')

                if st.button("Kart Limitini Kaydet"):
                    url = "http://localhost:5000/KartLimit"
                    veri = {"müşteriNo": st.session_state.musteri_no_input, "kartNo": selected_card_no, "yeniLimit": yeni_kart_limit}
                    response = requests.post(url, json=veri)

                    if response.status_code == 200:
                        st.success(f"{selected_card_no} kart limiti başarıyla güncellendi!")
                        # Güncel bilgileri tekrar çekerek arayüzü yenile
                        # (Daha verimli: sadece ilgili kartı güncelle)
                        for i, kart in enumerate(st.session_state.current_customer_data['kartlar']):
                            if kart['KartNo'] == selected_card_no:
                                st.session_state.current_customer_data['kartlar'][i]['KartGünlükLimit'] = response.json()['KartGünlükLimit']
                                st.session_state.current_customer_data['kartlar'][i]['KartKalanGünlükLimit'] = response.json()['KartKalanGünlükLimit']
                                break
                        musteri_bilgileri_goster(st.session_state.current_customer_data)
                        st.session_state.show_update_card_limit_input = False # Formu gizle
                    else:
                        st.error(response.json()["error"])
