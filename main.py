import sys
import json
import random
import string
import urllib.request
import discord
from datetime import datetime, timedelta, timezone
from methods import get_owm_data, make_embed_image_hourly, convert_date_jp
from config import DISCORD

def main():
    # コマンドライン引数の受付
    args = sys.argv

    # 引数が足りない場合
    if len( args ) == 1:
        print('都道府県名が入力されていません')
        exit()

    # 都道府県データの読み込み
    with open('pref_data.json', 'r', encoding = 'utf-8') as f:
        # 都道府県データの生成
        pref_data = json.load( f )

    # 第1引数(都道府県名)が都道府県データに存在しない場合
    pref = args[1]
    if pref not in pref_data:
        print('入力された都道府県名が見つかりませんでした')
        exit()

    # 都道府県データから市区町村データを取得
    city_data = pref_data[pref]['市区町村']

    # 市区町村名リストを生成
    city_names = [
        city_data[i]['市区町村名_漢字'] \
        for i in range( len( city_data ) )
    ]

    # 引数が足りない場合
    if len( args ) == 2:
        post_city_names_list( city_names )
        exit()

    # 第2引数(市区町村名)が市区町村名リストに存在しない場合
    city = args[2]
    if city not in city_names:
        post_city_names_list( city_names )
        exit()

    # 市区町村名リスト内で何番目のデータかを判定し、index番号を取得
    # (実際には [ 市区町村コード - 1 ] のデータを取得)
    target_city_id = city_names.index( city )

    # indexに基づいた市区町村データを取得
    target_data = city_data[target_city_id]

    # 市区町村データ内の緯度経度から天気データを取得
    wd = get_owm_data( target_data['緯度'], target_data['経度'] )

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


def post_city_names_list( city_names ):
    print('市区町村名が存在しません')
    print('以下の内容から入力してください')
    print( city_names )


# ランダムなファイル名を生成するメソッド
def get_random_str():
    random_str = string.ascii_letters + string.digits + string.ascii_uppercase + string.ascii_lowercase
    return ''.join( [ random.choice( random_str ) for i in range( 16 ) ] )


if __name__ == '__main__':
    main()