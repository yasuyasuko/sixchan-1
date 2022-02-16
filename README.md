# sixchan
Youtubeで投稿している"【Python】Flaskでつくる5ちゃんねる風掲示板Webアプリ"シリーズのリポジトリです。
- Part1: https://youtu.be/DkOZSxaMV8w
- Part2: https://youtu.be/BO0O8FcQQ6M
- Part3: https://youtu.be/_Jyis3245Ys

## Quickstart
以下でリポジトリをクローンして、開発サーバを立ち上げることができます。
```bash
git clone -b youtube-part3 https://github.com/suwa808/sixchan.git
cd sixchan
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
make up
make createtables
make insertmocks
make dev
```

## Links
- [SuwaCoding](https://www.youtube.com/channel/UCAqqAK9M58yNRPhaMSbmV4Q)