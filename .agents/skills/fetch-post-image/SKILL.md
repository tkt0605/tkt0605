---
name: fetch-post-image
description: タイトル・著者・ジャンルから書影/ポスター/ジャケット画像をWeb検索して見つけ、public/assets/<folder>配下にPNGとしてダウンロードする。movies/musics/novelsの新規ポストでimageフィールドを手入力したくないときに使う。new-postスキルから画像入力ステップの代わりに呼ばれることが多い。
---

# fetch-post-image

`title` / `author` / `genre` を使って、その作品の代表画像（書影・映画ポスター・アルバムジャケット）をWeb検索で見つけ、
`public/assets/<asset_folder>/<slug>.png` にダウンロードするスキル。
`new-post`スキルでimageを毎回手入力する手間を省くために使う。

対応カテゴリは `movies` / `musics` / `novels` のみ（`travels`は緯度経度中心、`projects`はスクリーンショット等で自動取得に向かないため対象外）。

## 引数

呼び出し側（new-postなど）から以下を受け取る。渡されなければユーザーに確認する。

- `category`: `movies` / `musics` / `novels` のいずれか
- `title`: 作品タイトル（必須）
- `author`: 著者・監督・アーティスト名（任意だが検索精度向上のため強く推奨）
- `genre`: ジャンル（検索クエリ補助のみ、必須ではない）
- `slug`: 保存ファイル名に使うスラッグ（呼び出し側で決めたものをそのまま使う。なければtitleから生成）

## 実行手順

1. **asset_folderへの変換**
   `category` を保存先サブフォルダ名に変換する（ポスト側のフォルダ名と微妙に異なるので注意）。
   - `movies` → `movie`
   - `musics` → `music`
   - `novels` → `novel`
   保存先: `public/assets/<asset_folder>/<slug>.png`

2. **検索クエリを組み立てる**
   - movies: `"{title}" "{author}" 映画 ポスター`
   - musics: `"{title}" "{author}" アルバム ジャケット`
   - novels: `"{title}" "{author}" 表紙`
   `author`が無ければtitleのみで検索する。

3. **WebSearchで検索する**
   結果の中から、まず日本語版Wikipedia（`ja.wikipedia.org`）の記事を優先的に探す。
   Wikipediaの記事は表紙画像・ポスター画像・ジャケット画像がinfoboxに構造化されて入っていることが多く、
   出典・ライセンスも比較的明確なため最有力候補とする。
   見つからなければ、検索結果の他の上位ページ（出版社/レーベル/公式サイトなど）を候補にする。

4. **画像の直接URLを取得する**
   候補ページをWebFetchで取得し、「この記事のメイン画像（表紙/ポスター/ジャケット）の直接画像URL（.jpg/.png/.webpなど）を1つだけ返して」と指示して抽出する。
   WebFetchがURLを返せない場合は、og:image相当のメタ情報を聞き出す。
   どうしても直接URLが取れない場合はそのページは諦め、次の候補へ進む。候補が尽きたらユーザーに「画像が見つからなかった」と報告し、imageフィールドは空のまま進める。
   また、同じWebFetch呼び出しで「この記事の冒頭（リード文）をもとに作品の概要を1〜2文で要約して」とも指示し、summary_hintとして保持する。

5. **画像をダウンロードする**
   ```
   curl -sL "<image_url>" -o /tmp/fetch-post-image/<slug>.<ext>
   ```
   ダウンロード後、`file /tmp/fetch-post-image/<slug>.<ext>` で実際に画像ファイル（JPEG/PNG/WebP等）であることを確認する。
   HTMLやエラーページが落ちてきていないか（サイズが極端に小さい、`file`の出力がHTMLになっている等）を必ずチェックする。

6. **PNGに変換して配置する**
   macOSの`sips`コマンドで変換する。
   ```
   sips -s format png /tmp/fetch-post-image/<slug>.<ext> --out public/assets/<asset_folder>/<slug>.png
   ```
   変換後、`public/assets/<asset_folder>/<slug>.png` が存在し、サイズが0バイトでないことを確認する。
   一時ファイルは削除してよい。

7. **呼び出し元に結果を返す**
   フロントマターに書く値は `/assets/<asset_folder>/<slug>.png`（先頭スラッシュ、`public/`は含めない）。
   取得に失敗した場合はその旨を伝え、`image`/`img`フィールドは空文字のまま進めてよいと伝える。
   画像探索時に見つけた紹介文・概要（Wikipediaのリード文など）があれば、summary_hintとして呼び出し元に一緒に返す。

## 注意

- ダウンロードする画像は著作物（書影・ポスター・ジャケット）であり、個人の非商用ブログ上での紹介目的の引用として使うことを前提とする。商用利用や無断の二次配布はしないこと。
- 同名ファイルが既に存在する場合は上書きせず、呼び出し元に確認する。
- ジャンルが複数解釈できるなど検索クエリが曖昧な場合は、ヒット数が最も多い/Wikipediaがある候補を優先し、迷ったらユーザーに確認する。
