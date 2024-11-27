from bs4 import BeautifulSoup
import requests
from urllib3.util.retry import Retry
import os
import time
import re
import pickle
import string

# 定义网站和保存位置的基本信息
website_url = "https://www.hooktheory.com"
artists_entry_url = website_url + "/theorytab/artists/"
sleep_time = 0.11
alphabet_list = string.ascii_lowercase
root_dir = "./datasets"
root_info = os.path.join(root_dir, "info")
url_cache = "./datasets/cache"
url_artists_cache_file = os.path.join(url_cache, "url_artist_list_cache.pkl")

# 创建一个带有重试策略的会话
session = requests.Session()
retry = Retry(
    total=5,  # 总共重试次数
    backoff_factor=0.1,  # 重试间隔时间
    status_forcelist=[500, 502, 503, 504],  # 需要重试的状态码
)
adapter = requests.adapters.HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)


def fetch_artists(artists_url: str, alphabet_list: str, cache_file: str = None):
    """从网站爬取指定字母开头的艺人列表并保存缓存"""
    if cache_file and os.path.exists(cache_file):
        print("艺人信息已缓存，直接读取")
        with open(cache_file, "rb") as f:
            url_artist_list = pickle.load(f)
        print(f"从缓存文件中读取到{len(url_artist_list)}个艺人链接")
        return url_artist_list

    url_artist_list = []
    for ch in alphabet_list:
        print(f"正在爬取==[{ch}]==========================")
        page_count = 1
        while True:
            time.sleep(sleep_time)
            url = artists_url + ch + "?page=" + str(page_count)
            response_tmp = requests.get(url)
            soup = BeautifulSoup(response_tmp.text, "html.parser")
            item_list = soup.find_all("li", {"class": re.compile("overlay-trigger")})
            if item_list:
                page_count += 1
                for item in item_list:
                    url_artist_list.append(
                        item.find_all("a", {"class": "a-no-decoration"})[0]["href"]
                    )
            else:
                break
        print(f"{ch}字母开头艺人已爬取完毕")
    if cache_file:
        with open(cache_file, "wb") as f:
            pickle.dump(url_artist_list, f)
    print(f"全部艺人信息爬取完毕，共有{len(url_artist_list)}个")
    return url_artist_list


def fetch_artist_songs(artist_link: str, cache_file: str = None):
    """爬取艺人的歌曲列表并保存缓存"""
    if cache_file and os.path.exists(cache_file):
        print(f"艺人 {artist_link.split('/')[-1]} 的歌曲信息已缓存，直接读取")
        with open(cache_file, "rb") as f:
            songs_name = pickle.load(f)
        print(f"从缓存文件中读取到{len(songs_name)}首歌曲")
        return songs_name

    print(f"正在爬取艺人 {artist_link.split('/')[-1]} 的歌曲：")
    response_tmp = session.get(website_url + artist_link)
    soup = BeautifulSoup(response_tmp.text, "html.parser")
    item_list = soup.find_all("li", {"class": re.compile("overlay-trigger")})
    songs_name = []
    for item in item_list:
        song_name = item.find_all("a", {"class": "a-no-decoration"})[0]["href"].split(
            "/"
        )[-1]
        songs_name.append(song_name)
        print(f"   > {song_name}")

    if cache_file:
        with open(cache_file, "wb") as f:
            pickle.dump(songs_name, f)

    return songs_name


def song_retrieval(artist_name: str, song_name: str):
    """用于爬取指定艺人指定歌曲的数据"""
    suffix = "/theorytab/view/" + artist_name + "/" + song_name
    song_url = website_url + suffix
    response_temp = requests.get(song_url)
    soup = BeautifulSoup(response_temp.text, "html.parser")
    sections = [
        item["href"].split("#")[-1]
        for item in soup.find_all("a", {"href": re.compile(suffix + "#")})
    ]
    print(f"Sections found: {sections}")
    pks = [
        item["href"].split("/")[-1]
        for item in soup.find_all("a", {"href": re.compile("/theorytab/chords/pk/")})
    ]
    print(f"PKs found: {pks}")
    for index, pk in enumerate(pks):
        req_url = f"{website_url}/songs/getXmlByPk?pk={pk}"
        response_info = requests.get(req_url)
        with open(os.path.join(root_info,sections[index]+'.xml'),'w',encoding='utf-8') as f:
            f.write(response_info.text)
        time.sleep(0.08)

song_retrieval("lone","hiraeth")

if __name__ != "__main__":
    # 补全目录
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)
    if not os.path.exists(root_info):
        os.makedirs(root_info)
    # 爬取艺人信息
    artist_links_collection = fetch_artists(
        artists_entry_url, alphabet_list, url_artists_cache_file
    )
    # 获取歌曲列表
    num_song = 0
    artist_song_dict = dict()
    for artist_link in artist_links_collection:
        artist_name = artist_link.split("/")[-1]
        songs_name = fetch_artist_songs(
            artist_link, os.path.join(url_cache, "songs", artist_name + ".pkl")
        )
        num_song += len(songs_name)
        artist_song_dict[artist_name] = songs_name
        print(f"当前歌曲名单总数：{num_song}")
    for artist_link in artist_links_collection:
        artist_name = artist_link.split("/")[-1]
        info_path = os.path.join(url_cache, "info")
        # song_retrieval(artist_name,artist_song_dict[artist_name][0])
