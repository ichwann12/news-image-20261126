# news-image-20261126

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![Rank](https://make.fun/badge/news-image-20261126/ichwann12/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![Reward](https://make.fun/badge/news-image-20261126/ichwann12/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

A program that draws a newspaper front page summing up the world's news of
Thursday 26 November 2026 and writes it to `/output/entry.png`.

The front page leads with India marking 18 years since the 26/11 Mumbai
terror attacks (and Constitution Day), then covers the first foreign
astronaut aboard China's Tiangong station, naval mines hitting two oil
tankers in the Strait of Hormuz, Israel's strike on a Hamas official in
Gaza, the Solomon Islands–Australia security treaty, and 15-year-old
Vaibhav Sooryavanshi's world-record 204 off 53 balls — with an "Also today"
strip for Ukraine, Bangladesh, North Korea, US tariffs and the Mississippi
plane crash.

Run it with:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

It draws the image deterministically with PIL (no network, no clock), so two
runs produce identical bytes.
