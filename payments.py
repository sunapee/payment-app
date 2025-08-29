import streamlit as st
import pandas as pd
import time
import os   
import math
import csv
from datetime import datetime

st.set_page_config(
    page_icon="💰",  # グラフ上昇の絵文字をアイコンとして使用
)

def check_password():
    def password_entered():
        if st.session_state["password"] == "4649":
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.image("ncc_logo.jpg", use_container_width=True)
        st.text_input("パスワードを入力してください", type="password", on_change=password_entered, key="password")
        st.stop()

check_password()

def load_css():
    css_file = os.path.join(os.path.dirname(__file__), 'style.css')
    if os.path.exists(css_file):
        with open(css_file, encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    else:
        st.error("style.cssファイルが見つかりません。")

load_css()

# Custom title with added styling
#st.markdown('<div class="title">入金伝票作成システム</div>', unsafe_allow_html=True)

# メインコンテンツ
#st.header("入金伝票")
col1, col2, col3 = st.columns([1,1,1])

with col1:
    st.subheader("入金伝票")
    
    method = st.selectbox("入金タイプ", ["前受入金", "売掛"])
    currency = st.selectbox("通貨", ["JPY", "USD", "EUR"])
    paytype = st.selectbox("一部or全部", ["全部", "一部"])
    customer = st.text_input("顧客名")

    # レート変数の初期化
    today_rate_usd = 103.0
    today_rate_eur = 120.0

    if (method == "売掛" or method == "前受入金") and currency == "USD":
        today_rate_usd_input = st.text_input("今日のレート (USD)", placeholder="入力",key="rate_usd")
        # 入力値の検証と変換
        try:
            today_rate_usd = float(today_rate_usd_input) if today_rate_usd_input else 103.0
            if today_rate_usd <= 0:
                st.error("レートは0より大きい値を入力してください")
                today_rate_usd = 103.0  # デフォルト値
        except ValueError:
            st.error("有効な数値を入力してください")
            today_rate_usd = 103.0  # デフォルト値
            
    elif (method == "売掛" or method == "前受入金") and currency == "EUR":
        today_rate_eur_input = st.text_input("今日のレート (EUR)", placeholder="入力",key="rate_eur")
        # 入力値の検証と変換
        try:
            today_rate_eur = float(today_rate_eur_input) if today_rate_eur_input else 120.0
            if today_rate_eur <= 0:
                st.error("レートは0より大きい値を入力してください")
                today_rate_eur = 120.0  # デフォルト値
        except ValueError:
            st.error("有効な数値を入力してください")
            today_rate_eur = 120.0  # デフォルト値    

with col2:
    st.subheader("計画/Invoice")
    if method == "前受入金":
        num_plans = st.number_input("計画番号の数", min_value=1, value=1)
        total_advance_amount: float = 0.0
        plan_details = []

        for i in range(int(num_plans)):
            plan_number = st.text_input(f"計画番号 {i+1}")
            if currency == "JPY":
                advance_amount_input = st.text_input(f"前受額{i+1} JPY", placeholder="入力",key=f"advance_jpy_{i}")

                # 入力値を数値に変換（空欄や不正値は0扱い）
                try:
                    advance_amount = float(advance_amount_input) if advance_amount_input else 0.0
                except ValueError:
                    advance_amount = 0.0
                
                st.write(f"前受額{i+1} JPY: {advance_amount:,.0f}")
                
            elif currency == "USD":
                usd_amount_input = st.text_input(f"前受額{i+1} USD", placeholder="入力",key=f"advance_usd_{i}")
                # 入力値を数値に変換（空欄や不正値は0扱い）
                try:
                    usd_amount = float(usd_amount_input) if usd_amount_input else 0.0
                except ValueError:
                    usd_amount = 0.0
                
                advance_amount = usd_amount * 103.00
                st.write(f"前受額{i+1} USD: {usd_amount:,.2f}")
                st.write(f"JPY換算: {advance_amount:,.0f}")
            elif currency == "EUR":
                eur_amount_input = st.text_input(f"前受額{i+1} EUR", placeholder="入力",key=f"advance_eur_{i}")
                # 入力値を数値に変換（空欄や不正値は0扱い）
                try:
                    eur_amount = float(eur_amount_input) if eur_amount_input else 0.0
                except ValueError:
                    eur_amount = 0.0
                advance_amount = eur_amount * 120.00    
                st.write(f"前受額{i+1} EUR: {eur_amount:,.2f}")
                st.write(f"JPY換算: {advance_amount:,.0f}")

            plan_details.append({
                "plan_number": plan_number,
                "advance_amount": advance_amount
            })
            total_advance_amount += advance_amount

    elif method == "売掛":
        if currency == "JPY":
            num_plans = st.number_input("計画No/INVOICEの数", min_value=1, value=1)
            total_urikake_amount: float = 0.0
            plan_details = []

            for i in range(int(num_plans)):
                plan_number = st.text_input(f"計画(国内)No /INVOICE(海外)No {i+1}")
                urikake_date = st.date_input(f"売掛日 {i+1}")
                urikake_amount_input = st.text_input(f"売掛額{i+1} JPY", placeholder="入力")
                # 入力値を数値に変換（空欄や不正値は0扱い）
                try:
                    urikake_amount = float(urikake_amount_input) if urikake_amount_input else 0.0   
                except ValueError:
                    urikake_amount = 0.0
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
                    usd_amount_input = st.text_input(f"売掛額{i+1} USD", placeholder="入力")
                    try:
                        usd_amount = float(usd_amount_input) if usd_amount_input else 0.0
                    except ValueError:
                        usd_amount = 0.0
                    urikake_amount = math.floor(usd_amount * 103.00)
                    st.write(f"売掛額{i+1} USD: {usd_amount:,.2f}")
                    st.write(f"JPY換算: {urikake_amount:,.0f}")
                elif currency == "EUR":
                    eur_amount_input = st.text_input(f"売掛額{i+1} EUR", placeholder="入力")
                    try:
                        eur_amount = float(eur_amount_input) if eur_amount_input else 0.0
                    except ValueError:
                        eur_amount = 0.0
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
            # 修正: text_inputからmin_value, max_valueパラメータを削除し、検証を手動で行う
            deposit_amount_input = st.text_input("入金額 JPY", placeholder="0以上の数値を入力")
            
            # 入力値の検証と変換
            try:
                deposit_amount = float(deposit_amount_input) if deposit_amount_input else 0.0
                if deposit_amount < 0:
                    st.error("入金額は0以上で入力してください")
                    deposit_amount = 0.0
                elif deposit_amount > total_advance_amount:
                    st.error(f"入金額は{total_advance_amount:,.0f}以下で入力してください")
                    deposit_amount = total_advance_amount
            except ValueError:
                st.error("有効な数値を入力してください")
                deposit_amount = 0.0
                
            st.write(f"入金額 JPY: {deposit_amount:,.0f}")
            fee_amount = total_advance_amount - deposit_amount
            if abs(fee_amount) <= 1:
                fee_amount = 0
            st.write(f"手数料 JPY: {abs(fee_amount):,.0f}")
            
        elif currency == "USD":
            # 修正: text_inputからmin_valueパラメータを削除
            deposit_amount_input = st.text_input(f"入金額 {currency}", placeholder="0以上の数値を入力", key="deposit_usd_advance")
            
            # 入力値の検証と変換
            try:
                deposit_amount = float(deposit_amount_input) if deposit_amount_input else 0.0
                if deposit_amount < 0:
                    st.error("入金額は0以上で入力してください")
                    deposit_amount = 0.0
            except ValueError:
                st.error("有効な数値を入力してください")
                deposit_amount = 0.0

            st.write(f"入金額 USD: {deposit_amount:,.0f}")
                
            jpy_deposit_amount = math.floor(deposit_amount * today_rate_usd)
            # 差益の計算：(当日レート - 103) * USD額
            # 103.00はコード上の基準レート
            base_rate = 103.00
            usd_amount = total_advance_amount / base_rate  # 基準レートでUSDに換算
            profit_margin_raw = (today_rate_usd - base_rate) * usd_amount  # floor前の値
            profit_margin = math.floor((today_rate_usd - base_rate) * usd_amount + 0.0000001)

            # 計算結果を小数点第2位まで表示
            calculated_amount = deposit_amount * today_rate_usd
            deposit_label = f"入金額 JPY ({deposit_amount:,.2f} × {today_rate_usd:.2f} = {calculated_amount:,.2f})"

            st.text_input(deposit_label, value=f"{int(jpy_deposit_amount):,.0f}", key="deposit_amount_jpy_advance", placeholder="自動計算されます")
            
            # 差益JPYをtext_inputで表示（自動更新されるように）
            profit_label = f"差益 JPY (({today_rate_usd:.2f} - {base_rate:.2f}) × {usd_amount:,.2f} = {profit_margin_raw:,.2f})"
            st.text_input(profit_label, value=f"{profit_margin:,.0f}", key="profit_margin_advance_usd", placeholder="自動計算されます")

            jpy_deposit_amount_int = int(jpy_deposit_amount)
            profit_margin_int = int(profit_margin)
            total_advance_amount_int = int(total_advance_amount)

            fee_amount = total_advance_amount_int + profit_margin_int - jpy_deposit_amount_int

            # 手数料が1以下なら0に設定
            if abs(fee_amount) <= 1:
                fee_amount = 0

            # 手数料の計算過程を表示
            fee_label = f"手数料 JPY ({total_advance_amount_int:,.0f} + {profit_margin_int:,.0f} - {jpy_deposit_amount_int:,.0f} = {fee_amount:,.0f})"
            st.text_input(fee_label, value=f"{fee_amount:,.0f}", key="fee_amount_advance_usd", placeholder="自動計算されます")

        elif currency == "EUR":
            # 修正: text_inputからmin_valueパラメータを削除
            deposit_amount_input = st.text_input(f"入金額 {currency}", placeholder="0以上の数値を入力")
            
            # 入力値の検証と変換
            try:
                deposit_amount = float(deposit_amount_input) if deposit_amount_input else 0.0
                if deposit_amount < 0:
                    st.error("入金額は0以上で入力してください")
                    deposit_amount = 0.0
            except ValueError:
                st.error("有効な数値を入力してください")
                deposit_amount = 0.0

            st.write(f"入金額 EUR: {deposit_amount:,.0f}")
                
            jpy_deposit_amount = math.floor(deposit_amount * today_rate_eur)

            # 差益の計算：(当日レート - 120) * EUR額
            # 120.00はコード上の基準レート
            base_rate = 120.00
            eur_amount = total_advance_amount / base_rate  # 基準レートでEURに換算
            profit_margin_raw = (today_rate_eur - base_rate) * eur_amount  # floor前の値
            profit_margin = math.floor((today_rate_eur - base_rate) * eur_amount + 0.0000001)

            # 計算結果を小数点第2位まで表示
            calculated_amount = deposit_amount * today_rate_eur
            deposit_label = f"入金額 JPY ({deposit_amount:,.2f} × {today_rate_eur:.2f} = {calculated_amount:,.2f})"
           
            st.text_input(deposit_label, value=f"{int(jpy_deposit_amount):,.0f}", key="deposit_amount_jpy_advance_eur", placeholder="自動計算されます")

            # 差益JPYをtext_inputで表示（自動更新されるように）
            profit_label = f"差益 JPY (({today_rate_eur:.2f} - {base_rate:.2f}) × {eur_amount:,.2f} = {profit_margin_raw:,.2f})"
            st.text_input(profit_label, value=f"{profit_margin:,.0f}", key="profit_margin_advance_eur", placeholder="自動計算されます")
            
            # 前受入金・EUR
            jpy_deposit_amount_int = int(jpy_deposit_amount)
            profit_margin_int = int(profit_margin)
            total_advance_amount_int = int(total_advance_amount)

            fee_amount = total_advance_amount_int + profit_margin_int - jpy_deposit_amount_int
            
            # 手数料が1以下なら0に設定
            if abs(fee_amount) <= 1:
                fee_amount = 0

            # 手数料の計算過程を表示
            fee_label = f"手数料 JPY ({total_advance_amount_int:,.0f} + {profit_margin_int:,.0f} - {jpy_deposit_amount_int:,.0f} = {fee_amount:,.0f})"
            st.text_input(fee_label, value=f"{fee_amount:,.0f}", key="fee_amount_advance_eur", placeholder="自動計算されます")

    elif method == "売掛":
        st.write(f"合計売掛額 JPY: {total_urikake_amount:,.0f}")

        if currency == "JPY":
            # 修正: text_inputからmin_value, max_valueパラメータを削除し、検証を手動で行う
            deposit_amount_input = st.text_input("入金額 JPY", placeholder="0以上の数値を入力")
            
            # 入力値の検証と変換
            try:
                deposit_amount = float(deposit_amount_input) if deposit_amount_input else 0.0
                if deposit_amount < 0:
                    st.error("入金額は0以上で入力してください")
                    deposit_amount = 0.0
                elif deposit_amount > total_urikake_amount:
                    st.error(f"入金額は{total_urikake_amount:,.0f}以下で入力してください")
                    deposit_amount = total_urikake_amount
            except ValueError:
                st.error("有効な数値を入力してください")
                deposit_amount = 0.0

            st.write(f"入金額 JPY: {deposit_amount:,.0f}")
                
            fee_amount = total_urikake_amount - deposit_amount
            # 手数料が1以下なら0に設定
            if abs(fee_amount) <= 1:
                fee_amount = 0
            st.write(f"手数料 JPY: {abs(fee_amount):,.0f}")
        
        elif currency == "USD":
            # 修正: text_inputからmin_valueパラメータを削除
            deposit_amount_input = st.text_input(f"入金額 {currency}", placeholder="0以上の数値を入力")
            
            # 入力値の検証と変換
            try:
                deposit_amount = float(deposit_amount_input) if deposit_amount_input else 0.0
                if deposit_amount < 0:
                    st.error("入金額は0以上で入力してください")
                    deposit_amount = 0.0
            except ValueError:
                st.error("有効な数値を入力してください")
                deposit_amount = 0.0

            st.write(f"入金額 USD: {deposit_amount:,.0f}")
                
            jpy_deposit_amount = math.floor(deposit_amount * today_rate_usd)

            # 差益の計算：(当日レート - 103) * USD額
            base_rate = 103.00
            usd_amount = total_urikake_amount / base_rate  # 基準レートでUSDに換算
            profit_margin_raw = (today_rate_usd - base_rate) * usd_amount  # floor前の値
            profit_margin = math.floor((today_rate_usd - base_rate) * usd_amount + 0.0000001)
            # 入金額JPYをtext_inputで表示
            # 計算結果を小数点第2位まで表示
            calculated_amount = deposit_amount * today_rate_usd
            deposit_label = f"入金額 JPY ({deposit_amount:,.2f} × {today_rate_usd:.2f} = {calculated_amount:,.2f})"
            st.text_input(deposit_label, value=f"{int(jpy_deposit_amount):,.0f}", key="deposit_amount_jpy_urikake_usd", placeholder="自動計算されます")
            
            # 差益JPYをtext_inputで表示（自動更新されるように）
            profit_label = f"差益 JPY (({today_rate_usd:.2f} - {base_rate:.2f}) × {usd_amount:,.2f} = {profit_margin_raw:,.2f})"
            st.text_input(profit_label, value=f"{profit_margin:,.0f}", key="profit_margin_urikake_usd", placeholder="自動更新されます")
            
            # 表示用に整数化した値を使って手数料を計算
            jpy_deposit_amount_int = int(jpy_deposit_amount)
            profit_margin_int = int(profit_margin)
            total_urikake_amount_int = int(total_urikake_amount)

            # 整数で手数料を計算
            fee_amount = total_urikake_amount_int + profit_margin_int - jpy_deposit_amount_int
            # 手数料が1以下なら0に設定
            if abs(fee_amount) <= 1:
                fee_amount = 0

            # 手数料の計算過程を表示
            fee_label = f"手数料 JPY ({total_urikake_amount_int:,.0f} + {profit_margin_int:,.0f} - {jpy_deposit_amount_int:,.0f} = {fee_amount:,.0f})"
            st.text_input(fee_label, value=f"{fee_amount:,.0f}", key="fee_amount_urikake_usd", placeholder="自動計算されます")
            
        elif currency == "EUR":
            # 修正: text_inputからmin_valueパラメータを削除
            deposit_amount_input = st.text_input(f"入金額 {currency}", placeholder="0以上の数値を入力")
            
            # 入力値の検証と変換
            try:
                deposit_amount = float(deposit_amount_input) if deposit_amount_input else 0.0
                if deposit_amount < 0:
                    st.error("入金額は0以上で入力してください")
                    deposit_amount = 0.0
            except ValueError:
                st.error("有効な数値を入力してください")
                deposit_amount = 0.0
                
            st.write(f"入金額 EUR: {deposit_amount:,.0f}")
                
            jpy_deposit_amount = math.floor(deposit_amount * today_rate_eur)

            # 差益の計算：(当日レート - 120) * EUR額
            base_rate = 120.00
            eur_amount = total_urikake_amount / base_rate  # 基準レートでEURに換算
            profit_margin_raw = (today_rate_eur - base_rate) * eur_amount  # floor前の値
            profit_margin = math.floor((today_rate_eur - base_rate) * eur_amount + 0.0000001)

            # 計算結果を小数点第2位まで表示
            calculated_amount = deposit_amount * today_rate_eur
            deposit_label = f"入金額 JPY ({deposit_amount:,.2f} × {today_rate_eur:.2f} = {calculated_amount:,.2f})"
            
            st.text_input(deposit_label, value=f"{int(jpy_deposit_amount):,.0f}", key="deposit_amount_jpy_urikake_eur", placeholder="自動計算されます")
            
            # 差益JPYをtext_inputで表示（自動更新されるように）
            profit_label = f"差益 JPY (({today_rate_eur:.2f} - {base_rate:.2f}) × {eur_amount:,.2f} = {profit_margin_raw:,.2f})"
            st.text_input(profit_label, value=f"{profit_margin:,.0f}", key="profit_margin_urikake_eur", placeholder="自動計算されます")

            # 表示用に整数化した値を使って手数料を計算
            jpy_deposit_amount_int = int(jpy_deposit_amount)
            profit_margin_int = int(profit_margin)
            total_urikake_amount_int = int(total_urikake_amount)

            # 整数で手数料を計算
            fee_amount = total_urikake_amount_int + profit_margin_int - jpy_deposit_amount_int

            # 手数料が1以下なら0に設定
            if abs(fee_amount) <= 1:
                fee_amount = 0

            # 手数料の計算過程を表示
            fee_label = f"手数料 JPY ({total_urikake_amount_int:,.0f} + {profit_margin_int:,.0f} - {jpy_deposit_amount_int:,.0f} = {fee_amount:,.0f})"
            st.text_input(fee_label, value=f"{fee_amount:,.0f}", key="fee_amount_urikake_eur", placeholder="自動計算されます")
