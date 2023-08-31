import datetime

if __name__ == '__main__':
    # Sun Mar 26 20:52:19 GMT+08:00 2023
    GMT = "%a %b %d %H:%M:%S GMT+08:00 %Y"
    print(datetime.datetime.now().strftime(GMT))
