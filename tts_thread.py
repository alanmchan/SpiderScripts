'''
多线程爬去tts教学视频
'''

from Crypto.Cipher import AES
import requests, re, time, random
from queue import Queue
from threading import Thread


class TTSSpider(object):
    '''tts 视频爬取'''
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
            'Referer': 'http://tts.tmooc.cn/video/showVideo?menuId=646374&version=AIDTN201809'
        }
        self.m3u8_url = 'http://videotts.it211.com.cn/{}/{}.m3u8'
        self.q = Queue()

        self.listt = []

    def get_m3u8(self, url):
        '''获取m3u8'''
        resp = requests.get(url, headers=self.headers).text
        # print(resp)
        # 正则匹配key的链接
        pattern_key = re.compile('#EXT-X-KEY.*?URI="(.*?)"', re.S)
        try:
            key_link = pattern_key.findall(resp)[0]
            key = self.get_key(key_link)
        except:
            return False

        # 正则匹配ts文件链接
        pattern_ts = re.compile('#EXTINF.*?000,\n(.*?)\n', re.S)
        ts_list = pattern_ts.findall(resp)  # ts链接列表

        for ts_link in ts_list:
            print(ts_link)
            self.get_ts(ts_link, key)
            # time.sleep(random.randint(1,5))
        return True

    def get_key(self, key_link):
        '''根据key的url获取key文件'''
        resp = requests.get(url=key_link, headers=self.headers)
        resp.encoding = "utf-8"
        return resp.content

    def get_ts(self, ts_link, key):
        '''根据ts链接获取ts文件'''
        resp = requests.get(ts_link, headers=self.headers).content
        # 正则匹配获取文件名
        pattern = re.compile('.cn/(.*?)/')
        filename = pattern.findall(ts_link)[0]

        # 创建解码对象
        cryptor = AES.new(key, AES.MODE_CBC, key)
        with open('test/' + filename + '.mp4' , 'ab') as f:
            f.write(cryptor.decrypt(resp))  # 解码并写入文件

    def url_in(self):
        month_days = {
            2:28,
            3: 31,
            4:30,
            5:31,
            6:30,
            7:26
        }
        for month, days in month_days.items():
            for day in range(1, days + 1):
                for i in ['am', 'pm']:
                    # 拼接url
                    course = "%s1902%02d%02d%s" % ('aid', month, day, i)
                    url = self.m3u8_url.format(course, course)
                    self.q.put((url, course))

    def start_spider(self):
        while True:
            # 获取url
            if not self.q.empty():
                url, course = self.q.get()
                print(url)
                if self.get_m3u8(url):
                    print(course, "爬取成功")
                else:
                    print(course, "数据不存在")
                time.sleep(3)
            else:
                break

    def main(self):
        self.url_in()
        # 线程列表
        t_list = []
        # 创建多个线程并启动线程
        for i in range(10):
            t = Thread(target=self.start_spider)
            t_list.append(t)
            t.start()
        # 回收线程
        for t in t_list:
            t.join()





if __name__ == '__main__':
    spider = TTSSpider()
    spider.main()