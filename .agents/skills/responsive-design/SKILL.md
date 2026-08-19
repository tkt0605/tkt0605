---
name: responsive-design
description: プロジェクト全体（templates/とsrc/index.css）のレスポンシブデザインを点検し、モバイル〜デスクトップで崩れる箇所を修正・最適化する。「レスポンシブ対応して」「スマホで見たときのレイアウトを直して」など、画面幅に応じた表示崩れの調整を頼まれたら使う。
---

# responsive-design

`templates/` のJinja2テンプレート（Tailwind CSS）と`src/index.css`（カスタムCSS）を対象に、
画面幅が変わったときの崩れ（横スクロール強制、要素の重なり、文字や画像の極端な縮小など）を見つけて直すスキル。

## 前提（現状の傾向）

- `templates/base.html`には`viewport`メタタグが設定済みで、Tailwind自体はモバイルファースト（`sm:`=640px, `md:`=768px, `lg:`=1024px, `xl:`=1280px、`src/index.css`の`@import "tailwindcss"`に準拠）。
- ただし`src/index.css`側のカスタムクラス（`.novels-stage`, `.musics-stage`, `.travel-stage`等の`*-stage`系コンポーネントや、`hobby-detail`系、各種`*-card`系）には固定px幅・`min-width: 520px`のような値が多く、レスポンシブ対応が後回しになっている箇所が多い。
- `templates/index.html`など一部のテンプレートはTailwindの`sm:`/`md:`を使っているが、全体に一貫して適用されているわけではない。

## 実行手順

1. **対象範囲を確認する**
   ユーザーから特定のページ/コンポーネントが指定されていればそこに絞る。指定がなければ`templates/`配下と`src/index.css`全体を対象にする。

2. **崩れ箇所を洗い出す**
   - `src/index.css`で`width:`/`min-width:`に固定px値が入っている箇所をgrepし、それがビューポートより大きくなりうるか（=横スクロールや要素の食い込みを引き起こすか）を判断する。
   - 該当テンプレートをWebFetchではなくRead/Grepで確認し、Tailwindのレスポンシブ修飾子（`sm:`/`md:`/`lg:`）が使われているか、使われるべきなのに省略されていないかを確認する。
   - 特に横並びのカード一覧（`*-stage`系）、地球儀（`.travel-stage`/`.globe-canvas`）、`hobby-detail`系の詳細パネルは画面幅に応じてレイアウトが変わるべき箇所なので優先的に確認する。

3. **モバイルファーストで修正する**
   - カスタムCSSはモバイル向け（小さい画面）の値をベースとして書き、`@media (min-width: 640px)`以降でデスクトップ向けに拡張する既存パターン（`src/index.css`の`.globe-canvas`の書き方）に合わせる。
   - 固定`min-width`で横スクロールを強制している箇所は、`min-width`を撤廃するか、`max-width: 100%`や`overflow-x: auto`との組み合わせに置き換えるか、グリッド/フレックスを`flex-wrap`させるなど、画面幅に追従する形に変更する。
   - Tailwindで書けるテンプレート側のレイアウト調整（カラム数、padding、文字サイズなど）は、既存の`sm:`/`md:`/`lg:`の使い方に揃えて追記する。
   - CSS変数や`clamp()`を使った可変サイズも、既存スタイル（`width: min(76vw, 540px)`のパターン）に合わせて活用してよい。

4. **ビルドして確認する**
   `pnpm build`（Tailwindのコンパイル＋`uv run src/build.py`）またはタスクに応じて`tailwindcss -i ./src/index.css -o ./dist/index.css`を実行し、`pnpm preview`またはdev serverで実際にブラウザを開いて確認する。
   複数の画面幅（モバイル幅375px程度、タブレット幅768px程度、デスクトップ幅1280px程度）でレイアウトが崩れないか、横スクロールが意図せず発生していないかを必ず目視確認する。CSSの変更だけで「直ったはず」と判断せず、実際にブラウザで確認すること。

## 注意

- `src/index.css`の先頭3行（`@tailwind base/components/utilities`）と`@import "tailwindcss"`はビルド設定そのものなので変更しない。
- `dist/index.css`はTailwind CLIが生成する出力であり`build.py`はクリーンしない対象だが、直接編集してはならない（`src/index.css`を編集してビルドし直す）。
- 既存の配色・余白・フォントサイズなどのデザイン意図は変えず、あくまで画面幅に応じた崩れの解消・最適化に留める。デザインの大幅な変更が必要そうな場合はユーザーに確認する。
