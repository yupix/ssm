# SSM Project

![ssm](https://repo.akarinext.org/assets/image/YX.png)

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
