from DirHandler import DirHandler
from NameHandler import NameHandler


file_names = DirHandler("path").get_files()
asset_list = NameHandler(file_names).get_pairs()

for i in range(0, len(asset_list)):
    print(asset_list[i], " .......... ", file_names[i])
