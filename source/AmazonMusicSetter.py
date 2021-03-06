from datetime import timedelta
from source.DriverSetterBase import DriverSetterBase
import time
from selenium.webdriver.common.action_chains import ActionChains
from source.FuzzyMatcher import FuzzyMatcher


class AmazonMusicSetter(DriverSetterBase):

    def __init__(self, test_mode, asset_list, email=None, password=None, playlist_name=None):
        super(AmazonMusicSetter, self).__init__()
        self.login(test_mode, email, password)
        self.setup_playlist(playlist_name)
        self.asset_list = asset_list
        self.status_matched = []
        self.status_failed = []
        self.find_assets(self.asset_list)
        self.driver.quit()
        self.exec_time = timedelta(seconds=time.time() - self.exec_time)
        self.log_status()

    def login(self, test_mode, email, password):
        # Primary page should be 'music.amazon.com', '.in' just to ease testing, otherwise 2 hops of log-ins
        self.driver.get('https://music.amazon.in/home')

        if test_mode is False or (email is None or password is None):
            print("Please Sign in to the service.\n")
            while True:
                res = input("Press y/Y to continue after sign-in...\n")
                if res == 'y' or res == 'Y':
                    break
        else:
            self.password = password
            self.email = email
            try:
                # dismiss popup about preferences since we aren't logged in
                self.move_and_click("//*[@id=\"dialogBoxView\"]/section/section/section[2]/button[2]", True)
                time.sleep(1)
            except Exception as e:
                self.logger.exception("No popup", e)
            # self.move_and_click("//*[@id=\"transportSignInView\"]/div", True)
            self.move_and_click("//*[@id=\"contextMenu\"]/li[1]/a", True)
            self.driver.find_element_by_xpath("//*[@id=\"ap_email\"]").send_keys(self.email)
            self.driver.find_element_by_xpath("//*[@id=\"ap_password\"]").send_keys(self.password)
            self.move_and_click("//*[@id=\"signInSubmit\"]", True)

    def setup_playlist(self, playlist):
        if playlist is None:
            self.playlist_name = input("Enter the new playlist name...\n")
        else:
            self.playlist_name = playlist
        time.sleep(3)
        self.move_and_click("//*[@id=\"newPlaylist\"]", True)
        self.driver.find_element_by_xpath("//*[@id=\"newPlaylistName\"]").send_keys(self.playlist_name)
        self.move_and_click("//*[@id=\"savePlaylistDialog\"]/a", True)

    # Method to handle the adding of selected tile asset to playlist
    def add_tile_asset(self, target_tile: int):
        self.driver.find_element_by_xpath("//*[@id=\"dragonflyView\"]/div/div[1]/div/h1").click()

        # Making sure with move_to that the element is visible/interactable
        self.move_and_click(
            "//*[@class=\"card trackCard\"]/div[2]/div/div[1]/div[" + str(target_tile) + "]/div[3]/span[3]", True)

        self.move_and_click("//*[@id=\"contextMenuContainer\"]/section/ul/li[2]/div", True)

        self.move_and_click("//dl/dd/ul/li/span[contains(text(), '" + self.playlist_name + "')]", True)

    # Method for handling the searching of an asset, returns the number of tiles available after the search
    def search_asset(self, artist, title):
        # Making sure with move_to that the element is visible/interactable
        search_area = self.driver.find_element_by_xpath("// *[ @ id = \"searchMusic\"]")
        ActionChains(self.driver).move_to_element(search_area).click(search_area).perform()
        search_area.clear()
        search_area.send_keys(artist + " " + title)

        self.move_and_click("//*[@id=\"dragonflyTransport\"]/div/div[1]/div/button", True)
        self.move_and_click("//*[@id=\"dragonflyTransport\"]/div/div[1]/div/button", True)

        results = self.driver.find_elements_by_xpath(
            "//*[@class=\"card trackCard\"]/div[2]/div/div[1]/div")

        return results

    # The method that iterates through assets, searching the asset and adding to playlist if found as a Match.
    def find_assets(self, asset_list):

        for asset in asset_list:
            asset_filetype = asset[0]
            if asset_filetype == 0:
                self.status_failed.append("FILE FAILED=" + str(asset))
                continue
            asset_artist = asset[1]
            asset_title = asset[2]

            results = self.search_asset(asset_artist, asset_title)

            # Expected to handle an exception for this case...but this seems to work somehow...
            if len(results) == 0:
                self.status_failed.append("NO RESULTS=" + str(asset))
                continue

            # iterate result tiles and match, max attempts = 5
            max_factor = 0
            target_tile = 0
            for i in range(1, min(len(results)+1, 5)):
                tile_song = self.driver.find_element_by_xpath(
                    "//*[@class=\"card trackCard\"]/div[2]/div/div[1]/div[" + str(i) + "]/div[2]/div[1]")\
                    .get_attribute("title").lower()
                tile_artist = self.driver.find_element_by_xpath(
                    "//*[@class=\"card trackCard\"]/div[2]/div/div[1]/div[" + str(i) + "]/div[2]/div[2]")\
                    .get_attribute("title").lower()

                # Match condition, needs a proper handler class with advanced logic/fuzzy....
                current_factor = FuzzyMatcher.get_match_factor(asset_filetype, asset_artist,
                                                               asset_title, tile_artist, tile_song)
                self.logger.debug(str("Current match status : %s  %s VS %s  %s  , factor : %2f"
                                      % (asset_title, asset_artist, tile_song, tile_artist,  current_factor)))
                if current_factor > max_factor:
                    target_tile = i
                    max_factor = current_factor

            if max_factor != 0:
                try:
                    self.add_tile_asset(target_tile)
                    self.status_matched.append(
                        str("MATCH SUCCESS=%s, MATCH FACTOR=%s" % (str(asset), str(max_factor))))
                    time.sleep(1)
                except Exception as e:
                    self.logger.exception(e)
                    self.status_failed.append("FAILED TO ADD DUE TO EXCEPTION=" + str(asset))

            else:
                self.status_failed.append("FAILED TO MATCH=" + str(asset))


if __name__ == "__main__":
    # testing
    test_list = [
                (3, "alan walker", "force"),
                (2, "siafugasudfgsidfg", "asudgausgdausydg"),
                (3,  "ahrix", "nova"),
                (3, "alan walker", "spectre")
                ]
    ob = AmazonMusicSetter(False, test_list)
