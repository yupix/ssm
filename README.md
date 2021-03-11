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

#### プロジェクト直下に.envを設置し以下の項目を設定する(必須)

```
# Bot情報
SSM_BOT_TOKEN = DiscordBotのトークン

# データベース周り
SSM_DB_USER = データベースのユーザー
SSM_DB_PASSWORD = 上記で設定したユーザーのパスワード

# 読み上げ機能（保守されていないのでNoneで問題ない）
SSM_JTALK_DIC_PATH = None
SSM_VOICE_PATH = None
SSM_JTALK_BIN_PATH = None
```

### 推奨: ホストに構築（すべての機能が利用可能）

```cmd
git clone <https://github.com/yupix/ssm.git>

cd ssm
python main.py
```

## データベース定義に関して

データベース定義に関しては [こちら](./doc/schema)をご覧ください。

## コマンド一覧

現在作成中
