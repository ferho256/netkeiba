import argparse
import os
import requests
import time

from bs4 import BeautifulSoup as BS
import pandas as pd
from requests.sessions import session
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class Netkeiba:
    def __init__(self, login_id=None, password=None):
        login_url = 'https://regist.netkeiba.com/account/?pid=login'

        self.session = requests.session()

        if login_id is not None and login_id is not None:
            login_info = {
                'pid' : 'login',
                'action' : 'auth',
                'return_url2' : '',
                'mem_tp' : '',
                'login_id' : login_id,
                'pswd' : password,
            }
            self.ses = self.session.post(login_url, data=login_info)
        else:
            print('netkeibaのアカウントを入力してください')
            exit()
        time.sleep(1)

    def get_valid_urls(
        self,
        start_year=2020,
        start_mon=1,
        end_year=2020,
        end_mon=12):

        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(chrome_options=options)
        wait = WebDriverWait(driver, 10)

        search_detail_URL =\
            'https://db.netkeiba.com/?pid=race_search_detail'

        driver.get(search_detail_URL)
        wait.until(EC.presence_of_all_elements_located)

        # 芝, ダートを選択
        siba = driver.find_element_by_id('check_track_1')
        siba.click()
        dirt = driver.find_element_by_id('check_track_2')
        dirt.click()

        # 期間を選択
        start_year_element = driver.find_element_by_name('start_year')
        start_year_select = Select(start_year_element)
        start_year_select.select_by_value(str(start_year))
        start_mon_element = driver.find_element_by_name('start_mon')
        start_mon_select = Select(start_mon_element)
        start_mon_select.select_by_value(str(start_mon))
        end_year_element = driver.find_element_by_name('end_year')
        end_year_select = Select(end_year_element)
        end_year_select.select_by_value(str(end_year))
        end_mon_element = driver.find_element_by_name('end_mon')
        end_mon_select = Select(end_mon_element)
        end_mon_select.select_by_value(str(end_mon))

        # 中央競馬場を指定
        # やらないと地方や海外が混ざる
        for i in range(1, 11):
            terms = driver.find_element_by_id(f'check_Jyo_{i:02}')
            terms.click()

        # 表示件数を最大(100)に変更
        list_element = driver.find_element_by_name('list')
        list_select = Select(list_element)
        list_select.select_by_value('100')

        form = driver.find_element_by_css_selector(
            '#db_search_detail_form > form')
        form.submit()
        wait.until(EC.presence_of_all_elements_located)

        save_dir = './valid_urls'
        filename = 'valid_urls.csv'
        urls = []

        try:
            os.makedirs(save_dir)
        except FileExistsError:
            pass

        while True:
            time.sleep(1)
            wait.until(EC.presence_of_all_elements_located)
            all_rows = driver.find_element_by_class_name(
                'race_table_01').find_elements_by_tag_name('tr')
            for row in range(1, len(all_rows)):
                race_url =\
                        all_rows[row].find_elements_by_tag_name('td')[4]\
                            .find_element_by_tag_name('a').get_attribute('href')
                urls.append(race_url)
            try:
                target = driver.find_elements_by_link_text('次')[0]
                driver.execute_script('arguments[0].click();', target)
            except IndexError:
                break

        urls = pd.DataFrame(urls)
        urls.columns = ['URL']
        urls.to_csv(f'{save_dir}/{filename}')

        driver.close()


    def scrape_race(self, url):
        
        self.ses = self.session.get(url)
        self.ses.encoding = 'EUC-JP'
        # bs = BS(ses.text, 'html.parser')
        filename = "test.html"
        with open(filename, 'w', encoding='EUC-JP') as f:
            f.write(self.ses.text)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='''
    netkeibaから競馬情報を取得するコード
    ''')
    parser.add_argument('-url', '--get_url', type=bool, default=False, )
    parser.add_argument('-i', '--login_id', type=str, default=None, help='メールアドレス')
    parser.add_argument('-p', '--password', type=str, default=None, help='ログインパスワード')
    args = parser.parse_args()

    NS = Netkeiba(args.login_id, args.password)

    if args.get_url:
        period = {
            'start_year': 2015,
            'start_mon': 1,
            'end_year': 2021,
            'end_mon': 11,
        }

        NS.get_valid_urls(*period.values())

    test_url = 'https://db.netkeiba.com/race/202105050812/'
    NS.scrape_race(test_url)

