# SSM Project

![ssm](https://repo.akarinext.org/assets/image/YX.png)

## 注意

このブランチがtestingの場合は絶対に本番環境で動かさないでください！
理由はこのブランチは現在大幅な変更を加えており、まだ直しきれていなくてもpushして少しでも変更を分かりやすくするために
作成しているものです。このブランチを使うことで発生した問題などは一切対応しないのでご注意ください。

## 概要

このProjectはIntegrationServer専用に作成しているものです。
このProjectは[AGPL](LICENSE)ライセンスのもと配布または使用することができます

## 使い方

```
#MAIN REPOSITORY
git clone https://lab.akarinext.org/yupix/ssm.git

#SUB REPOSITORY 
git clone https://lab.akirin.xyz/yupix/ssm.git


cd ssm
python main.py

#ブログでの権限をインポート(必須)
db_user='root' # データベースのユーザー名に指定してください
mysql -u ${db_user} -p -h localhost default_discord < ./template/role.txt'
```

## CONFIG

### COMMAND

基本的にコマンドの使用可能かいなかはサーバー毎に設定できるべきであり何らかの理由で自分のBotが入ってるサーバーで特定のコマンドをoffにすることができます  

#### 値に関して

- true: 全サーバーで有効
- false: 全サーバーで無効


| コマンド名 | デフォルト値 |
|---|---|
|blogcategory|true|

## REPOSITORY構造

- [MAIN Repository](https://lab.akarinext.org/yupix/ssm)
- [SUB Repository](https://lab.akirin.xyz/yupix/ssm)
- [BACKUP Repository](https://github.com/yupix/ssm)

