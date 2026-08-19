---
name: fetch-new-country
description: 国名から国旗画像をWeb検索で見つけ、public/assets/travel/flag/配下にPNGとしてダウンロードする。travels/の新規ポストでflagフィールドを手入力したくないときに使う。new-travelスキルから国旗取得ステップとして呼ばれることが多い。
---

# fetch-new-country

`country`（国名）を使って、その国の国旗画像をWeb検索で見つけ、
`public/assets/travel/flag/<slug>.png` にダウンロードするスキル。
`new-travel`スキルでflagを毎回手入力する手間を省くために使う。

対応カテゴリは `travels` のみ。

## 引数

呼び出し側（new-travelなど）から以下を受け取る。渡されなければユーザーに確認する。

- `country`: 国名（必須、例: `Thailand` / `タイ`。表記はpostsのcountryフィールドに揃える）
- `slug`: 保存ファイル名に使うスラッグ（呼び出し側で決めたものをそのまま使う。なければ`country`から生成）
  - 生成ルール: 英数字以外を除去し、すべて小文字化する（例: `U.S.A` → `usa`、`Thailand` → `thailand`）
  - 既に`public/assets/travel/flag/<slug>.png`が存在する場合は、同じ国の再取得とみなし上書きせずそのまま使ってよい（呼び出し元に再ダウンロード不要と伝える）

## 実行手順

1. **検索クエリを組み立てる**
   `"{country}" 国旗` で検索する（countryが日本語表記でなければ英語名でも検索を試す）。

2. **WebSearchで検索する**
   結果の中から、まず日本語版または英語版Wikipediaの国の記事（例: `ja.wikipedia.org/wiki/タイ`）を優先的に探す。
   Wikipediaの国記事はinfoboxに国旗画像が構造化されて入っていることがほとんどで、出典・ライセンスも明確なため最有力候補とする。
   見つからなければ、検索結果の他の上位ページ（外務省サイトや旗一覧サイトなど）を候補にする。

3. **画像の直接URLを取得する**
   候補ページをWebFetchで取得し、「この記事のinfoboxにある国旗画像の直接画像URL（.svg/.jpg/.png等）を1つだけ返して」と指示して抽出する。
   `.svg`の場合はラスター変換が必要になるため、可能であれば`.png`/`.jpg`版（サムネイルURLなど）を優先的に探す。
   WebFetchがURLを返せない場合は、og:image相当のメタ情報を聞き出す。
   どうしても直接URLが取れない場合はそのページは諦め、次の候補へ進む。候補が尽きたらユーザーに「国旗が見つからなかった」と報告し、flagフィールドは空のまま進める。

4. **画像をダウンロードする**
   ```
   curl -sL "<image_url>" -o /tmp/fetch-new-country/<slug>.<ext>
   ```
   ダウンロード後、`file /tmp/fetch-new-country/<slug>.<ext>` で実際に画像ファイルであることを確認する。
   HTMLやエラーページが落ちてきていないか（サイズが極端に小さい、`file`の出力がHTMLになっている等）を必ずチェックする。

5. **PNGに変換して配置する**
   macOSの`sips`コマンドで変換する（`.svg`はsipsで直接変換できないため、`.svg`しか取得できなかった場合は手順3に戻って別候補を探す）。
   ```
   sips -s format png /tmp/fetch-new-country/<slug>.<ext> --out public/assets/travel/flag/<slug>.png
   ```
   変換後、`public/assets/travel/flag/<slug>.png` が存在し、サイズが0バイトでないことを確認する。
   一時ファイルは削除してよい。

6. **呼び出し元に結果を返す**
   フロントマターに書く値は `/assets/travel/flag/<slug>.png`（先頭スラッシュ、`public/`は含めない）。
   取得に失敗した場合はその旨を伝え、`flag`フィールドは空文字のまま進めてよいと伝える。

## 注意

- ダウンロードする国旗画像は各国の公的な意匠であり、個人の非商用ブログ上での紹介目的の使用を前提とする。商用利用や無断の二次配布はしないこと。
- 同名ファイルが既に存在する場合は上書きせず、呼び出し元に確認する。
- 国名の表記揺れ（通称/正式名称、日本語/英語）で候補が見つからない場合は、もう一方の表記でも検索を試す。
