import requests
from pprint import pprint
import json
import math
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urlencode
from datetime import datetime
from datetime import timedelta
from data_cgv import data


class BoxOffice(object):
    base_url = 'http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json'
    def __init__(self,api_key):
        self.api_key = api_key

    def get_movies(self):
        target_dt = datetime.now() - timedelta(days=1)
        target_dt_str = target_dt.strftime('%Y%m%d')
        query_url = '{}?key={}&targetDt={}'.format(self.base_url,self.api_key,target_dt_str)
        with urlopen(query_url) as fin:
            return json.loads(fin.read().decode('utf-8'))

    def simplify(self, result):
        return [
            {
                'rank': entry.get('rank'),
                'name': entry.get('movieNm'),
                'code': entry.get('movieCd')
            }
            for entry in result.get('boxOfficeResult').get('dailyBoxOfficeList')
        ]


class LotteCinema(object):
    base_url = 'http://www.lottecinema.co.kr'
    base_url_cinema_data = '{}/LCWS/Cinema/CinemaData.aspx'.format(base_url)
    base_url_movie_list = '{}/LCWS/Ticketing/TicketingData.aspx'.format(base_url)

    def make_payload(self, **kwargs):
        param_list = {'channelType': 'MW', 'osType':'', 'osVersion':'', **kwargs}
        data = {'ParamList': json.dumps(param_list)}
        payload = urlencode(data).encode('utf8')
        return payload

    def byte_to_json(self,fp):
         content = fp.read().decode('utf8')
         return json.loads(content)

    def get_theater_list(self):
         url = self.base_url_cinema_data
         payload = self.make_payload(MethodName='GetCinemaItems')
         with urlopen(url,data = payload) as fin:
             json_content = self.byte_to_json(fin)
             data = json_content.get('Cinemas').get('Items')
             data = list(filter(lambda x:x['DivisionCode']!=2, data))
             return [
                {   
                    'TheaterName': '{} 롯데시네마'.format(entry.get('CinemaNameKR')),
                    'TheaterID': '{}|{}|{}'.format(entry.get('DivisionCode'), entry.get('SortSequence'), entry.get('CinemaID')),
                    'TheaterDCODE': entry.get('DetailDivisionCode'),
                    'Longitude': entry.get('Longitude'),
                    'Latitude': entry.get('Latitude')
                }
                for entry in data
             ]

    def distance(self, x1, x2, y1, y2):
          dx = float(x1) - float(x2)
          dy = float(y1) - float(y2)
          distance = math.sqrt(dx**2 + dy**2)
          return distance

    def filter_nearest_theater(self, theater_list, pos_latitude, pos_longitude, n=3):
          distance_to_theater = []
          for theater in theater_list:
            distance = self.distance(pos_latitude, theater.get('Latitude'), pos_longitude, theater.get('Longitude'))
            distance_to_theater.append((distance, theater))

          return [theater for distance, theater in sorted(distance_to_theater, key=lambda x: x[0])[:n]]

    def get_movie_list(self, theater_id):
          url = self.base_url_movie_list
          target_dt = datetime.now()
          target_dt_str = target_dt.strftime('%Y-%m-%d')
          payload = self.make_payload(MethodName='GetPlaySequence', playDate=target_dt_str, cinemaID=theater_id, representationMovieCode='')
          with urlopen(url, data = payload) as fin:
              json_content = self.byte_to_json(fin)
              movie_id_to_info = {}

              for entry in json_content.get('PlaySeqsHeader', {}).get('Items', []):
                  movie_id_to_info.setdefault(entry.get('MovieCode'), {})['Name'] = entry.get('MovieNameKR')

              for order, entry in enumerate(json_content.get('PlaySeqs').get('Items')):
                  schedules = movie_id_to_info[entry.get('MovieCode')].setdefault('Schedules', [])
                  schedule = {
                      'StartTime': '{}'.format(entry.get('StartTime')),
                      'RemainingSeat': str(int(entry.get('TotalSeatCount')) - int(entry.get('BookingSeatCount')))
                  }
                  schedules.append(schedule)
              return movie_id_to_info

        



#print(c.get_movie_list('1|43|3018'))

#print(c.filter_nearest_theater(c.get_theater_list(), 37.5, 126.844))

#movie_id_to_info = c.get_movie_list('1|3|3027')
#movie_schedules = []
#text = '{}의 상영시간표입니다.\n\n'.format('롯데시네마')
#string = ""

class MegaBox(object):
    base_url = 'https://www.megabox.co.kr/on/oh/ohc/Brch/schedulePage.do'

    def get_theater_list(self):
        url = self.base_url
        target_dt = datetime.now()
        target_dt_str = target_dt.strftime('%Y%m%d')
        code_list = []
        set_list = []
        data_list = []
        parameters = {'masterType':'brch', 'playDe':target_dt_str}
        res = requests.post(url, data = parameters).json()
        dat = res.get('megaMap').get('movieFormList')
        for s in dat:
            code_list.append(str(s['brchNo']))
        set_list = list(set(code_list))

        for i in set_list:
            parameters = {'masterType':'brch', 'brchNo':i, 'brchNo1':i, 'firstAt':'Y'}
            response = requests.post(url, data = parameters).json()
            data = response.get('megaMap').get('brchInfo')
            data_list.append(data)

        return [
            {
                'TheaterName':'{} 메가박스'.format(entry.get('brchNm')),
                'TheaterID': entry.get('brchNo'),
                'Latitude': entry.get('brchLat'),
                'Longitude': entry.get('brchLon')
            }
            for entry in data_list
         ]


    def distance(self,x1,x2,y1,y2):
        dx = float(x1) - float(x2)
        dy = float(y1) - float(y2)
        distance = math.sqrt(dx**2 + dy**2)
        return distance


    def filter_nearest_theater(self, theater_list, pos_latitude, pos_longitude, n=3):
        distance_to_theater = []
        for theater in theater_list:
            distance = self.distance(pos_latitude, theater.get('Latitude'), pos_longitude, theater.get('Longitude'))
            distance_to_theater.append((distance,theater))

        return [theater for distance, theater in sorted(distance_to_theater, key=lambda x: x[0])[:n]]




    def get_movie_list(self, theater_id):
        url = self.base_url
        target_dt = datetime.now()
        target_dt_str = target_dt.strftime('%Y%m%d')
        parameters = {'masterType':'brch', 'brchNo':theater_id, 'brchNo1':theater_id, 'firstAt':'Y', 'playDe':target_dt_str}
        json_content = requests.post(url, data = parameters).json()
        movie_id_to_info = {}

        for entry in json_content.get('megaMap', {}).get('movieFormList', []):
            movie_id_to_info.setdefault(entry.get('movieNo'), {})['Name'] = entry.get('movieNm')

        for order, entry in enumerate(json_content.get('megaMap').get('movieFormList')):
            schedules = movie_id_to_info[entry.get('movieNo')].setdefault('Schedules', [])
            schedule = {
                'StartTime': '{}'.format(entry.get('playStartTime')),
                'RemainingSeat': str(int(entry.get('restSeatCnt')))
            }
            schedules.append(schedule)
        return movie_id_to_info


class CGV(object):

    def get_theater_list(self):
        return data

    def distance(self, x1, x2, y1, y2):
        dx = float(x1) - float(x2)
        dy = float(y1) - float(y2)
        distance = math.sqrt(dx**2 + dy**2)
        return distance


    def filter_nearest_theater(self,theater_list, pos_latitude, pos_longitude, n=3):
        distance_to_theater = []
        for theater in theater_list:
            distance = self.distance(pos_latitude, theater.get('Latitude'), pos_longitude, theater.get('Longitude'))
            distance_to_theater.append((distance,theater))

        return [theater for distance, theater in sorted(distance_to_theater, key = lambda x: x[0])[:n]]

    def get_movie_list(self, area_code, theater_code):
        string = ""
        target_dt = datetime.now()
        target_dt_str = target_dt.strftime('%Y%m%d')

        header = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/83.0.4103.61 Safari/537.36"}
        url = 'http://www.cgv.co.kr/common/showtimes/iframeTheater.aspx?areacode={}&theatercode={}&date={}'.format(area_code,theater_code,target_dt_str)
        r = requests.get(url, headers = header)
        bs = BeautifulSoup(r.content, "lxml")

        movies = bs.select('body > div > div.sect-showtimes > ul > li')

        for movie in movies:
            dict = {}
            title = movie.select('div.col-times > div.info-movie > a > strong')[0].text.strip()
            timetable = movie.select('div.col-times > div.type-hall > div.info-timetable > ul > li')
            string += "============================\n" +  "*" + ' ' + title + "\n\n"+ ' 상영시간' + ' ' + '  빈좌석' + '\n'
            for info in timetable:
                time = info.select_one('em').text
                seat = info.select_one('span').text
                if '잔여좌석' in seat:
                    seat = info.select_one('span').text[4:]
                dict.setdefault(time,seat)
            dict = sorted(dict.items(), key = lambda x: x[0])
            for result in dict:
                string += '  ' + result[0] + ' ' + '     ' + result[1] + '\n'

        return string
            




  		

