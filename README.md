<h1 align="center">DiscordWeatherWebhook</h1>

# 開発環境(Developed)
* [Python](https://www.python.org) 3.9.6

    ### 使用ライブラリ(Using Library)
    * [Plotly](https://pandas.pydata.org) 5.2.1
    * [Kaleido](https://github.com/plotly/Kaleido)  0.2.1
    * [Pillow](https://www.crummy.com/software/BeautifulSoup/bs4/doc) 8.3.1
    * [discord.py](https://discordpy.readthedocs.io/ja/latest) 1.7.3

# 下準備(Setup)
* [DiscordのWebhookの設定方法(一例)](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)
* config.pyは予め作成しておく
```bash
git clone https://github.com/Jave-Strife/discord-weather-webhook.git
cd discord-weather-webhook
pip install plotly
pip install kaleido
pip install pillow
pip install discord.py
python main.py [都道府県名] [市区町村名]
```

# 使用WebAPI(Using WebAPI)
* [OpenWeatherMap](https://openweathermap.org)