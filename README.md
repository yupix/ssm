# SSM Project

![ssm](https://repo.akarinext.org/assets/image/YX.png)

## 注意

このProjectを使用する場合はmasterブランチを使用することを強く推奨します。
masterブランチはtestingブランチがある程度安定したと判断した際にのみ更新され、
基本的にtestingブランチは不安定な状態の機能や作りかけの機能が大量にあるため開発者や、新機能を試す以外では絶対に使わないでください。

## このREADMEに関する注意点

コマンドなどに関してはほとんどが未完成品であり、編集仕立ての場合、

## 概要

このProjectはIntegrationServer専用に作成しているものです。
このProjectは[AGPL](LICENSE)ライセンスのもと配布または使用することができます

## 使い方
open-jtalkが別途必要です

### 推奨: Dockerに構築(一部機能が利用不可)
```
git clone https://github.com/yupix/ssm.git

#.configとdocker-compose.ymlを変更する
docker-compose build
docker-compose up -d
```
### 非推奨: ホストに構築(すべての機能が利用可能)
```
git clone https://github.com/yupix/ssm.git


cd ssm
python main.py
```

## CONFIG

### COMMAND

基本的にコマンドの使用可能かいなかはサーバー毎に設定できるべきであり何らかの理由で自分のBotが入ってるサーバーで特定のコマンドをoffにすることができます  

#### コマンド一覧

コマンドの前にはtu!などのprefixが必要です。 例: `tu!ping`  
%user_id%はユーザーを右クリックで取得可能なid(開発者モードon必須かも)


| コマンド名 | 使い方|
|---|---|
|blocklist add %user_id%|指定したユーザーをブロックリストに登録します。|

#### 値に関して

- true: 全サーバーで有効
- false: 全サーバーで無効


| コマンド名 | デフォルト値 |
|---|---|
|blogcategory|true|
