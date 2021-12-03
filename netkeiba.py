import os
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class NetkeibaScraper:
    def __init__(self):
        self.search_detail_URL =\
            'https://db.netkeiba.com/?pid=race_search_detail'

    def scrape_valid_urls(self, period):

        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(chrome_options=options)
        wait = WebDriverWait(driver, 10)

        driver.get(self.search_detail_URL)
        wait.until(EC.presence_of_all_elements_located)

        # 芝, ダートを選択
        siba = driver.find_element_by_id('check_track_1')
        siba.click()
        dirt = driver.find_element_by_id('check_track_2')
        dirt.click()

        # 期間を選択
        start_year_element = driver.find_element_by_name('start_year')
        start_year_select = Select(start_year_element)
        start_year_select.select_by_value(str(period['start_year']))
        start_mon_element = driver.find_element_by_name('start_mon')
        start_mon_select = Select(start_mon_element)
        start_mon_select.select_by_value(str(period['end_mon']))
        end_year_element = driver.find_element_by_name('end_year')
        end_year_select = Select(end_year_element)
        end_year_select.select_by_value(str(period['end_year']))
        end_mon_element = driver.find_element_by_name('end_mon')
        end_mon_select = Select(end_mon_element)
        end_mon_select.select_by_value(str(period['end_mon']))

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

        pd.DataFrame(urls).to_csv(f'{save_dir}/{filename}')


if __name__ == '__main__':

    NS = NetkeibaScraper()

    period = {
        'start_year': 2015,
        'start_mon': 1,
        'end_year': 2021,
        'end_mon': 11,
    }

    NS.scrape_valid_urls(period)
