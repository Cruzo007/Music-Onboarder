import re


class NameHandler:
    re_pattern = "^(?P<artist>(\w+\s)+)\s*-\s*(?P<song>(\w+\s*)+)"
    file_list = []
    asset_pair =[]

    def __init__(self, file_list):
        self.file_list = file_list

    def set_pairs(self):
        for name in self.file_list:
            match = re.search(self.re_pattern, name)
            if match:
                pair = match.group("artist").strip().lower() + "-" +match.group("song").strip().lower()

            else:
                pair = "INVALID FILENAME-" + name

            self.asset_pair.append(pair)

    def get_pairs(self):
        self.set_pairs()
        return self.asset_pair


if __name__ == "__main__":
    sample = [
              'Arctic Monkeys - I Wanna Be Yours.mp3',
              'Arctic Monkeys - One For The Road Official Video[www.MP3Fiber.com].mp3',
              'Arctic Monkeys - R U Mine.mp3',
              'Arctic Monkeys By Stop The World I Wanna Get Off With You Official Audio[www.MP3Fiber.com].mp3'
              ]
    ob = NameHandler(sample)
    for i in ob.get_pairs():
        print(i)