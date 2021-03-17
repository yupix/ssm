# SSM Project

![ssm](https://s3.akarinext.org/misskey/*/29af8bc0-54d3-4ac1-801c-aef2990855cc.png)

## 注意

1. このbranchが`testing`の場合作成途中のものや、そもそも動かないことが多々あるため推奨していません
2. **releases 1.2.0からは1.0.1と大幅にデータベースの仕様が変更されており引き継ぎは不可となっています。**
2.5 migrateファイルは1.3.0からの配布となります。現在は使用しないことを推奨しています
3. このREADMEの更新は非常に遅れており、コマンドなども一切更新ができていません

## 概要

このProjectはIntegrationServer専用に作成しているものです。
このProjectは[AGPL](LICENSE)ライセンスのもと配布または使用できます
詳しい使い方は[こちら](https://github.com/yupix/ssm/wiki) をご覧ください

## 使い方

音声読み上げを使用するにはopen-jtalkが別途必要です。詳しい設定方法は[こちら](https://github.com/yupix/ssm/wiki/%E8%A8%AD%E5%AE%9A%E6%96%B9%E6%B3%95) をご覧ください

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

## APIに関して

APIに関しては[ここ](https://github.com/yupix/ssm/wiki/API%E3%81%AB%E9%96%A2%E3%81%97%E3%81%A6) を閲覧してください


## コマンド一覧

[こちら](https://github.com/yupix/ssm/wiki/%E3%82%B3%E3%83%9E%E3%83%B3%E3%83%89%E4%B8%80%E8%A6%A7) をご覧ください
