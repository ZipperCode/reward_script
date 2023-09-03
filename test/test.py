import datetime
import os

if __name__ == '__main__':
    # Sun Mar 26 20:52:19 GMT+08:00 2023
    GMT = "%a %b %d %H:%M:%S GMT+08:00 %Y"
    print(datetime.datetime.now().strftime(GMT))
    p = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
    print("path = " + p)
    os.makedirs(p)
    with open(os.path.join(p,'test.txt'), 'w+') as f:
        f.write("hello")

