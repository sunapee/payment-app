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

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.subheader("入金伝票")
    method = st.selectbox("入金タイプ", ["前受入金", "売掛"], key="method")
    currency = st.selectbox("通貨", ["JPY", "USD", "EUR"], key="currency")
    paytype = st.selectbox("一部or全部", ["全部", "一部"], key="paytype")
    customer = st.text_input("顧客名", key="customer")

    today_rate_usd = 103.0
    today_rate_eur = 120.0

    if currency == "USD":
        today_rate_usd_input = st.text_input("今日のレート (USD)", placeholder="入力", key="rate_usd")
        try:
            today_rate_usd = float(today_rate_usd_input) if today_rate_usd_input else 103.0
            if today_rate_usd <= 0:
                st.error("レートは0より大きい値を入力してください")
                today_rate_usd = 103.0
        except ValueError:
            st.error("有効な数値を入力してください")
            today_rate_usd = 103.0

    elif currency == "EUR":
        today_rate_eur_input = st.text_input("今日のレート (EUR)", placeholder="入力", key="rate_eur")
        try:
            today_rate_eur = float(today_rate_eur_input) if today_rate_eur_input else 120.0
            if today_rate_eur <= 0:
                st.error("レートは0より大きい値を入力してください")
                today_rate_eur = 120.0
        except ValueError:
            st.error("有効な数値を入力してください")
            today_rate_eur = 120.0

with col2:
    st.subheader("計画/Invoice")
    plan_details = []
    total_amount = 0.0

    if method == "前受入金":
        num_plans = st.number_input("計画番号の数", min_value=1, value=1, key="num_plans_advance")
        for i in range(int(num_plans)):
            plan_number = st.text_input(f"計画番号 {i + 1}", key=f"plan_number_adv_{i}")
            amount_jpy_for_plan = 0.0
            if currency == "JPY":
                amount_input = st.text_input(f"前受額{i + 1} JPY", placeholder="入力", key=f"advance_jpy_{i}")
                try:
                    amount = float(amount_input) if amount_input else 0.0
                except ValueError:
                    amount = 0.0
                st.write(f"前受額{i + 1} JPY: {amount:,.0f}")
                amount_jpy_for_plan = amount
            elif currency == "USD":
                amount_input = st.text_input(f"前受額{i + 1} USD", placeholder="入力", key=f"advance_usd_{i}")
                try:
                    amount_usd = float(amount_input) if amount_input else 0.0
                except ValueError:
                    amount_usd = 0.0
                amount_jpy = amount_usd * today_rate_usd
                st.write(f"前受額{i + 1} USD: {amount_usd:,.2f}")
                st.write(f"JPY換算: {amount_jpy:,.0f}")
                amount_jpy_for_plan = amount_jpy
            elif currency == "EUR":
                amount_input = st.text_input(f"前受額{i + 1} EUR", placeholder="入力", key=f"advance_eur_{i}")
                try:
                    amount_eur = float(amount_input) if amount_input else 0.0
                except ValueError:
                    amount_eur = 0.0
                amount_jpy = amount_eur * today_rate_eur
                st.write(f"前受額{i + 1} EUR: {amount_eur:,.2f}")
                st.write(f"JPY換算: {amount_jpy:,.0f}")
                amount_jpy_for_plan = amount_jpy
            
            total_amount += amount_jpy_for_plan
            plan_details.append({"plan_number": plan_number, "amount": amount_jpy_for_plan})

    elif method == "売掛":
        if currency == "JPY":
            num_plans = st.number_input("計画No/INVOICEの数", min_value=1, value=1, key="num_plans_urikake_jpy")
            for i in range(int(num_plans)):
                plan_number = st.text_input(f"計画(国内)No /INVOICE(海外)No {i + 1}", key=f"plan_number_urikake_jpy_{i}")
                urikake_date = st.date_input(f"売掛日 {i + 1}", key=f"urikake_date_jpy_{i}")
                amount_input = st.text_input(f"売掛額{i + 1} JPY", placeholder="入力", key=f"urikake_jpy_{i}")
                try:
                    amount = float(amount_input) if amount_input else 0.0
                except ValueError:
                    amount = 0.0
                st.write(f"売掛額{i + 1} JPY: {amount:,.0f}")
                total_amount += amount
                plan_details.append({"plan_number": plan_number, "amount": amount, "date": urikake_date})
        else:
            num_invoice = st.number_input("Invoiceの数", min_value=1, value=1, key="num_invoice")
            total_usd_amount = 0.0
            
            for i in range(int(num_invoice)):
            invoice_number = st.text_input(f"Invoice番号 {i + 1}", key=f"invoice_number_{i}")
            urikake_date = st.date_input(f"売掛日 {i + 1}", key=f"invoice_date_{i}")
            if currency == "USD":
                amount_input = st.text_input(f"売掛額{i + 1} USD", placeholder="入力", key=f"urikake_usd_{i}")
                try:
                    amount_usd = float(amount_input) if amount_input else 0.0
                except ValueError:
                    amount_usd = 0.0
                amount_jpy = math.floor(amount_usd * today_rate_usd)
                st.write(f"売掛額{i + 1} USD: {amount_usd:,.2f}")
                st.write(f"JPY換算: {amount_jpy:,.0f}")
                total_amount += amount_jpy
                # 修正: USDの合計額を加算
                total_usd_amount += amount_usd
                plan_details.append({"invoice_number": invoice_number, "amount": amount_jpy, "date": urikake_date})
                
                elif currency == "EUR":
                    amount_input = st.text_input(f"売掛額{i + 1} EUR", placeholder="入力", key=f"urikake_eur_{i}")
                    try:
                        amount_eur = float(amount_input) if amount_input else 0.0
                    except ValueError:
                        amount_eur = 0.0
                    amount_jpy = math.floor(amount_eur * today_rate_eur)
                    st.write(f"売掛額{i + 1} EUR: {amount_eur:,.2f}")
                    st.write(f"JPY換算: {amount_jpy:,.0f}")
                    total_amount += amount_jpy
                    total_eur_amount += amount_eur
                    plan_details.append({"invoice_number": invoice_number, "amount": amount_jpy, "date": urikake_date})


with col3:
    
    st.subheader("金額詳細")
    
    if method == "前受入金":
        st.write(f"合計前受額 JPY: {total_amount:,.0f}")
    elif method == "売掛":
        st.write(f"合計売掛額 JPY: {total_amount:,.0f}")

    # --- 修正点: 堅牢性を高めたコールバック関数 ---
    def update_manual_input(target_key, input_key, auto_value):
        input_value = st.session_state.get(input_key)

        # 入力が空（Noneや空文字列）の場合は、自動計算値に戻す
        if not input_value:
            st.session_state[target_key] = auto_value
            return

        try:
            # カンマを削除して数値に変換
            numeric_value = int(str(input_value).replace(',', ''))
            st.session_state[target_key] = numeric_value
        except (ValueError, TypeError):
            # "abc"のような無効な入力の場合も、自動計算値に戻す
            st.session_state[target_key] = auto_value

    if currency == "JPY":
        deposit_amount_input = st.text_input("入金額 JPY", placeholder="0以上の数値を入力", key="deposit_jpy")
        try:
            deposit_amount = float(deposit_amount_input) if deposit_amount_input else 0.0
            if deposit_amount < 0:
                st.error("入金額は0以上で入力してください")
                deposit_amount = 0.0
        except ValueError:
            st.error("有効な数値を入力してください")
            deposit_amount = 0.0
        
        st.write(f"入金額 JPY: {deposit_amount:,.0f}")
        fee_amount = total_amount - deposit_amount
        if abs(fee_amount) <= 1:
            fee_amount = 0
        st.write(f"手数料 JPY: {abs(fee_amount):,.0f}")

    elif currency in ["USD", "EUR"]:
        base_rate = 103.00 if currency == "USD" else 120.00
        today_rate = today_rate_usd if currency == "USD" else today_rate_eur

        deposit_amount_input = st.text_input(f"入金額 {currency}", placeholder="0以上の数値を入力", key=f"deposit_{currency.lower()}")
        try:
            deposit_amount = float(deposit_amount_input) if deposit_amount_input else 0.0
            if deposit_amount < 0:
                st.error("入金額は0以上で入力してください")
                deposit_amount = 0.0
        except ValueError:
            st.error("有効な数値を入力してください")
            deposit_amount = 0.0
        
        st.write(f"入金額 {currency}: {deposit_amount:,.2f}")

        # 自動計算
        auto_jpy_deposit = math.floor(deposit_amount * today_rate)
        foreign_amount_for_profit = total_amount / base_rate if base_rate > 0 else 0
        auto_profit_margin_raw = (today_rate - base_rate) * total_usd_amount
        auto_profit_margin = math.floor(auto_profit_margin_raw + 0.0000001)
        auto_fee_amount = total_amount + auto_profit_margin - auto_jpy_deposit
        if abs(auto_fee_amount) <= 1:
            auto_fee_amount = 0

        # セッションステートのキー
        deposit_key = f'manual_deposit_{method}_{currency}'
        profit_key = f'manual_profit_{method}_{currency}'
        fee_key = f'manual_fee_{method}_{currency}'
        last_deposit_key = f'last_deposit_{method}_{currency}'

        # 外貨入金額の変更時や初回表示時にセッションステートをリセット/初期化
        if st.session_state.get(last_deposit_key) != deposit_amount or deposit_key not in st.session_state:
            st.session_state[deposit_key] = auto_jpy_deposit
            st.session_state[profit_key] = auto_profit_margin
            st.session_state[fee_key] = auto_fee_amount
            st.session_state[last_deposit_key] = deposit_amount
            
            # --- 修正点: value引数を削除したので、ウィジェットの表示をリセットするためにキーの値を直接更新 ---
            st.session_state[f"deposit_input_{method}_{currency}"] = f"{auto_jpy_deposit:,.0f}"
            st.session_state[f"profit_input_{method}_{currency}"] = f"{auto_profit_margin:,.0f}"
            st.session_state[f"fee_input_{method}_{currency}"] = f"{auto_fee_amount:,.0f}"


        # 入力ウィジェットのキー
        deposit_input_key = f"deposit_input_{method}_{currency}"
        profit_input_key = f"profit_input_{method}_{currency}"
        fee_input_key = f"fee_input_{method}_{currency}"
        
        # JPY入金額
        calculated_amount_label = f"入金額 JPY ({deposit_amount:,.2f} × {today_rate:.2f} = {auto_jpy_deposit:,.0f})"
        st.text_input(
            calculated_amount_label,
            # 修正点: value引数を削除
            key=deposit_input_key,
            on_change=update_manual_input,
            args=(deposit_key, deposit_input_key, auto_jpy_deposit)
        )
        
        # 差益
        profit_label = f"差益 JPY (({today_rate:.2f} - {base_rate:.2f}) × {foreign_amount_for_profit:,.2f} = {auto_profit_margin_raw:,.2f})"
        st.text_input(
            profit_label,
            # 修正点: value引数を削除
            key=profit_input_key,
            on_change=update_manual_input,
            args=(profit_key, profit_input_key, auto_profit_margin)
        )
        
        # 手数料
        current_profit = st.session_state.get(profit_key, 0)
        current_deposit = st.session_state.get(deposit_key, 0)
        manual_fee_calc = total_amount + current_profit - current_deposit
        fee_label = f"手数料 JPY ({total_amount:,.0f} + {current_profit:,.0f} - {current_deposit:,.0f} = {manual_fee_calc:,.0f})"
        st.text_input(
            fee_label,
            # 修正点: value引数を削除
            key=fee_input_key,
            on_change=update_manual_input,
            args=(fee_key, fee_input_key, auto_fee_amount)
        )
