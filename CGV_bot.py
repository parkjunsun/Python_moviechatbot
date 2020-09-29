import telegram
import json
import time
import requests
import urllib.parse
import urllib.request
from datetime import datetime
from datetime import timedelta
from movies import BoxOffice
from movies import CGV
from data_cgv import data
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = '1232910624:AAE6XNGREcnUGi3X6v8mDHnH70Gp1pffRUo'
CHAT_ID = '1197755619'
welcome_msg = '반가워요.\n\n 저는 요즘 볼만한 영화들을 알려드리고, 현재 계신 곳에서 가까운 영화관들의 상영시간표를 알려드려요.\n\n'\
              "'영화순위' , '근처 상영관 찾기', '예매하기', '길 찾기'를 입력해보세요"
error_msg = '잘 모르겠네요.\n\n'\
            '저는 요즘 볼만한 영화들을 알려드리고, '\
            '현재 계신 곳에서 가까운 CGV 영화관들의 상영시간표를 알려드려요.\n\n'\
            "'영화순위' , '근처 상영관 찾기' , '예매하기', '길 찾기'를 입력해보세요."

api_key = '772a77a99609fbe7310a45d116355ee1'
GOOGLE_API = 'AIzaSyBpA-KgsaVfDRbo5LI__ylBv3dUQ68dQkQ'
bot = telegram.Bot(token = TOKEN)
flag = 0

def send_box_office(chat_id):
    box = BoxOffice(api_key)
    movies = box.simplify(box.get_movies())
    rank_message = '\n'.join(['{}. {}'.format(m['rank'], m['name']) for m in movies])
    response = '요즘 볼만한 영화들의 순위입니다\n{}'.format(rank_message)
    send_message(chat_id, response)




def send_search_theater_message(chat_id):
    location_keyboard = telegram.KeyboardButton(text="위치 정보 전송", request_location = True)
    custom_keyboard = [[location_keyboard]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=chat_id, text="현재 계신 위치를 알려주세요", reply_markup = reply_markup)




def send_nearest_theaters(chat_id, latitude, longitude):
    remove_keyboard = telegram.ReplyKeyboardRemove()
    bot.send_message(chat_id = chat_id, text = "현재 위치를 확인했습니다.\n 데이터를 가져오고 있습니다.", reply_markup = remove_keyboard)
    cinema = CGV()
    theaters = cinema.get_theater_list()
    nearest_theaters = cinema.filter_nearest_theater(theaters, latitude, longitude)
    send_message(chat_id, '가장 가까운 상영관들입니다.\n' + \
                          '상영 시간표 및 빈좌석수를 확인하세요')

    data1 = '{} {} {}'.format(nearest_theaters[0]['RegionCode'],nearest_theaters[0]['TheaterCode'],nearest_theaters[0]['TheaterName'])
    data2 = '{} {} {}'.format(nearest_theaters[1]['RegionCode'],nearest_theaters[1]['TheaterCode'],nearest_theaters[1]['TheaterName'])
    data3 = '{} {} {}'.format(nearest_theaters[2]['RegionCode'],nearest_theaters[2]['TheaterCode'],nearest_theaters[2]['TheaterName'])

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=nearest_theaters[0]['TheaterName'], callback_data=data1)],[InlineKeyboardButton(text=nearest_theaters[1]['TheaterName'], callback_data=data2)],[InlineKeyboardButton(text=nearest_theaters[2]['TheaterName'], callback_data=data3)]])
    bot.sendMessage(chat_id,text="choose one",reply_markup=keyboard)


def send_nearest_ticketbox(chat_id, latitude, longitude):
    remove_keyboard = telegram.ReplyKeyboardRemove()
    bot.send_message(chat_id = chat_id, text = "현재 위치를 확인했습니다.\n 데이터를 가져오고 있습니다.", reply_markup = remove_keyboard)
    target_dt = datetime.now()
    target_dt_str = target_dt.strftime('%Y%m%d')
    cinema = CGV()
    tboxes = cinema.get_theater_list()
    nearest_tboxes = cinema.filter_nearest_theater(tboxes, latitude, longitude)
    send_message(chat_id, '선택한 영화관의 예매 사이트로 이동합니다.\n')

    area_code1 = nearest_tboxes[0]['RegionCode']
    area_code2 = nearest_tboxes[1]['RegionCode']
    area_code3 = nearest_tboxes[2]['RegionCode']

    theater_code1 = nearest_tboxes[0]['TheaterCode']
    theater_code2 = nearest_tboxes[1]['TheaterCode']
    theater_code3 = nearest_tboxes[2]['TheaterCode']

    url1 = 'http://m.cgv.co.kr/WebApp/Reservation/Schedule.aspx?tc={}&rc={}&ymd={}'.format(theater_code1, area_code1, target_dt_str)
    url2 = 'http://m.cgv.co.kr/WebApp/Reservation/Schedule.aspx?tc={}&rc={}&ymd={}'.format(theater_code2, area_code2, target_dt_str)
    url3 = 'http://m.cgv.co.kr/WebApp/Reservation/Schedule.aspx?tc={}&rc={}&ymd={}'.format(theater_code2, area_code2, target_dt_str)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=nearest_tboxes[0]['TheaterName'], url = url1)],[InlineKeyboardButton(text=nearest_tboxes[1]['TheaterName'], url = url2)],[InlineKeyboardButton(text=nearest_tboxes[2]['TheaterName'], url = url3)]])
    bot.sendMessage(chat_id, text="예매할 지역의 영화관을 고르세요", reply_markup=keyboard)


def send_nearest_theaters_location(chat_id, latitude, longitude):
    remove_keyboard = telegram.ReplyKeyboardRemove()
    bot.send_message(chat_id = chat_id, text = "현재위치를 확인했습니다.\n 데이터를 가져오고 있습니다.", reply_markup = remove_keyboard)
    cinema = CGV()
    theaters = cinema.get_theater_list()
    nearest_theaters = cinema.filter_nearest_theater(theaters, latitude, longitude)
    send_message(chat_id, '가장 가까운 상영관들입니다.\n' + \
                          '최단거리 경로를 확인하세요')

    data1 = '{} {} {} {}'.format(nearest_theaters[0]['Latitude'], nearest_theaters[0]['Longitude'], latitude, longitude)
    data2 = '{} {} {} {}'.format(nearest_theaters[1]['Latitude'], nearest_theaters[1]['Longitude'], latitude, longitude)
    data3 = '{} {} {} {}'.format(nearest_theaters[2]['Latitude'], nearest_theaters[2]['Longitude'], latitude, longitude)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=nearest_theaters[0]['TheaterName'], callback_data=data1)],[InlineKeyboardButton(text=nearest_theaters[1]['TheaterName'], callback_data=data2)],[InlineKeyboardButton(text=nearest_theaters[2]['TheaterName'], callback_data=data3)]])
    bot.sendMessage(chat_id, text = "choose one", reply_markup = keyboard)





def send_theater_schedule(chat_id, area_code, theater_code, theater_name):
    cinema = CGV()
    data = cinema.get_movie_list(area_code,theater_code)
    text = '{}의 상영시간표 입니다.\n'.format(theater_name)

    send_message(chat_id, text = text + '\n' + data)


def send_location_steps(chat_id, des_lat, des_lon, src_lat, src_lon):
    
    string = ""
    num = 1
    mode = 'transit'
    departure_time = 'now'
    lang = 'ko'

    url = 'https://maps.googleapis.com/maps/api/directions/json?origin={},{}&destination={},{}&mode={}&departure_time={}&language={}&key={}'.format(src_lat,src_lon,des_lat,des_lon,mode,departure_time,lang,GOOGLE_API)
    response = requests.get(url).json()
    path = response['routes'][0]['legs'][0]

    duration_time = path['duration']['text']
    departure_time = path['departure_time']['text']
    arrival_time = path['arrival_time']['text']
    stepList = path['steps']

    string += "출발: 현위치\n" + \
              "도착: 선택한 영화관\n" + \
              "예상소요시간: " + departure_time + ' ' + '~' + ' ' + arrival_time + '(' + duration_time + ')' + '\n' + \
              "최단시간 경로: "


    for info in stepList:
        if info['travel_mode'] == 'WALKING':
            string += "\U0001f6b6" + " >" + " "
        elif info['travel_mode'] == 'TRANSIT':
            if info['transit_details']['line']['vehicle']['type'] == 'SUBWAY':
                string += "\U0001f689" + "  " + info['transit_details']['line']['short_name'] + " >" + " "
            elif info['transit_details']['line']['vehicle']['type'] == 'BUS':
                string += "\U0001f68c" + "  " + info['transit_details']['line']['short_name'] + " >" + " "
    string += "\U0001f6a9" + " 도착\n" + \
              "============================\n" + \
              "============================\n" + \
              "세부경로\n"
                

    for info in stepList:
        if info['travel_mode'] == 'WALKING':
            if info['distance']['text'] == '1 m':
                string += '(' + str(num) + ')' + ' ' +  "\U0001f6b6" +"  >>  " + info['html_instructions'] + " " +'(환승)\n'
            else:
                string += '(' + str(num) + ')' + ' ' +  "\U0001f6b6" +"  >>  " + info['html_instructions'] + " " +'(' + info['duration']['text'] + ',' + info['distance']['text'] + ')' + '\n'
        else:
            if info['transit_details']['line']['vehicle']['type'] == 'SUBWAY':
                string += '(' + str(num) + ')' + ' ' + "\U0001f689" + "  " + info['transit_details']['line']['name'] + ' ' + info['transit_details']['line']['short_name'] +" >>  " + info['transit_details']['departure_stop']['name'] + " ----> " + info['transit_details']['arrival_stop']['name'] + ' ' +'(' + info['duration']['text'] + ',' + info['distance']['text'] + ')' + '\n'
            elif info['transit_details']['line']['vehicle']['type'] == 'BUS':
                string += '(' + str(num) + ')' +  ' ' + "\U0001f68c" + "  " + info['transit_details']['line']['name'] + ' ' + info['transit_details']['line']['short_name'] +" >>  " + info['transit_details']['departure_stop']['name'] + " ----> " + info['transit_details']['arrival_stop']['name'] + ' ' +'(' + info['duration']['text'] + ',' + info['distance']['text'] + ')' + '\n'
        num = num + 1

    send_message(chat_id, text = string)
 
def send_error_message(chat_id, text):
    text = urllib.parse.quote(text)
    query = 'chat_id={}&text={}'.format(chat_id, text)
    response = request_to_chatbot_api(method='sendMessage', query = query)
    return response




def request(url):
    response = urllib.request.urlopen(url)
    byte_data = response.read()
    text_data = byte_data.decode()
    return text_data

def build_url(method, query):
    return 'https://api.telegram.org/bot{}/{}?{}'.format(TOKEN,method,query)

def request_to_chatbot_api(method, query):
    url = build_url(method, query)
    response = request(url)
    return json.loads(response)

def simplify_messages(response):
    result = response['result']
    if not result:
        return None, []
    last_update_id = max(item['update_id'] for item in result)
    if result[0].get('message'):
        messages = [item['message'] for item in result]
    elif result[0].get('callback_query'):
        messages = [item['callback_query'] for item in result]
    return last_update_id, messages

def get_updates(update_id):
    query = 'offset={}'.format(update_id)
    response = request_to_chatbot_api(method='getUpdates', query=query)
    return simplify_messages(response)

def send_welcome_message(chat_id, text):
    text = urllib.parse.quote(text)
    query = 'chat_id={}&text={}'.format(chat_id,text)
    response = request_to_chatbot_api(method='sendMessage', query=query)
    return response


def check_messages_and_response(next_update_id):
    global flag
    last_update_id, recieved_messages = get_updates(next_update_id)
    for message in recieved_messages:
        chat_id = message['from']['id']
        if 'text' in message:
            text = message['text']
            if text == '영화순위':
                send_box_office(chat_id)
            elif text == '근처 상영관 찾기':
                flag = 0
                send_search_theater_message(chat_id)
            elif text == '예매하기':
                flag = 1
                send_search_theater_message(chat_id)
            elif text == '길 찾기':
                flag = 2
                send_search_theater_message(chat_id)
            else:
                send_error_message(chat_id, error_msg)
        elif 'location' in message:
            latitude = float(message['location']['latitude'])
            longitude = float(message['location']['longitude'])
            if flag == 0:
                send_nearest_theaters(chat_id,latitude,longitude)
            elif flag == 1:
                send_nearest_ticketbox(chat_id, latitude, longitude)
            else:
                send_nearest_theaters_location(chat_id, latitude, longitude)
        elif 'data' in message:
            if flag == 0:
                data = message['data'].split(' ')
                area_code = data[0]
                theater_code = data[1]
                theater_name = data[2]
                send_theater_schedule(chat_id, area_code, theater_code, theater_name)
            else:
                data = message['data'].split(' ')
                theater_lat = data[0]
                theater_lon = data[1]
                my_lat = data[2]
                my_lon = data[3]
                send_location_steps(chat_id, theater_lat, theater_lon, my_lat, my_lon)
               
    return last_update_id    
	
                      

def send_message(chat_id, text):
    text = urllib.parse.quote(text)
    query = 'chat_id={}&text={}'.format(chat_id,text)
    response = request_to_chatbot_api(method='sendMessage', query=query)
    return response



if __name__ == '__main__':
    reply_markup = telegram.ReplyKeyboardRemove()
    bot.send_message(chat_id = CHAT_ID, text="안녕하세요", reply_markup = reply_markup)
    send_welcome_message(CHAT_ID, welcome_msg)
    next_update_id = 0
    while True:
        last_update_id = check_messages_and_response(next_update_id)
        if last_update_id:
            next_update_id = last_update_id + 1
        time.sleep(5)
                  
