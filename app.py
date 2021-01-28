import requests
from bs4 import BeautifulSoup as bs
import re
import sqlite3
import time
from config import *

conn = sqlite3.connect('database.db')
c = conn.cursor()
sql = "CREATE TABLE IF NOT EXISTS kyo (done_tid INT)"
c.execute(sql)
conn.commit()


def rss2wh(rss, wh):
    if len(rss) != len(wh):
        print("Not equal parameters", flush=True)
        return

    while True:
        for r, z in zip(rss, wh):
            try:
                rss_url = f'https://boards.4chan.org/{r}/index.rss'
            except requests.exceptions.RequestException as e:
                print(f'Error: {e}. Continuing', flush=True)
                continue
            time.sleep(1)
            response = requests.get(rss_url)
            if response.status_code == 200:
                soup = bs(response.text, 'lxml-xml').find_all('item')
                for i in soup:
                    json_sending = {}
                    isImage = False
                    thread_id = int(re.search(r'\d{4,}$', i.guid.text).group())
                    c.execute("SELECT done_tid FROM kyo WHERE done_tid = ?",
                              (thread_id, ))
                    if len(c.fetchall()) > 0:
                        print(
                            f'{thread_id} already exists. Continuing...', flush=True)
                        continue
                    thread_link = i.guid.text
                    thread_title = i.title.text
                    image_link = bs(i.description.text, 'lxml-xml').a['href']
                    if image_link[-3:] in ('jpg', 'png'):
                        isImage = True

                    embed = {
                        "title": thread_title,
                        "url": thread_link,
                    }

                    if isImage:
                        embed["image"] = {"url": image_link}
                    else:
                        pass

                    json_sending["embeds"] = [embed]
                    time.sleep(1)
                    return_code = requests.post(
                        z, json=json_sending, timeout=60).status_code
                    print(
                        f'{thread_title.encode("utf8")} || {thread_link}', flush=True)

                    if not isImage:
                        json_sending.pop("embeds")
                        json_sending["content"] = image_link
                        time.sleep(1)
                        requests.post(
                            z, json=json_sending, timeout=60).status_code
                        print("Posted content too", flush=True)

                    if return_code == 204:
                        print("Posted Successfully", flush=True)
                        c.execute("INSERT INTO kyo (done_tid) VALUES (?)",
                                  (thread_id, ))
                        conn.commit()
                    else:
                        print(f"Error in POST: {return_code}", flush=True)
            else:
                print(f'Error in GET: {response.status_code}', flush=True)

        time.sleep(300)


rss2wh(["fit", "cm", "c", "fa", "lit", "g", "int", "p", "a"], [
       kyo, momiji, shigure, ayame, hatori, hatsuharu, hiro, ritsu, kagura])

conn.close()
