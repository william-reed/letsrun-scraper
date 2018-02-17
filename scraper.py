import bs4
import requests
import re
import json
import os
from mysql.connector import connection

headers = {'User-Agent': 'LetsRun Analyser 1.0'}

add_post = ("INSERT INTO posts "
            "(id, thread, parent, author, subject, body, datestamp, cat, body_text, body_html, thread_url, reply_url, "
            "main_category, sub_category, cookie_db_field) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")


def extract_post(id, cursor):
    """
    :param id: the reply / post id
    :param cursor: the database cursor
    :return:
    """
    reply = bs4.BeautifulSoup(requests.get('https://www.letsrun.com/forum/post.php?reply=' + str(id),
                                           headers=headers).text,
                              'html.parser').text
    # make sure the page loaded correct and we didnt stumble upon a deleted / non existant post
    if "404: Not Found" in reply:
        print("404: Not Found for " + str(id))
        return

    # https://stackoverflow.com/questions/13323976/how-to-extract-a-json-object-that-was-defined-in-a-html-page-javascript-block-us
    # also see freenode #python logs from 2/10/18 around 10:00AM EST for more info on this
    # extract the JavaScript stored in window.App.state.reply
    try:
    	reply_text = re.compile(r'window.App.state.reply = ({.*?});\s*$', re.MULTILINE).search(reply).group(1)
    	reply_json = json.loads(reply_text)
    except AttributeError:
    	print("AttributeError, retrying")
    	extract_post(id, cursor)
    	return


    # insert reply_json into db
    print("Subject: " + reply_json['subject'] + " by " + reply_json['author'] + " on " + reply_json['datestamp'])

    data = [reply_json['id'], reply_json['thread'], reply_json['parent'], reply_json['author'], reply_json['subject'],
     		reply_json['body'], reply_json['datestamp'], reply_json['cat'], reply_json['body_text'], reply_json['body_html'],
      		reply_json['thread_url'], reply_json['reply_url'],reply_json['main_category'], reply_json['sub_category'],
       		reply_json['cookie_db_field']]

    cursor.execute(add_post, data)


if __name__ == '__main__':
    db = connection.MySQLConnection(user=os.environ['MYSQL_USER'], password=os.environ['MYSQL_PASSWORD'],
            database=os.environ['LETSRUN_DB'], charset='utf8mb4', collation='utf8mb4_bin')
    cursor = db.cursor()

    # set charset and collation
    cursor.execute("SET NAMES 'utf8mb4' COLLATE 'utf8mb4_bin'")
    db.commit()

    # find starting index
    start = 0
    stop = 8666120
    cursor.execute("SELECT id FROM posts ORDER BY id DESC LIMIT 1;")
    result = cursor.fetchone()

    if result is not None:
        start = result[0] + 1

    for i in range(start, stop):
        extract_post(i, cursor)

        # commit every 100 rows
        if i % 100 == 0:
        	db.commit()

    # do work
    db.close()

# weird posts
# 1554667 has a negative timestamp
