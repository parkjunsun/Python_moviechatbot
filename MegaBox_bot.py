import telegram
import json
import time
import requests
import urllib.parse
import urllib.request
from movies import BoxOffice
from movies import MegaBox
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN='995708301:AAHcCVDYBib9u8oBqnm7bXfkYXOFIqmRdPE'
CHAT_ID = '1197755619'
welcome_msg = '반가워요.\n\n 저는 요즘 볼만한 영화들을 알려드리고, 현재 계신 곳에서 가까운 MegaBox 영화관들의 상영시간표를 알려드려요.\n\n'\
              "'영화순위' , '근처 상영관 찾기', '예매하기', '길 찾기'를 입력해보세요"
error_msg = '잘 모르겠네요.\n\n'\
            '저는 요즘 볼만한 영화들을 알려드리고, '\
            '현재 계신 곳에서 가까운 영화관들의 상영시간표를 알려드려요.\n\n'\
            "'영화순위' , '근처 상영관 찾기' , '예매하기', '길 찾기'를 입력해보세요."
api_key = '772a77a99609fbe7310a45d116355ee1'
GOOGLE_API = 'AIzaSyBpA-KgsaVfDRbo5LI__ylBv3dUQ68dQkQ'
bot = telegram.Bot(token=TOKEN)
flag = 0

def send_box_office(chat_id):
    box = BoxOffice(api_key)
    movies = box.simplify(box.get_movies())
    rank_message = '\n'.join(['{}. {}'.format(m['rank'], m['name']) for m in movies])
    response = '요즘 볼만한 영화들의 순위입니다\n{}'.format(rank_message)
    send_message(chat_id, response)


def send_search_theater_message(chat_id):
    location_keyboard = telegram.KeyboardButton(text="위치 정보 전송", request_location=True)
    custom_keyboard = [[location_keyboard]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=chat_id, text="현재 계신 위치를 알려주세요", reply_markup=reply_markup)


def send_nearest_theaters(chat_id,latitude,longitude):   
    remove_keyboard = telegram.ReplyKeyboardRemove()
    bot.send_message(chat_id = CHAT_ID, text="현재위치를 확인했습니다.", reply_markup = remove_keyboard) 
    cinema = MegaBox()
    theaters = cinema.get_theater_list()
    nearest_theaters = cinema.filter_nearest_theater(theaters, latitude, longitude)
    send_message(chat_id, '가장 가까운 상영관들입니다.\n' + \
                          '상영 시간표 및 빈좌석수를 확인하세요.\n' + \
                          '*현 시각에 영화상영을 종료한 영화관들은 제시되지 않습니다.*')
    data1 = '{} {}'.format(nearest_theaters[0]['TheaterID'], nearest_theaters[0]['TheaterName'])
    data2 = '{} {}'.format(nearest_theaters[1]['TheaterID'], nearest_theaters[1]['TheaterName'])
    data3 = '{} {}'.format(nearest_theaters[2]['TheaterID'], nearest_theaters[2]['TheaterName'])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=nearest_theaters[0]['TheaterName'], callback_data=data1)],[InlineKeyboardButton(text=nearest_theaters[1]['TheaterName'], callback_data=data2)],[InlineKeyboardButton(text=nearest_theaters[2]['TheaterName'], callback_data=data3)]])
    bot.sendMessage(chat_id,text="choose one",reply_markup=keyboard)

def send_nearest_ticketbox(chat_id, latitude, longitude):
    remove_keyboard = telegram.ReplyKeyboardRemove()
    bot.send_message(chat_id = chat_id, text="현재 위치를 확인했습니다.", reply_markup = remove_keyboard)
    cinema = MegaBox()
    tboxes = cinema.get_theater_list()
    nearest_tboxes = cinema.filter_nearest_theater(tboxes, latitude, longitude)
    send_message(chat_id, '선택한 영화관의 예매 사이트로 이동합니다.\n')

    brchNo1 = nearest_tboxes[0]['TheaterID']
    brchNo2 = nearest_tboxes[1]['TheaterID']
    brchNo3 = nearest_tboxes[2]['TheaterID']

    url1 = 'https://m.megabox.co.kr/booking/theater?brchNo={}'.format(brchNo1)
    url2 = 'https://m.megabox.co.kr/booking/theater?brchNo={}'.format(brchNo2)
    url3 = 'https://m.megabox.co.kr/booking/theater?brchNo={}'.format(brchNo3)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=nearest_tboxes[0]['TheaterName'], url = url1)],[InlineKeyboardButton(text=nearest_tboxes[1]['TheaterName'], url = url2)],[InlineKeyboardButton(text=nearest_tboxes[2]['TheaterName'], url = url3)]])
    bot.sendMessage(chat_id, text="예매할 지역의 영화관을 고르세요", reply_markup=keyboard)


def send_nearest_theaters_location(chat_id, latitude, longitude):
    remove_keyboard = telegram.ReplyKeyboardRemove()
    bot.send_message(chat_id = chat_id, text = "현재위치를 확인했습니다.", reply_markup = remove_keyboard)
    cinema = MegaBox()
    theaters = cinema.get_theater_list()
    nearest_theaters = cinema.filter_nearest_theater(theaters, latitude, longitude)
    send_message(chat_id, '가장 가까운 상영관들 입니다.\n' + \
                          '최단거리 경로를 확인하세요')

    data1 = '{} {} {} {}'.format(nearest_theaters[0]['Latitude'], nearest_theaters[0]['Longitude'], latitude, longitude)
    data2 = '{} {} {} {}'.format(nearest_theaters[1]['Latitude'], nearest_theaters[1]['Longitude'], latitude, longitude)
    data3 = '{} {} {} {}'.format(nearest_theaters[2]['Latitude'], nearest_theaters[2]['Longitude'], latitude, longitude)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=nearest_theaters[0]['TheaterName'], callback_data=data1)],[InlineKeyboardButton(text=nearest_theaters[1]['TheaterName'], callback_data=data2)],[InlineKeyboardButton(text=nearest_theaters[2]['TheaterName'], callback_data=data3)]])

    bot.sendMessage(chat_id, text = "choose one", reply_markup = keyboard)


def send_theater_schedule(chat_id, theater_id, theater_name):
    cinema = MegaBox()
    movie_id_to_info = cinema.get_movie_list(theater_id)
    text = '{} MEGABOX의 상영시간표입니다.\n'.format(theater_name)
    string = ""


    for info in movie_id_to_info.values():
       dict={}
       string += "============================\n" + "*" + ' ' + info['Name'] + "\n\n" + ' 상영시간' + '  ' + '  빈좌석' + '\n'
       for schedule in info['Schedules']:
           dict[schedule['StartTime']] = schedule['RemainingSeat']
       dict = sorted(dict.items(), key = lambda x: x[0] )
       for result in dict:
           string += '  ' + result[0] + ' ' + '       ' + result[1] + "\n"
    
    send_message(chat_id, text= text + '\n' + string)    



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
                string += '(' + str(num) + ')' + ' ' + "\U0001f68c" + "  " + info['transit_details']['line']['name'] + ' ' + info['transit_details']['line']['short_name'] +" >>  " + info['transit_details']['departure_stop']['name'] + " ----> " + info['transit_details']['arrival_stop']['name'] + ' ' +'(' + info['duration']['text'] + ',' + info['distance']['text'] + ')' + '\n'
        num = num + 1

    send_message(chat_id, text = string)

def send_error_message(chat_id, text):
    text = urllib.parse.quote(text)
    query = 'chat_id={}&text={}'.format(chat_id,text)
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
                theater_id = data[0]
                theater_name = data[1]
                send_theater_schedule(chat_id, theater_id, theater_name)
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
