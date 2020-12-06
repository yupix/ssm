# SSM Project

![ssm](https://repo.akarinext.org/assets/image/YX.png)

## 注意

1. このbranchが`testing`の場合作成途中のものや、そもそも動かないことが多々あるため推奨していません
2. このREADMEの更新は非常に遅れており、コマンドなども一切更新ができていません

## 概要

このProjectはIntegrationServer専用に作成しているものです。
このProjectは[AGPL](LICENSE)ライセンスのもと配布または使用できます

## 使い方

open-jtalkが別途必要です

### 推奨: Dockerに構築（一部機能が利用不可）

```cmd
git clone https://github.com/yupix/ssm.git

#.configとdocker-compose.ymlを変更する
docker-compose build
docker-compose up -d
```

### 非推奨: ホストに構築（すべての機能が利用可能）

```cmd
git clone <https://github.com/yupix/ssm.git>

cd ssm
python main.py
```

## データベース定義に関して

データベース定義に関しては [こちら](./doc/schema)をご覧ください。

## コマンド一覧

現在作成中
