---
name: new-travel
description: posts/travels配下に新しいMarkdownポストを対話形式で追加する。「旅行を1件追加して」「〇〇に行った記録を追加」など、travelsへの新規コンテンツ追加を頼まれたら使う。movies/musics/novels用のnew-postとは別物（travels専用）。
---

# new-travel

`posts/travels/` 配下に新しいMarkdownファイルを、エディタを開かずに対話形式で追加するスキル。
`new-post`スキルの対象（`projects`/`movies`/`musics`/`novels`）には`travels`を含めない。`travels`はlat/lng・国旗・自撮り画像など専用の項目を持つため、本スキルで個別に扱う。

## フロントマター仕様

既存ファイル（`posts/travels/san_francisco.md`、`posts/travels/travels.md`）を参照。必ず最新の実ファイルを優先すること。

- `title`（必須）: 訪れた都市・地名
- `summary`（任意）: 一言の感想・紹介文。省略可（空文字でよい）
- `country`（必須）: 国名。既存ポストの表記揺れ（`U.S.A`、`Japan`など）に合わせる
- `lat` / `lng`（必須）: 都市の緯度経度。数値（小数）
- `kind`（任意）: `visited`（デフォルト）または`wishlist`。省略時は`visited`扱い
- `flag`（任意）: 国旗画像パス。`fetch-new-country`スキルで自動取得する
- `image`（任意）: 自撮り画像パス。`public/assets/travel/me/<slug>.png`にユーザー自身が保存したファイルを指す。本スキルでは取得・生成せず、ユーザーに配置済みかどうかを確認するのみ
- `url`（任意）: 旅行に関する外部リンク（自分のブログ記事など）。省略時は空文字（`url: ""`）。`templates/posts/travels/list.html`の詳細パネルに「外部リンク」として表示される

## 実行手順

1. **入力をユーザーに尋ねる**
   - タイトル（都市・地名、必須）
   - 国名（必須）
   - 緯度経度（必須）。ユーザーが分からない場合はWebSearchで`"{title}" 緯度 経度`を検索して調べてよいが、必ずユーザーに確認した値を使う
   - summary（任意）。AskUserQuestionで「自分で書く／省略する」を選ばせるのが望ましい。省略時は空文字
   - kind（任意）。聞かれなければ`visited`扱いとし、わざわざ尋ねない（wishlist投稿を明示的に頼まれた場合のみ尋ねる）
   - url（任意）。外部リンク（ブログ記事など）があれば尋ねる。「Enterでスキップ可」と伝えてよい。省略時は空文字

2. **ファイル名（slug）を決める**
   タイトルから半角英数のスラッグを生成する（例: `San Francisco` → `san_francisco`）。
   `posts/travels/` 内の既存ファイル名と衝突しないか確認する（衝突したら別名にする）。

3. **国旗を取得する**
   `fetch-new-country`スキルに`country`（と国名から導出した国旗用slug）を渡して呼び出し、`public/assets/travel/flag/<slug>.png`を取得する。
   取得できた場合は`flag: /assets/travel/flag/<slug>.png`を、できなかった場合は`flag`を空文字または省略にする。

4. **自撮り画像の確認**
   ユーザーに「`public/assets/travel/me/<slug>.png`に自撮り画像を配置済みか」を尋ねる。
   - 配置済みと回答された場合: `ls public/assets/travel/me/`で実在を確認し、存在すれば`image: /assets/travel/me/<slug>.png`を設定する
   - 未配置・スキップの場合: `image`は空文字のまま進める（このスキルが画像を検索・生成することはない）

5. **Markdownファイルを書き出す**
   `posts/travels/<slug>.md` に、YAMLフロントマター + 本文（任意、空でもよい）を書き込む。
   フロントマターの値が日本語や記号を含む場合はダブルクオートで囲む（既存ファイルの書式に合わせる）。
   `summary`は省略された場合`summary: ""`として書く（キー自体は残す。既存ファイルの形式に合わせる）。

6. **ビルドして確認する**
   `uv run src/build.py` を実行し、エラーが出ないこと、`dist/travels/index.html`に新しい国名・タイトルが反映されていることを確認する。
   失敗したらフロントマターのキー名や引用符の閉じ忘れ、lat/lngが数値になっているかを疑う。

## 注意

- このスキルはファイルを新規作成するだけで、既存ポストの編集・削除は行わない。
- `flag`/`image`は現状`templates/posts/travels/list.html`側で未配線（`flag`は参照なし、`image`はコメントアウトされた詳細表示にのみ対応）。表示に反映したい場合はテンプレート側の対応が別途必要になることをユーザーに伝える。
- `kind: wishlist`は地球儀上に赤いピンとして表示され、`visited`は緑のチェックマークとして表示される（`templates/posts/travels/list.html`参照）。
