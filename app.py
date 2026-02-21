import streamlit as st
import requests
import pandas as pd
from io import BytesIO

# UI အပြင်အဆင်
st.set_page_config(page_title="Loyverse to Excel Sync", layout="wide")
st.title("📊 Loyverse Daily Sales to Excel")

# ဘေးဘောင် (Sidebar) တွင် API Key ထည့်ရန်
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Loyverse API Key", type="password")
    date_from = st.date_input("From Date")
    date_to = st.date_input("To Date")

def fetch_loyverse_data(api_key, date_from, date_to):
    url = f"https://api.loyverse.com/v1.0/receipts?created_at_min={date_from}T00:00:00Z&created_at_max={date_to}T23:59:59Z"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('receipts', [])
    else:
        st.error(f"Error: {response.status_code}")
        return None

if st.button("အရောင်းစာရင်းများ ရယူရန်"):
    if not api_key:
        st.warning("ကျေးဇူးပြု၍ API Key ထည့်ပေးပါ။")
    else:
        with st.spinner('Data ဆွဲယူနေပါသည်...'):
            data = fetch_loyverse_data(api_key, date_from, date_to)
            
            if data:
                # Data ကို ဇယားပုံစံပြောင်းခြင်း
                df = pd.json_normalize(data)
                
                # လိုချင်တဲ့ Column တွေကိုပဲ ရွေးထုတ်ခြင်း (ဥပမာ- နေ့စွဲ၊ စုစုပေါင်း)
                cols_to_show = ['receipt_number', 'created_at', 'total_money', 'total_tax']
                df_filtered = df[cols_to_show] if all(c in df.columns for c in cols_to_show) else df

                st.success(f"အရောင်းပြေစာ {len(df)} စောင် တွေ့ရှိပါတယ်။")
                st.dataframe(df_filtered, use_container_width=True)

                # Excel ဖိုင်အဖြစ် ပြောင်းလဲခြင်း
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sales')
                
                # Download ခလုတ်
                st.download_button(
                    label="📥 Download Excel File",
                    data=output.getvalue(),
                    file_name=f"Loyverse_Sales_{date_from}.xlsx",
                    mime="application/vnd.ms-excel"
                )
            else:
                st.info("ပြထားသော ရက်စွဲအတွင်း အရောင်းစာရင်း မရှိပါ။")
                