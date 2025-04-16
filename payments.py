import streamlit as st
from supabase import create_client, Client
import pandas as pd
import time
import os   
import math


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

def add_payment(method, currency, paytype, customer, total_advance_amount, deposit_amount, fee_amount, profit_margin=None, plan_number=None, invoice_number=None, urikake_date=None, total_urikake_amount=None):
    supabase.table("payments").insert({
        "method": method,
        "currency": currency,
        "paytype": paytype,
        "customer": customer,
        "total_advance_amount": total_advance_amount,
        "total_urikake_amount": total_urikake_amount,
        "deposit_amount": deposit_amount,
        "fee_amount": fee_amount,
        "profit_margin": profit_margin,
        "plan_number": plan_number,
        "invoice_number": invoice_number,
        "urikake_date": urikake_date.strftime("%Y-%m-%d") if urikake_date else None
    }).execute()

def delete_payment(payment_id):
    try:
        # 削除処理
        response = supabase.table("payments").delete().eq("id", payment_id).execute()
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
st.markdown('<div class="title">入金伝票作成システム</div>', unsafe_allow_html=True)

# Sidebar with menu
menu = st.sidebar.radio("メニューを選択してください", ["入金", "データ覧"])


if menu == "入金":
    st.header("入金伝票")
    col1, col2, col3 = st.columns([3,3,3])

    with col1:
        st.subheader("基本情報")
        
        
        method = st.selectbox("入金タイプ", ["前受入金", "売掛"])
        currency = st.selectbox("通貨", ["JPY", "USD", "EUR"])
        paytype = st.selectbox("一部or全部", ["全部", "一部"])
        customer = st.text_input("顧客名")

        if (method == "売掛" or method == "前受入金") and currency == "USD":
            today_rate_usd = st.number_input("今日のレート (USD)", placeholder="入力",key="rate_usd")
        elif (method == "売掛" or method == "前受入金") and currency == "EUR":
            today_rate_eur = st.number_input("今日のレート (EUR)", placeholder="入力",key="rate_eur")    



    with col2:
        
        st.subheader("計画/Invoice")
        if method == "前受入金":
            num_plans = st.number_input("計画番号の数", min_value=1, value=1)
            total_advance_amount: float = 0.0
            plan_details = []

            for i in range(int(num_plans)):
                plan_number = st.text_input(f"計画番号 {i+1}")
                if currency == "JPY":
                    advance_amount_input = st.number_input(f"前受額{i+1} JPY", placeholder="入力",key=f"advance_jpy_{i}")
                    
                    advance_amount = float(advance_amount_input)
                    st.write(f"前受額{i+1} JPY: {advance_amount:,.0f}")
                    
    
                elif currency == "USD":
                    usd_amount_input = st.number_input(f"前受額{i+1} USD", placeholder="入力",key=f"advance_usd_{i}")
                    usd_amount = float(usd_amount_input)
                    advance_amount = usd_amount * 103.00
                    st.write(f"前受額{i+1} USD: {usd_amount:,.2f}")
                    st.write(f"JPY換算: {advance_amount:,.0f}")
                elif currency == "EUR":
                    eur_amount_input = st.number_input(f"前受額{i+1} EUR", placeholder="入力",key=f"advance_eur_{i}")
                    eur_amount = float(eur_amount_input)
                    advance_amount = eur_amount_input * 120.00
                    st.write(f"前受額{i+1} EUR: {eur_amount:,.2f}")
                    st.write(f"JPY換算: {advance_amount:,.0f}")

                plan_details.append({
                    "plan_number": plan_number,
                    "advance_amount": advance_amount
                })
                total_advance_amount += advance_amount

        elif method == "売掛":
            if currency == "JPY":
                num_plans = st.number_input("計画番号の数", min_value=1, value=1)
                total_urikake_amount: float = 0.0
                plan_details = []

                for i in range(int(num_plans)):
                    plan_number = st.text_input(f"計画番号 {i+1}")
                    urikake_date = st.date_input(f"売掛日 {i+1}")
                    urikake_amount_input = st.number_input(f"売掛額{i+1} JPY", placeholder="入力")
                    urikake_amount = float(urikake_amount_input)
                    st.write(f"売掛額{i+1} JPY: {urikake_amount:,.0f}")

                    plan_details.append({
                        "plan_number": plan_number,  
                        "urikake_amount": urikake_amount,
                        "urikake_date": urikake_date
                    })
                    total_urikake_amount += urikake_amount
            else:
                num_invoice = st.number_input("Invoiceの数", min_value=1, value=1)
                total_urikake_amount: float = 0.0
                plan_details = []

                for i in range(int(num_invoice)):
                    invoice_number = st.text_input(f"Invoice番号 {i+1}")
                    urikake_date = st.date_input(f"売掛日 {i+1}")

                    if currency == "USD":
                        usd_amount_input = st.number_input(f"売掛額{i+1} USD", placeholder="入力")
                        usd_amount = float(usd_amount_input)
                        urikake_amount = usd_amount * 103.00
                        st.write(f"売掛額{i+1} USD: {usd_amount:,.2f}")
                        st.write(f"JPY換算: {urikake_amount:,.0f}")
                    elif currency == "EUR":
                        eur_amount_input = st.number_input(f"売掛額{i+1} EUR", placeholder="入力")
                        eur_amount = float(eur_amount_input)
                        urikake_amount = eur_amount * 120.00
                        st.write(f"売掛額{i+1} EUR: {eur_amount:,.2f}")
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
                if abs(fee_amount) <= 1:
                    fee_amount = 0

                st.write(f"手数料 JPY: {abs(fee_amount):,.0f}")
            elif currency == "USD":
                deposit_amount = st.number_input(f"入金額 {currency}", min_value=0.0,key="deposit_usd_advance")
                jpy_deposit_amount = math.floor(deposit_amount * today_rate_usd)
                # 差益の計算：(当日レート - 103) * USD額
                # 103.00はコード上の基準レート
                base_rate = 103.00
                usd_amount = total_advance_amount / base_rate  # 基準レートでUSDに換算
                profit_margin = (today_rate_usd - base_rate) * usd_amount
                st.text_input("入金額 JPY", value=f"{int(jpy_deposit_amount):,.0f}", key="deposit_amount_jpy_advance", placeholder="自動計算されます")
                # 差益JPYをtext_inputで表示（自動更新されるように）
                st.text_input("差益 JPY", value=f"{int(profit_margin):,.0f}", key="profit_margin_advance_usd", placeholder="自動計算されます")
                
                fee_amount = total_advance_amount + profit_margin - jpy_deposit_amount
                # 手数料が1以下なら0に設定
                if abs(fee_amount) <= 1:
                    fee_amount = 0
                st.text_input("手数料 JPY", value=f"{abs(fee_amount):,.0f}", key="fee_amount_advance_jpy", placeholder="自動計算されます")
                
                
            elif currency == "EUR":
                deposit_amount = st.number_input(f"入金額 {currency}", min_value=0.0)
                jpy_deposit_amount = math.floor(deposit_amount * today_rate_eur)

                # 差益の計算：(当日レート - 120) * EUR額
                # 120.00はコード上の基準レート
                base_rate = 120.00
                eur_amount = total_advance_amount / base_rate  # 基準レートでEURに換算
                profit_margin = (today_rate_eur - base_rate) * eur_amount

                # 入金額JPYをtext_inputで表示
                st.text_input("入金額 JPY", value=f"{int(jpy_deposit_amount):,.0f}", key="deposit_amount_jpy_advance_eur", placeholder="自動計算されます") 

                # 差益JPYをtext_inputで表示（自動更新されるように）
                st.text_input("差益 JPY", value=f"{int(profit_margin):,.0f}", key="profit_margin_advance_eur", placeholder="自動計算されます")

                fee_amount = total_advance_amount + profit_margin - jpy_deposit_amount
                # 手数料が1以下なら0に設定
                if abs(fee_amount) <= 1:
                    fee_amount = 0
                st.text_input("手数料 JPY", value=f"{abs(fee_amount):,.0f}", key="fee_amount_advance_jpy", placeholder="自動計算されます")

        elif method == "売掛":
            st.write(f"合計売掛額 JPY: {total_urikake_amount:,.0f}")

            if currency == "JPY":
                deposit_amount = st.number_input("入金額 JPY", min_value=0.0, max_value=float(total_urikake_amount))
                fee_amount = total_urikake_amount - deposit_amount
                # 手数料が1以下なら0に設定
                if abs(fee_amount) <= 1:
                    fee_amount = 0
                st.write(f"手数料 JPY: {abs(fee_amount):,.0f}")
            
            if currency == "USD":
                deposit_amount = st.number_input(f"入金額 {currency}", min_value=0.0)
                jpy_deposit_amount = math.floor(deposit_amount * today_rate_usd)

                # 差益の計算：(当日レート - 103) * USD額
                base_rate = 103.00
                usd_amount = total_urikake_amount / base_rate  # 基準レートでUSDに換算
                profit_margin = (today_rate_usd - base_rate) * usd_amount
                # 入金額JPYをtext_inputで表示
                st.text_input("入金額 JPY", value=f"{int(jpy_deposit_amount):,.0f}", key="deposit_amount_jpy_urikake_usd", placeholder="自動計算されます")
                
                # 差益JPYをtext_inputで表示（自動更新されるように）
                st.text_input("差益 JPY", value=f"{int(profit_margin):,.0f}", key="profit_margin_urikake_usd", placeholder="自動更新されます")
                
                # 手数料の計算：売掛額 + 差益 - 入金額
                fee_amount = total_urikake_amount + profit_margin - jpy_deposit_amount
                # 手数料が1以下なら0に設定
                if abs(fee_amount) <= 1:
                    fee_amount = 0
                st.text_input("手数料 JPY", value=f"{abs(fee_amount):,.0f}", key="fee_amount_urikake_jpy", placeholder="自動計算されます")
            
            elif currency == "EUR":
                deposit_amount = st.number_input(f"入金額 {currency}", min_value=0.0)
                jpy_deposit_amount = math.floor(deposit_amount * today_rate_eur)

                # 差益の計算：(当日レート - 120) * EUR額
                base_rate = 120.00
                eur_amount = total_urikake_amount / base_rate  # 基準レートでEURに換算
                profit_margin = (today_rate_eur - base_rate) * eur_amount

                st.text_input("入金額 JPY", value=f"{int(jpy_deposit_amount):,.0f}", key="deposit_amount_jpy_urikake_eur", placeholder="自動計算されます")
                
                # 差益JPYをtext_inputで表示（自動更新されるように）
                st.text_input("差益 JPY", value=f"{int(profit_margin):,.0f}", key="profit_margin_urikake_eur", placeholder="自動計算されます")
                
                # 手数料の計算：売掛額 + 差益 - 入金額
                fee_amount = total_urikake_amount + profit_margin - jpy_deposit_amount
                # 手数料が1以下なら0に設定
                if abs(fee_amount) <= 1:
                    fee_amount = 0
                st.text_input("手数料 JPY", value=f"{abs(fee_amount):,.0f}", key="fee_amount_urikake_jpy", placeholder="自動計算されます")
            
       

    # データベースに追加
    if st.button("データベースへ追加"):
        if method == "前受入金":
            if currency == "JPY":
                profit_margin = 0  # JPYの場合は差益なし
            elif currency == "USD":
                profit_margin = int(jpy_deposit_amount + fee_amount - total_advance_amount)
            elif currency == "EUR":
                profit_margin = int(jpy_deposit_amount + fee_amount - total_advance_amount)
            for detail in plan_details:
                add_payment(
                    method=method,
                    currency=currency,
                    paytype=paytype,
                    customer=customer,
                    total_advance_amount=detail["advance_amount"],
                    deposit_amount=deposit_amount,
                    fee_amount=int(fee_amount),
                    profit_margin=profit_margin,
                    plan_number=detail["plan_number"]
                )
        elif method == "売掛":
            for detail in plan_details:
                if currency == "USD":
                    profit_margin = int((today_rate_usd - 103) * (total_urikake_amount/103.00))
                elif currency == "EUR":
                    profit_margin = int((today_rate_eur - 120) * (total_urikake_amount/120.00))
                else:  # JPY
                    profit_margin = 0
                add_payment(
                    method=method,
                    currency=currency,
                    paytype=paytype,
                    customer=customer,
                    total_advance_amount=0,
                    total_urikake_amount=detail["urikake_amount"],
                    deposit_amount=deposit_amount,
                    fee_amount=int(fee_amount),
                    profit_margin=profit_margin,
                    invoice_number=None if currency == "JPY" else detail["invoice_number"],
                    plan_number=detail["plan_number"] if currency == "JPY" else None,
                    urikake_date=detail["urikake_date"]
                )
        
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
                
                st.rerun()
            else:
                st.error("削除に失敗しました。")
    else:
        st.write("データがありません")



