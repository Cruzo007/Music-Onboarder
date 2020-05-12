import sys
from selenium import webdriver
from selenium.webdriver import ActionChains
import os
import re
import time

class DriverGetterBase:
    driver = None
    playlist_src = None
    asset_list = None
    exec_time = None

    def __init__(self):
        # Dynamic Path computation, handling execution from anywhere
        self.exec_time = time.time()
        cur_path = os.getcwd()
        path_groups = cur_path.split("Music-Onboarder")
        dyn_path = cur_path
        rel_path = ""
        if path_groups[1] != '':
            counter = path_groups[1].count("\\")
            for i in range(0, counter):
                rel_path = rel_path + "../"
            dyn_path = rel_path

        # Only supporting win/Mac OS X
        if sys.platform == "win32":
            self.driver = webdriver.Chrome(dyn_path + '/webdriver/chromedriver.exe')
        else:
            self.driver = webdriver.Chrome(dyn_path + '/webdriver/chromedriver_mac64')
        self.driver.implicitly_wait(10)

    # Method for easy clicking/ just movement to the element as per the bool flag
    def move_and_click(self, xpath: str, click: bool):
        element = self.driver.find_element_by_xpath(xpath)
        if click is True:
            ActionChains(self.driver).move_to_element(element).click().perform()
        else:
            ActionChains(self.driver).move_to_element(element).perform()

    def context_click(self, xpath: str):
        element = self.driver.find_element_by_xpath(xpath)
        ActionChains(self.driver).move_to_element(element).context_click().perform()

    """
    Normalise strings in between services, as Explicit/Featuring substrings/tags
    differ from service to service.
    
    Maintain the hierarchy of the substitutions, else the strings might break.
    """
    @staticmethod
    def string_normalizer(asset: str):
        re_feats = "ft\.|featuring\.|feat\."
        re_explicits = "\[e\]|explicit"
        re_brackets_etc = "\(|\[|\]|\)"
        re_spaces = "\s\s+"
        asset = re.sub(re_feats, "", asset)
        asset = re.sub(re_explicits, "", asset)
        asset = re.sub(re_brackets_etc, "", asset)
        asset = re.sub(re_feats, " ", asset)
        asset = re.sub(re_spaces, " ", asset)

        return asset

    def get_status(self):
        total = len(self.asset_list)
        log = []
        summary = "Total=" + str(total) + ", PlaylistSource=" + str(self.playlist_src)
        log.append(summary)
        for item in self.asset_list:
            log.append(item)
        log.append("Execution time= " + str(self.exec_time))

        return log

