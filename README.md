# sixchan
Youtubeで投稿している"【Python】Flaskでつくる5ちゃんねる風掲示板Webアプリ"シリーズのリポジトリです。
- Part1: https://youtu.be/DkOZSxaMV8w

## Quickstart
以下でリポジトリをクローンして、開発サーバを立ち上げることができます。
```bash
git clone -b youtube-part1 https://github.com/suwa808/sixchan.git
cd sixchan
python3 -m venv .venv
pip3 install -r requirements.txt
python3 -c "from sixchan import db; db.create_all()"
python3 -c "from sixchan import insert_mock_reses; insert_mock_reses()"
make dev
```

## Links
- [SuwaCoding](https://www.youtube.com/channel/UCAqqAK9M58yNRPhaMSbmV4Q)