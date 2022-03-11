## 🎬 Movie ChatBot
📽 롯데시네마, CGV, 메가박스의 상영관 예매 정보, 영화관 위치, 길찾기 정보를 제공하는 텔레그램 채팅봇 프로그램입니다+IMAX 알람봇

<br><br>

## 🚀 개발개요
* 3사 영화관 모두 들어가서 예매정보를 확인하는게 비효율적이다. 그리고 예매정보가 한눈에 들어오질 않는다. 이를 영화사별 채팅방을 분리 시켜 놓고 채팅으로 정보를 제공 받으면 편리 할 것 같다는 생각에서 만들어 보았다.
* 타 지역에 있을 때 가까운 주변에 있는 영화관들을 찾고 어떻게 찾아갈 수 있는지 알려준다면 좋지 않을까 해서 개발을 진행했다.
* 블록버스터급 영화를 좋아하기 때문에 IMAX에서 보는 것을 선호하는데 예매를 빨리해야 볼 수 있기 때문에 IMAX알람 봇도 개발을 했다.  

<br><br>

## 📺 시연영상
### ✅ 롯데시네마 채팅방입니다. (CGV, 메가박스도 동일합니다)

<img src = "https://user-images.githubusercontent.com/50009692/128194624-49cb8c1e-f250-4c45-9b26-4d7c7f05d235.gif">

<br><br>

## ⚒ 기술스택
* Python
* Python Telegram Bot

<br><br>

## ⛏ Installation & Execution (Ubuntu16.04 기준)
* #### ✅ 라이브러리 설치
```
apt-get install -y python3
apt-get install -y python3-pip
pip3 install requests
pip3 install python-telegram-bot
pip3 install beautifulsoup4
pip3 install lxml
```
* #### ✅ bot_exe.sh 작성 (3사 영화관 봇을 같이 실행하기 위한 쉘 스크립트)　　　　**‼ chmod +x bot_exe.sh 으로 실행권한 주기**
```bash
#!/bin/sh
python3 LotteCinema_bot.py &
python3 MegaBox_bot.py &
python3 CGV_bot.py &   
python3 imax_alarm_bot.py
```
* #### ✅ 실행
```
3사 영화관 채팅 봇 동시 실행 -> ./bot_exe.sh
롯데시네마 단일 실행 ▶ python3 LotteCinema_bot.py
메가박스 단일 실행 ▶ python3 MegaBox.py
CGV 단일 실행 ▶ python3 CGV_bot.py
IMAX 알람 봇 실행 ▶ python3 imax_alarm_bot.py &
```

<br><br>

## ⚙ 환결성정
* #### 사용 API
> 영화 진흥위원회 API (<https://www.kobis.or.kr/kobisopenapi/homepg/main/main.do>)
> 
> GOOGLE DIRECTIONS API (<https://developers.google.com/maps/documentation/directions/overview>)
> 
> Telegram Bot API (<https://core.telegram.org/bots/api>)
* #### Appication.py 　　　　**‼ gitignore사용**
```python
MOVIE_API = '영화 진흥위원회 API'
GOOGLE_API = 'google directions API'
CHAT_ID = 'Telegram Bot Chat Bot API'

CGV_TOKEN = 'CGV 채팅방 TOKEN'
LOTTE_TOKEN = 'LOTTE 시네마 채팅방 TOKEN'
MEGA_TOKEN = 'MEGABOX 채팅방 TOKEN'
IMAX_TOKEN = 'IMAX알림 채팅방 TOKEN'

```
