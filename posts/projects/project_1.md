---
title: "ThreeBody"
img: assets/projects/2026_07_10_テストDEMO.gif
url: https://threebody-phi.vercel.app/
summary: "1つのAIが答え、最大2つの別のAIがその答えを検算する、音声ファーストのAIチャットアプリ"
browse: "こちらから"
pin: true
order: 1
---

主体（一体目）が回答をストリーミングし、副体（二・三体目）が「崩れる点」「抜けている点」「別の見方」の観点から指摘を1つずつ返す。複数モデルの出力を混ぜて1つの答えを作るのではなく、答えをあとから検算する仕組み。

- Claude / GPT / DeepSeek / Ollama を「体」として自由に組み合わせ可能
- 音声入力・文単位の読み上げ・発話による割り込み（バージイン）に対応
- 検算付きの1ターンを「AIはこう言った → でも、ここが問題 → 次にすること」の共有カードとして書き出せる
- 技術スタック: Vue 3 / TypeScript / Supabase

[GitHub](https://github.com/tkt0605/threebody)
