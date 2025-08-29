# 薬管理アプリ
このプロジェクトは、PythonのFlaskとSQLiteをベースにしたシンプルなウェブベースの薬管理アプリケーションです。日々の薬の服用記録をカレンダー形式で管理できます。

# 機能一覧
* 月間カレンダー表示: 現在の月を表示し、「前月」「次月」でナビゲーションできます。
* 薬の登録・編集・削除: 特定の日付をタップして、薬の新規登録、既存薬の編集・削除が可能です。
* 服用状況の記録: カレンダーに表示された薬名をタップすると、服用済みとしてマークされます。
* 通知機能: 設定した服用時間になると、音とメッセージで通知します。

# 技術スタック
* バックエンド: Python, Flask, SQLAlchemy
* データベース: SQLite
* フロントエンド: HTML, CSS, JavaScript

# セットアップ方法
以下の手順に従って、ローカル環境でアプリケーションをセットアップおよび実行できます。

1. 仮想環境の構築
プロジェクトのルートディレクトリで、以下のコマンドを実行して仮想環境を作成し、有効化します。
```
# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化 (Windows)
venv\Scripts\activate

# 仮想環境を有効化 (macOS/Linux)
source venv/bin/activate
```
2. 依存ライブラリのインストール
requirements.txt に記載されている必要なライブラリをインストールします。
```
pip install -r requirements.txt
```
3. アプリケーションの実行
以下のコマンドでアプリケーションを起動します。
```
python app.py
```
※VSCodeの場合、エクスプローラーでapp.pyを選択して「実行」でもOK！

サーバーが起動したら、ブラウザで http://127.0.0.1:5000 にアクセスしてください。

ファイル構成
```
.
├── .gitignore             # Gitのバージョン管理から除外するファイルを指定
├── app.py                 # Flaskアプリケーションのメインファイル
├── database.py            # データベース接続とモデルの定義
├── requirements.txt       # プロジェクトの依存ライブラリ一覧
├── templates/
│   ├── layout.html        # 全ページの基本レイアウト
│   ├── calendar.html      # カレンダー表示ページ
│   └── medicine_form.html # 薬の登録・編集フォーム
└── static/
    ├── css/
    │   └── style.css      # スタイルシート
    ├── js/
    │   └── script.js      # フロントエンドのJavaScript
    └── sounds/
        └── alarm.mp3      # 通知音
```

ライセンス
このプロジェクトは、[MIT License](https://opensource.org/license/MIT)　のもとで公開されています。