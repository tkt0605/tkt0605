# CLAUDE.md

このファイルは、このリポジトリでコードを扱う際にClaude Code (claude.ai/code) へ向けたガイダンスを提供する。

## プロジェクト概要

MarkdownのポストとJinja2テンプレートから生成される個人サイト（tkt0605.me）の静的サイト。開発時はFlaskで配信する。Pythonの依存関係は`uv`、JS/CSSのツールチェインは`pnpm`で管理する。

## コマンド

- `pnpm dev` — Tailwindのwatch、HTML/MDのwatch（変更時に`src/build.py`で再ビルド）、Flask開発サーバーをまとめて起動する（ポート8000）。
- `pnpm build` — 本番用の一括ビルド。Tailwindで`src/index.css`をコンパイルした後、`uv run src/build.py`を実行して`dist/`を生成する。
- `pnpm preview` — ビルド済みの`dist/`を自動リロードなしでFlaskから配信する（ポート8000）。
- `uv run src/build.py [--output dist] [--no-clean]` — 静的サイトジェネレーターを直接実行する。`--no-clean`を付けると出力先ディレクトリの事前クリアをスキップする（通常は`index.css`を除いて出力先が毎回クリアされる。`index.css`はTailwindが管理するため対象外）。
- `uv run flask --app src/dev-server.py run --debug -p 8000` — 現在の`dist/`に対してFlaskの静的ファイルサーバーのみを起動する。

テストスイートやリンターは設定されていない（`pnpm test`はスタブ）。Prettier（`.html`用の`prettier-plugin-jinja-template`を含む）は依存関係として存在するが、実行用のスクリプトは用意されていない。

## アーキテクチャ

サイトは`src/build.py`という単体スクリプト（アプリケーションフレームワークなし）によってビルドされ、以下を行う。

1. **`posts/`配下のフォルダを自動検出する**（`movies`、`musics`、`novels`、`projects`、`travels`の各サブフォルダがコンテンツコレクションになる）。登録作業は不要で、`posts/`配下に`.md`ファイルを含む新しいフォルダと対応する`templates/posts/<folder>/list.html`を用意するだけで新しいコレクションになる。
2. **各ポストをYAMLフロントマター付きのMarkdownファイルとして読み込む**（`python-frontmatter` + `mistune`を使用）。認識されるフロントマターのキーは`title`、`summary`、`image`/`img`、`pin`（真偽値、デフォルト`false`）、`order`（整数、デフォルト`0`）。ポストはピン留め優先、その後`order`順にソートされる。
3. **個別ポストの詳細ページは`templates/posts/<folder>/page.html`が存在する場合のみレンダリングする**（例：`projects`には存在するが他のコレクションにはなく、それらは一覧のみとなる）。
4. **コレクションの一覧は`templates/posts/<folder>/list.html`でレンダリングし**、共通の`templates/posts/list_page.html`シェルに埋め込まれる。
5. **ホームページ（`templates/index.html`）は全コレクションの一覧と3つの単体コンテンツファイルを組み合わせてレンダリングする**：`content/information/whoami.md`、`content/mylist/hobby.md`、`content/experience/experience.md`（同じくMarkdown+フロントマターとして読み込まれるが、「ポスト」としては扱われない）。
6. **レンダリングされた各ページをBeautifulSoupで後処理する**。`<img>`タグに`decoding="async"`/`loading="lazy"`を付与し、`og_tags()`で生成したOpen Graph用の`<meta>`タグを挿入する。
7. 出力先は`dist/<folder>/<slug>.html`、`dist/<folder>/index.html`、`dist/index.html`。

テンプレート（`templates/`）はいずれも`templates/base.html`を継承しており、共通のヘッダー/ナビ/フッターを定義し、`/index.css`を読み込む（このCSSはTailwind CLIが生成して`dist/`配下にコミットされたものであり、`build.py`が生成するものではない）。

`src/dev-server.py`はキャッチオールルートを持つ最小限のFlaskアプリで、`dist/`内のファイルを優先して配信（`<path>`→`<path>.html`の順で試行）し、見つからない場合は`public/`（長期キャッシュ対象の静的アセット）にフォールバックする。実際のページ生成は常に`build.py`が担い、Flask側では行わない。

サイト全体の定数（著者名、ドメイン）は設定ファイルではなく`src/build.py`の冒頭にハードコードされている。
