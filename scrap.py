import requests
from bs4 import BeautifulSoup
import re
import time
import pandas as pd

def extract_number(text):
    '''
    문자열에서 숫자만 뽑아내는 함수
    '''
    search = re.compile('\d+').search(text)
    if search:
        return search.group()
    else:
        return 0


def scrap_page(soup):
    '''
    하나의 페이지를 스크래핑하는 함수
    '''
    # 모든 카드를 찾는다
    cards = soup.find_all(class_='job_seen_beacon')
    data = []
    # 모든 카드를 순회하면서, 각 카드에 있는 구인공고 정보를 뽑아낸다
    for card in cards:
        title = card.find(class_='jobTitle').text.replace('new', '')
        company_name = card.find(class_='companyName').text
        location = card.find(class_='companyLocation').text
        description = card.find(class_='job-snippet').text
        date = extract_number(card.find(class_='date').text)

        # 하나의 구인공고 데이터 딕셔너리화
        card_data = {
            'title': title,
            'company_name': company_name,
            'location': location,
            'description': description,
            'date': date
        }

        # 하나의 구인공고를 리스트에 담기
        data.append(card_data)

    return data 


def export_csv(data):
    '''
    리스트&딕셔너리 형태의 데이터를 CSV로 Export 하는 함수
    '''
    df = pd.DataFrame(data)
    df.to_csv("data.csv", encoding='utf-8-sig')


def run_scrapping():
    '''
    Indeed 전체 페이지를 모두 스크래핑하는 함수
    '''
    print('Start Scrap')  
  
    domain = 'https://kr.indeed.com'
    path = '/jobs?q=python&l=서울'

    data = []

    running = True  # 스크래퍼 실행중
    counter = 0
    # 여러 페이지 스크래핑
    while running:
        # 페이지 HTML 가져오기
        url = domain + path
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 현재 페이지 스크래핑
        page_data = scrap_page(soup)
        data.extend(page_data)

        # pagination 체크
        pagination = soup.find(class_='pagination-list')
        last_a = pagination.find_all('a')[-1]
        if last_a['aria-label'] == '다음' and counter < 10:
            path = last_a['href']  # 다음 페이지의 path 부분을 추출
        else:
            running = False  # 스크래퍼 종료

        print(f'{counter+1}페이지 스크래핑 완료')

        # 1초간 대기
        time.sleep(1)
        counter += 1

    print('End Scrap') 
    
    # 모은 데이터 반환
    return data