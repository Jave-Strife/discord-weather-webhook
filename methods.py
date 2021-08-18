import html
import io
import json
import os
import time
import urllib.request
import plotly.graph_objects as go
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from config import OWM

BG_COLOR = '#2F3136'
FRAME_COLOR = '#C08000'
FONT_FAMILY = 'IPAexGothic'
FONT_COLOR = '#FFFFFF'
FONT_PATH = 'ipaexg00401/ipaexg.ttf'

# 緯度経度から天気データを取得するメソッド
def get_owm_data( lat, lon ):
    # 送信するクエリパラメータを生成
    params = {
        'lang': 'ja',
        'units': 'metric',
        'exclude': 'minutely,alerts',
        'lat': lat,
        'lon': lon,
        'appid': OWM['APPID']
    }
    scheme = 'utf-8'

    # URLを指定
    url = f'{OWM["URL"]}?{urllib.parse.urlencode( params )}'

    try:
        # 天気データを取得
        res = urllib.request.urlopen( url ).read().decode( scheme )
        wd = json.loads( res )

        # 天気データをローカルに保存
        #with open('test_weather_data.json', 'w', encoding = scheme ) as f:
        #    json.dump( wd, f, indent = 4, ensure_ascii = False )

        # ローカルの天気データを取得
        #with open('test_weather_data.json', 'r', encoding = scheme ) as f:
        #    wd = json.load( f )

    except urllib.error.HTTPError as e:
        wd = OWM['ERROR_JSON']
        print( e.error )
        exit()

    except urllib.error.URLError as e:
        wd = OWM['ERROR_JSON']
        print( e.reason )
        exit()

    else:
        print( f'Weather data acquisition complete. {datetime.now()}')

    finally:
        time.sleep( 1 )
        return wd


# 天気画像を生成するメソッド
def make_embed_image_hourly( wd_hr, pref, city ):
    ''' 表外に出力するデータの取得 '''
    # 日付
    today = convert_date_jp( datetime.now() )

    # 入力した地名
    location = f'{pref}{city}の天気'

    # 著作権表記
    copyright = f'{html.unescape("&copy;")}OpenWeatherMap'

    ''' 表に出力するデータの取得 '''
    # 24時間後までを指定
    flg_24hr = range( round( len( wd_hr ) / 2 ) )

    # 3時間毎のデータを取得
    # 日時
    dt_hr = [
        datetime.fromtimestamp( wd_hr[i]['dt'] ).strftime('%m/%d %H:%M') \
        for i in flg_24hr if i % 3 == 0
    ]

    # 天気アイコン
    icon_hr = [
        get_weather_icon( wd_hr[i]['weather'][0]['icon'] ) \
        for i in flg_24hr if i % 3 == 0
    ]

    # 天候
    desc_hr = [
        wd_hr[i]['weather'][0]['description'] \
        for i in flg_24hr if i % 3 == 0
    ]

    # 気温(℃)
    temp_hr = [
        wd_hr[i]['temp'] \
        for i in flg_24hr if i % 3 == 0
    ]

    # 湿度(%)
    humi_hr = [
        wd_hr[i]['humidity'] \
        for i in flg_24hr if i % 3 == 0
    ]

    # 降水確率(%)
    pop_hr = [
        round( wd_hr[i]['pop'] * 100 ) \
        for i in flg_24hr if i % 3 == 0
    ]

    # 気圧(hPa)
    pres_hr = [
        f'{wd_hr[i]["pressure"]:,}' \
        for i in flg_24hr if i % 3 == 0
    ]

    ''' 2次元配列に格納 '''
    # 日時, アイコン(表示用), 天候, 気温, 湿度, 降水確率, 気圧
    cells = [ dt_hr, '', desc_hr, temp_hr, humi_hr, pop_hr, pres_hr ]

    # 表のヘッダーを指定
    header = [
        '<b>日時</b>',
        '<b>アイコン</b>',
        '<b>天候</b>',
        '<b>気温 ℃</b>',
        '<b>湿度 %</b>',
        '<b>降水確率 %</b>',
        '<b>気圧 hPa</b>'
    ]

    # 表のデータを生成
    table_data = go.Table(
        columnwidth = [35, 30, 60, 30, 30, 40, 35],
        header = dict(
            values = header,
            fill_color = BG_COLOR,
            line_color = FRAME_COLOR,
            font = dict(
                family = FONT_FAMILY,
                color = FONT_COLOR,
                size = 15
            ),
            align = 'center'
        ),
        cells = dict(
            values = cells,
            fill_color = BG_COLOR,
            line_color = FRAME_COLOR,
            font = dict(
                family = FONT_FAMILY,
                color = FONT_COLOR,
                size = 15.25
            )
        )
    )

    # 表のレイアウトを設定
    table_layout = dict(
        paper_bgcolor = BG_COLOR,
        margin = dict(
            l = 30,
            r = 30,
            t = 35,
            b = 0
        ),
        title = dict(
            text = f'{location} {today}現在',
            x = 0.5,
            font = dict(
                family = FONT_FAMILY,
                color = FONT_COLOR
            )
        )
    )

    # 表のデータから画像を生成し、メモリに保持
    fig = go.Figure( data = table_data, layout = table_layout )
    img = fig.to_image( format = 'png', engine = 'kaleido', scale = 1.5 )
    img = Image.open( io.BytesIO( img ) )

    # 著作権表記を追記
    draw = ImageDraw.Draw( img )
    draw.text(
        ( img.size[0] - 195, img.size[1] - 25 ),
        copyright,
        fill = FONT_COLOR,
        font = ImageFont.truetype( FONT_PATH, size = 20 )
    )

    # 天気アイコンを貼り付ける為の透過画像を生成
    img_clear = Image.new('RGBA', img.size, ( 255, 255, 255, 0 ) )

    # 天気アイコンを透過画像に貼り付け
    icon_position_y = 105
    for icon in icon_hr:
        img_clear.paste( icon, ( 196, icon_position_y ) )
        icon_position_y = icon_position_y + 77

    # 透過画像を画像の基に貼り付け
    img = Image.alpha_composite( img, img_clear )

    # 画像をメモリ上に保存
    img_bin = io.BytesIO()
    img.save( img_bin, format = 'png')
    img_bin.seek( 0 )

    return img_bin


# 日付を日本語表記で取得するメソッド
def convert_date_jp( dt ):
    weeks = ['日', '月', '火', '水', '木', '金', '土']
    week_num = int( dt.strftime('%w') )
    return dt.strftime( f'%Y/%m/%d({weeks[week_num]}) %H:%M')


# 天気アイコンを取得するメソッド
def get_weather_icon( icon_id ):
    # 絶対パスの取得
    abs_path = os.path.dirname( __file__ )

    # アイコンのディレクトリを指定
    icon_path = f'{abs_path}/weather_icon'

    # アイコン一覧
    icons = {
        '01d': f'{icon_path}/01d.png',
        '01n': f'{icon_path}/01n.png',
        '02d': f'{icon_path}/02d.png',
        '02n': f'{icon_path}/02n.png',
        '03d': f'{icon_path}/03.png',
        '03n': f'{icon_path}/03.png',
        '04d': f'{icon_path}/04.png',
        '04n': f'{icon_path}/04.png',
        '09d': f'{icon_path}/09.png',
        '09n': f'{icon_path}/09.png',
        '10d': f'{icon_path}/10.png',
        '10n': f'{icon_path}/10.png',
        '11d': f'{icon_path}/11.png',
        '11n': f'{icon_path}/11.png',
        '13d': f'{icon_path}/13.png',
        '13n': f'{icon_path}/13.png',
        '50d': f'{icon_path}/50.png',
        '50n': f'{icon_path}/50.png',
    }

    return Image.open( icons[icon_id] )