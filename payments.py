import streamlit as st
from supabase import create_client, Client
import pandas as pd
import time
import os   

def load_css():
    css_file = os.path.join(os.path.dirname(__file__), 'style.css')
    if os.path.exists(css_file):
        with open(css_file, encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    else:
        st.error("style.cssファイルが見つかりません。")

load_css()

# Supabaseの設定を環境変数から取得
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_data():
    with st.spinner('データを読み込んでいます...'):
        response = supabase.table("payments").select("*").execute()
    return response.data

def add_payment(method, currency, paytype, customer, total_advance_amount, deposit_amount, fee_amount, profit_margin=None):
    supabase.table("payments").insert({
        "method": method,
        "currency": currency,
        "paytype": paytype,
        "customer": customer,
        "total_advance_amount": total_advance_amount,
        "deposit_amount": deposit_amount,
        "fee_amount": fee_amount,
        "profit_margin": profit_margin
    }).execute()

def delete_payment(payment_id):
    try:
        # 削除処理
        response = supabase.table("payments").delete().eq("id", payment_id).execute()
        
        # レスポンスの詳細を出力
        st.write("削除レスポンス:", response)
        
        # 削除成功の判定を修正
        # データがからの配列で、例外が発生していない場合は成功とみなす
        return response.data is not None
    except Exception as e:
        st.error(f"削除中にエラーが発生しました: {str(e)}")
        return False

def check_deletion(payment_id):
    try:
        # 最新のデータを取得して確認
        data = fetch_data()
        
        # 削除対象のIDがデータに存在しないことを確認
        return not any(row['id'] == payment_id for row in data)
    except Exception as e:
        st.error(f"確認中にエラーが発生しました: {str(e)}")
        return False
# Custom title with added styling
st.markdown('<div class="title">入金データ管理アプリ</div>', unsafe_allow_html=True)

# Sidebar with menu
menu = st.sidebar.radio("メニューを選択してください", ["入金", "データ覧"])


if menu == "入金":
    st.header("新しい入金データを追加")
    col1, col2, col3 = st.columns([1,1,1])

    with col1:
        st.subheader("基本情報")
        
        
        method = st.selectbox("入金タイプ", ["前受入金", "売掛"])
        currency = st.selectbox("通貨", ["JPY", "USD", "EUR","GBP"])
        paytype = st.selectbox("一部or全部", ["全部", "一部"])
        customer = st.text_input("顧客名")

        if (method == "売掛" or method == "前受入金") and currency == "USD":
            today_rate_usd = st.number_input("今日のレート (USD)", placeholder="入力",key="rate_usd")
        elif (method == "売掛" or method == "前受入金") and currency == "EUR":
            today_rate_eur = st.number_input("今日のレート (EUR)", placeholder="入力",key="rate_eur")    
        elif (method == "売掛" or method == "前受入金") and currency == "GBP":
            today_rate_gbp = st.number_input("今日のレート (GBP)", placeholder="入力",key="rate_gbp")
        


    with col2:
        
        st.subheader("計画/Invoice")
        if method == "前受入金":
            num_plans = st.number_input("計画番号の数", min_value=1, value=1)
            total_advance_amount: float = 0.0
            plan_details = []

            for i in range(int(num_plans)):
                plan_number = st.text_input(f"計画番号 {i+1}")
                if currency == "JPY":
                    advance_amount = st.number_input(f"前受額{i+1} JPY", placeholder="入力",key=f"advance_jpy_{i}")
                elif currency == "USD":
                    usd_amount = st.number_input(f"前受額{i+1} USD", placeholder="入力",key=f"advance_usd_{i}")
                    advance_amount = usd_amount * 103.00
                    st.write(f"JPY換算: {advance_amount:,.0f}")
                elif currency == "EUR":
                    eur_amount = st.number_input(f"前受額{i+1} EUR", placeholder="入力",key=f"advance_eur_{i}")
                    advance_amount = eur_amount * 120.00
                    st.write(f"JPY換算: {advance_amount:,.0f}")
                elif currency == "GBP":
                    gbp_amount = st.number_input(f"前受額{i+1} GBP", placeholder="入力",key=f"advance_gbp_{i}")
                    advance_amount = gbp_amount * today_rate_gbp
                    st.write(f"JPY換算: {advance_amount:,.0f}")

                plan_details.append({
                    "plan_number": plan_number,
                    "advance_amount": advance_amount
                })
                total_advance_amount += advance_amount

        elif method == "売掛":
            num_invoice = st.number_input("Invoiceの数", min_value=1, value=1)
            total_urikake_amount: float = 0.0
            plan_details = []

            for i in range(int(num_invoice)):
                invoice_number = st.text_input(f"Invoice番号 {i+1}")
                urikake_date = st.date_input(f"売掛日 {i+1}")

                if currency == "JPY":
                    urikake_amount = st.number_input(f"売掛額{i+1} JPY", placeholder="入力")
                elif currency == "USD":
                    usd_amount = st.number_input(f"売掛額{i+1} USD", placeholder="入力")
                    urikake_amount = usd_amount * 103.00
                    st.write(f"JPY換算: {urikake_amount:,.0f}")
                elif currency == "EUR":
                    eur_amount = st.number_input(f"売掛額{i+1} EUR", placeholder="入力")
                    urikake_amount = eur_amount * 120.00
                    st.write(f"JPY換算: {urikake_amount:,.0f}")
                elif currency == "GBP":
                    gbp_amount = st.number_input(f"売掛額{i+1} GBP", placeholder="入力")
                    urikake_amount = gbp_amount * today_rate_gbp
                    st.write(f"JPY換算: {urikake_amount:,.0f}")

                plan_details.append({
                    "invoice_number": invoice_number,
                    "urikake_amount": urikake_amount,
                    "urikake_date": urikake_date
                })
                total_urikake_amount += urikake_amount
        


    with col3:
        
        st.subheader("金額詳細")
        if method == "前受入金":
            st.write(f"合計前受額 JPY: {total_advance_amount:,.0f}")
            
            
            if currency == "JPY":
                deposit_amount = st.number_input("入金額 JPY", min_value=0.0, max_value=float(total_advance_amount))
                fee_amount = total_advance_amount - deposit_amount
                st.write(f"手数料 JPY: {fee_amount:,.0f}")
            elif currency == "USD":
                deposit_amount = st.number_input(f"入金額 {currency}", min_value=0.0)
                jpy_deposit_amount = deposit_amount * today_rate_usd
                st.write(f"入金額 JPY: {jpy_deposit_amount:,.0f}")
                fee_amount = ((total_advance_amount/103.00) - (deposit_amount)) * today_rate_usd
                st.write(f"手数料 JPY: {fee_amount:,.0f}")
                profit_margin = jpy_deposit_amount + fee_amount - total_advance_amount
                st.write(f"差益 JPY: {profit_margin:,.0f}")
            elif currency == "EUR":
                deposit_amount = st.number_input(f"入金額 {currency}", min_value=0.0)
                jpy_deposit_amount = deposit_amount * today_rate_eur
                st.write(f"入金額 JPY: {jpy_deposit_amount:,.0f}")
                fee_amount = ((total_advance_amount/120.00) - (deposit_amount)) * today_rate_eur
                st.write(f"手数料 JPY: {fee_amount:,.0f}")
                profit_margin = jpy_deposit_amount + fee_amount - total_advance_amount
                st.write(f"差益 JPY: {profit_margin:,.0f}")
            elif currency == "GBP":
                deposit_amount = st.number_input(f"入金額 {currency}", min_value=0.0)
                jpy_deposit_amount = deposit_amount * today_rate_gbp
                st.write(f"入金額 JPY: {jpy_deposit_amount:,.0f}")
                fee_amount = (total_advance_amount) - (jpy_deposit_amount) 
                st.write(f"手数料 JPY: {fee_amount:,.0f}")


        elif method == "売掛":
            st.write(f"合計売掛額 JPY: {total_urikake_amount:,.0f}")
            
            if currency == "USD":
                
                
                deposit_amount = st.number_input(f"入金額 {currency}", min_value=0.0)
                jpy_deposit_amount = deposit_amount * today_rate_usd
                st.write(f"入金額 JPY: {jpy_deposit_amount:,.0f}")
                
                # 差益の計算：(当日レート - 103) * 売掛額(USD)
                profit_margin = (today_rate_usd - 103) * (total_urikake_amount/103.00)
                st.write(f"差益 JPY: {profit_margin:,.0f}")
                
                # 手数料の計算：売掛額 + 差益 - 入金額
                fee_amount = total_urikake_amount + profit_margin - jpy_deposit_amount
                st.text_input("手数料 JPY", value=f"{fee_amount:,.0f}", key="fee_amount_urikake_jpy", placeholder="自動計算されます")
            
            elif currency == "EUR":
                
                
                deposit_amount = st.number_input(f"入金額 {currency}", min_value=0.0)
                jpy_deposit_amount = deposit_amount * today_rate_eur
                st.write(f"入金額 JPY: {jpy_deposit_amount:,.0f}")
                
                 # 差益の計算：(当日レート - 103) * 売掛額(USD)
                profit_margin = (today_rate_eur - 120) * (total_urikake_amount/120.00)
                st.write(f"差益 JPY: {profit_margin:,.0f}")
                
                # 手数料の計算：売掛額 + 差益 - 入金額
                fee_amount = total_urikake_amount + profit_margin - jpy_deposit_amount
                st.text_input("手数料 JPY", value=f"{fee_amount:,.0f}", key="fee_amount_urikake_jpy", placeholder="自動計算されます")
            
            elif currency == "GBP":
                
                deposit_amount = st.number_input(f"入金額 {currency}", min_value=0.0)
                jpy_deposit_amount = deposit_amount * today_rate_gbp
                st.write(f"入金額 JPY: {jpy_deposit_amount:,.0f}")
                
                # 差益の計算
                profit_margin = jpy_deposit_amount - total_urikake_amount
                st.write(f"差益 JPY: {profit_margin:,.0f}")
                
                # 手数料の計算
                fee_amount =  jpy_deposit_amount - total_urikake_amount
                st.text_input("手数料 JPY", value=f"{fee_amount:,.0f}", key="fee_amount_urikake_gbp", placeholder="自動計算されます")
            
            elif currency == "JPY":
                deposit_amount = st.number_input("入金額 JPY", min_value=0.0, max_value=float(total_urikake_amount))
                fee_amount = total_urikake_amount - deposit_amount
                
                st.write(f"手数料 JPY: {fee_amount:,.0f}")
               
       

    # データベースに追加
    if st.button("データベースへ追加"):
        if method == "前受入金":
            add_payment(method, currency, paytype, customer, total_advance_amount, deposit_amount, fee_amount)
        elif method == "売掛":
            for detail in plan_details:
                supabase.table("payments").insert({
                    "method": method,
                    "currency": currency,
                    "paytype": paytype,
                    "customer": customer,
                    "invoice_number": detail.get("invoice_number", ""),
                    "urikake_date": detail.get("urikake_date", "").strftime("%Y-%m-%d") if detail.get("urikake_date") else "",
                    "total_urikake_amount": detail.get("urikake_amount", 0),
                    "deposit_amount": deposit_amount,
                    "fee_amount": fee_amount
                }).execute()
        
        st.success("データを追加しました！")
        st.rerun()

if menu == "データ覧":
    st.header("登録データ一覧")

    data = fetch_data()  # 最新データを取得
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df)

        st.subheader("データを削除")
        selected_id = st.selectbox("削除するデータのID", df["id"])

        if st.button("削除"):
            # 削除処理の結果を確認
            deletion_result = delete_payment(selected_id)
            
            if deletion_result:
                st.success("削除リクエストを送信しました。")
                time.sleep(2)  # 2秒待つ
                st.rerun()
            else:
                st.error("削除に失敗しました。")
    else:
        st.write("データがありません")


