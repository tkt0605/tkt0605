---
name: new-post
description: posts/projects, movies, musics, novels, travels 配下に新しいMarkdownポストを対話形式で追加する。「新しい記事を追加」「映画を1本追加して」など、postsへの新規コンテンツ追加を頼まれたら使う。
---

# new-post

`posts/<folder>/` 配下に新しいMarkdownファイルを、エディタを開かずに対話形式で追加するスキル。
このプロジェクトはフォルダごとにフロントマターのキーがバラバラ（`auther`誤字や`image`/`img`表記違いなど）なので、
このスキルでは既存ファイルから実際のキー名を確認したうえで、それに揃えて新規ファイルを生成する。

## 実行手順

1. **カテゴリの確認**
   `args` にカテゴリ名（`projects` / `movies` / `musics` / `novels` / `travels`）が渡されていれば使う。
   渡されていなければユーザーに尋ねる（AskUserQuestionで選択肢を出すのが望ましい）。

2. **既存ファイルからフロントマター仕様を確認する**
   `posts/<folder>/*.md` を2〜3件readし、実際に使われているキー名とその表記揺れを確認する。
   以下は参考スキーマだが、必ず最新の実ファイルを優先すること（リネームされている可能性があるため）。

   - **共通**（`src/build.py`が解釈）: `title`（必須）, `summary`(Web検索の結果内容から簡単な作品説明を生成), `image` または `img`, `pin`（真偽値、省略時false）, `order`（整数、省略時0）
   - **movies**: `image`, `auther`（※authorではなく誤字表記が定着している）, `genre`（既存値: `drama_film` / `horror` / `action` / `SF`）, `url`（任意、外部リンク。省略時`url: ""`）
   - **musics**: `image`, `author`（こちらは誤字なし）, `situation`（既存値: `morning` / `up` / `night`）, `url`（任意、外部リンク。省略時`url: ""`）
   - **novels**: `image`, `auther`, `genre`（既存値: `japan` / `abroad` / `SF`）, `url`（任意、外部リンク。省略時`url: ""`）
   - **travels**: `country`, `lat`, `lng`（緯度経度。`country`は他ポストと表記を揃える）
   - **projects**: `img`（imageではなくimg）, `url`, `summary`, `browse`（例: `"Github"`）, `pin`, `order`

   `url`はいずれのカテゴリも任意項目。`movies`/`musics`/`novels`では一覧テンプレートの詳細パネル（ホバー時表示）に「外部リンク」として表示され、`projects`ではリンクラベルに`browse`の値（未設定なら「外部リンク」）を使う。

   `genre`や`situation`のように `templates/posts/<folder>/list.html` 側でラベル分岐している項目は、
   テンプレート内の `{% set genres = [...] %}` / `{% set situations = [...] %}` を確認し、
   そこに定義されている `key` の値（例: `drama_film`, `up`）のいずれかと完全一致させる。
   一覧テンプレートが期待するキーと1文字でも違うと、その項目はリストに出てこないだけでエラーにもならないため要注意。

3. **入力をユーザーに尋ねる**
   カテゴリごとに必要な項目をユーザーに質問する。タイトルは必須、それ以外は「Enterでスキップ可」と伝えてよい。
   `genre`/`situation`のように選択肢が決まっている項目は、自由入力ではなくAskUserQuestionの選択肢として提示する。
   `image`/`img`については、カテゴリが`movies`/`musics`/`novels`の場合はユーザーに尋ねず、手順4でslugを決めた後に`fetch-post-image`スキルへ`title`/`author`/`genre`/`slug`を渡して自動取得する（取得失敗時のみ空のまま進める）。`travels`/`projects`は対象外なので従来どおりユーザーに尋ねる。`summary`は、`fetch-post-image`スキルによって得られた検索結果から作品の要約や紹介、説明を簡単にまとめ、生成する。

4. **ファイル名（slug）を決める**
   タイトルから半角英数のスラッグを生成するか、ユーザーに聞く。
   `posts/<folder>/` 内の既存ファイル名と衝突しないか確認する（衝突したら別名にする）。
   `movies`/`musics`/`novels`の場合は、ここで決まったslugを使って`fetch-post-image`スキルを呼び出し、画像を`public/assets/<asset_folder>/<slug>.png`に取得してから次の手順に進む。

5. **Markdownファイルを書き出す**
   `posts/<folder>/<slug>.md` に、YAMLフロントマター + 本文（任意、空でもよい）を書き込む。
   フロントマターの値が日本語や記号を含む場合はダブルクオートで囲む（既存ファイルの書式に合わせる）。
   `image`/`img`には、`fetch-post-image`で取得できた場合は`/assets/<asset_folder>/<slug>.png`を、取得できなかった場合は空文字を入れる。

6. **ビルドして確認する**
   `uv run src/build.py` を実行し、エラーが出ないこと、`dist/<folder>/index.html` に新しいタイトルが出力されていることを確認する。
   失敗したらフロントマターのキー名や引用符の閉じ忘れを疑う。

## 注意

- このスキルはファイルを新規作成するだけで、既存ポストの編集・削除は行わない。
- `pin: true` にすると一覧の先頭に固定されるため、明示的に頼まれない限り `pin` は省略（false扱い）してよい。
- `projects` のみ `templates/posts/projects/page.html` があるため詳細ページも生成される。他のカテゴリは一覧のみ。
