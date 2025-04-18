# 入金管理アプリ

## 概要

このアプリは、Streamlit を使用して構築された入金管理アプリケーションです。

## 機能

- **入金データの登録**
  - 入金タイプ（前受入金 / 売掛）を選択可能
  - 通貨（JPY / USD / EUR）を選択可能
  - 顧客名の入力
  - 計画番号またはInvoice番号の管理
  - 入金額・売掛額の入力
  - 手数料および差益の自動計算

## 使用技術

- **Python**: メインのプログラミング言語
- **Streamlit**: Web アプリケーションのフレームワーク
- **GitHub**: バージョン管理およびデプロイ用のリポジトリ
- **Streamlit Cloud**: アプリのデプロイ環境

## 環境構築手順

### 1. リポジトリの作成とクローン

```sh
# GitHub に新しいリポジトリを作成
# ローカル環境でリポジトリをクローン

git clone https://github.com/sunapee/payment-app
cd payment-app
```

### 2. 必要なパッケージのインストール

```sh
pip install -r requirements.txt
```

### 4. アプリの実行

```sh
streamlit run payments.py
```

## デプロイ手順

### 1. GitHub に変更をプッシュ

```sh
git add .
git commit -m "Update app"
git push origin main
```

### 2. Streamlit Cloud にデプロイ

1. [Streamlit Cloud](https://share.streamlit.io/) にログイン
2. 「新しいアプリをデプロイ」
3. GitHub リポジトリを選択
4. `payments.py` をエントリーポイントに設定
5. デプロイを実行

### 3. 変更を反映する方法

変更後に GitHub にプッシュし、Streamlit Cloud で `Rerun` ボタンをクリックすると最新の状態が反映されます。

## 参考

- [Streamlit 公式ドキュメント](https://docs.streamlit.io/)

