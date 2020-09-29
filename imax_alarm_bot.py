import requests
import telegram
import time
from datetime import datetime
from datetime import timedelta
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from data_cgv import data

imax_theaters = []
TOKEN = '1139254201:AAEnEm7lLz3SCfxT9IhaHYzG61_40VHXfW0'
CHAT_ID = '1197755619'


bot = telegram.Bot(token = TOKEN)

s = set()

def notice():
    string = ""
    all_imax_theaters = ['CGV천호', 'CGV왕십리', 'CGV용산아이파크몰', 'CGV판교', 'CGV인천', 'CGV일산', 'CGV수원', 'CGV소풍']
    for name in all_imax_theaters:
        string += name+'\n'
    bot.sendMessage(CHAT_ID, text = "수도권내 IMAX상영관 목록입니다.\n" + string)
    bot.sendMessage(CHAT_ID, text = "<<위 영화관들의 IMAX개봉시 알람이 울리게 됩니다.>>\n *챗봇방 오류시 문의: qkrwnstns52@naver.com") 
    





def imax_searching():    
    target_dt = datetime.now()
    target_dt_str = target_dt.strftime('%Y%m%d')
    imax_theaters = ['CGV용산아이파크몰']
    for name in imax_theaters:
        for info in data:
            if info['TheaterName'] == name:
                area_code = info['RegionCode']
                theater_code = info['TheaterCode']
                url = 'http://www.cgv.co.kr/common/showtimes/iframeTheater.aspx?areacode={}&theatercode={}&date={}'.format(area_code, theater_code, target_dt_str)
                r = requests.get(url)
                bs = BeautifulSoup(r.content, "lxml")
                imax = bs.select_one('span.imax')
                if (imax):
                    imax = imax.find_parent('div', class_='col-times')
                    title = imax.select_one('div.info-movie > a > strong').text.strip()
                    return True, name, title, theater_code, area_code, target_dt_str
                else:
                    title = None
                    return False, name, title, theater_code, area_code, target_dt_str
                
                    
        time.sleep(5)


if __name__ == '__main__':
    notice()
    while True:
        bool, name, title, theater_code, area_code, target_dt_str = imax_searching()
        if (bool) and title not in s:
            s.add(title)
            bot.sendMessage(chat_id = CHAT_ID, text = name + '에서 ' + title + ' IMAX예매가 열렸습니다.')
            booking_url = 'http://m.cgv.co.kr/WebApp/Reservation/Schedule.aspx?tc={}&rc={}&ymd={}'.format(theater_code, area_code, target_dt_str)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = name, url = booking_url)]])
            bot.sendMessage(CHAT_ID, text = "바로 예매하러가기", reply_markup = keyboard)
        else:
            continue
            
       time.sleep(30)


