# SSM Project

![ssm](https://s3.akarinext.org/misskey/*/29af8bc0-54d3-4ac1-801c-aef2990855cc.png)

## 注意

1. このbranchが`testing`の場合作成途中のものや、そもそも動かないことが多々あるため推奨していません
2. このbranchが`database-testing`の場合はデータベースへの大型変更を行っているため、絶対に使用しないでください。
   2.5 現在テスト中のため、postgresql以外でのサポートは受け付けません。
3. このREADMEの更新は非常に遅れており、コマンドなども一切更新ができていません

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

## APIに関して

APIでは主にリクエストされた情報を元にIDを作成し、そのIDの処理が終わるまで待つ処理が必要です。
理由に関しては最後に記載しますが、Apiにアクセスが返ってきたIDを保存し、そのIDをリクエストのパラメーターに設定し
以下の`result > type`がsuccessfulになるまで定期的にアクセスしてください。successfulになると新たに`body`という項目が増えそこに
詳しい詳細情報が入っています。
```json
{
   "result": {
      "type": "waiting"
   }
}
```

## コマンド一覧

|コマンド名|概要|
|---|---|
|warframe|warframeに関するメインコマンドです。サブコマンドを付与することで使用可能|
