import csv
import os
import random
import string
import discord
from datetime import datetime, timedelta, timezone
from methods import get_owm_data, make_embed_image_hourly, convert_date_jp
from config import DISCORD

def main():
    # 絶対パスの取得
    abs_path = os.path.dirname( __file__ )

    # CSVファイルの読み込み
    with open( f'{abs_path}/pref_data/use_data.csv', 'r', encoding = 'shift-jis') as f:
        reader = csv.DictReader( f )
        locations = [ r for r in reader ]

    # データの数だけループ
    for location in locations:
        # データを指定
        lat = location['緯度']
        lon = location['経度']
        pref = location['都道府県名_漢字']
        city = location['市区町村名_漢字']

        # 市区町村データ内の緯度経度から天気データを取得
        wd = get_owm_data( lat, lon )

        # 天気データから画像を生成
        img = make_embed_image_hourly( wd['hourly'], pref, city )

        # ランダムなファイル名を生成
        f_name = f'{get_random_str()}.png'

        # Discord.pyを用いたWebhookの設定
        webhook_data = DISCORD['Webhook2']
        webhook = discord.Webhook.partial(
            webhook_data['ID'],
            webhook_data['TOKEN'],
            adapter = discord.RequestsWebhookAdapter()
        )

        ''' Embedの生成 '''
        # 初期設定
        embed = discord.Embed(
            # タイトル
            title = f'{pref}{city}の天気',

            # 概要
            description = f'{convert_date_jp( datetime.now() )}現在',

            # 時刻(時差の調整)
            timestamp = datetime.now( timezone( timedelta( hours = 9 ) ) )
        )

        # 画像のセット
        embed.set_image( url = f'attachment://{f_name}')
        send_file = discord.File( fp = img, filename = f_name )

        # フッターのセット
        embed.set_footer(
            text = 'Powered by OpenWeatherMap',
            icon_url = 'https://openweathermap.org/themes/openweathermap/assets/img/logo_white_cropped.png'
        )

        # Discordに投稿
        webhook.send( embed = embed, file = send_file )


# ランダムなファイル名を生成するメソッド
def get_random_str():
    random_str = string.ascii_letters + string.digits + string.ascii_uppercase + string.ascii_lowercase
    return ''.join( [ random.choice( random_str ) for i in range( 16 ) ] )


if __name__ == '__main__':
    main()