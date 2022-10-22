from inspect import getcomments
import string
import requests
import sys
import getopt
from dataclasses import dataclass
from datetime import datetime

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATETIME_JSON = '%Y-%m-%dT%H:%M:%S.%fZ'
DATETIME_JSON2 = '%Y-%m-%dT%H:%M:%SZ'

@dataclass
class Comment:
    name: string = ''
    comment: string = ''
    id: string = ''
    date: datetime = datetime(1980, 1, 1)

    def toStr(this):
        return '[{2}] {0}: {1}'.format(this.name, this.comment, this.date)

    def toStrRelative(this, date):
        return '[{2}] {0}: {1}'.format(this.name, this.comment, (this.date-date))

def getComments(video, seconds=None, cursor=None):
    comments=[]
    headers={'Client-Id': 'kimne78kx3ncx6brgo4mv6wki5h1ko'}
    url=' https://api.twitch.tv/v5/videos/{0}/comments'
    url=url.format(video)
    if (seconds != None):
        url += '?content_offset_seconds={0}'.format(int(seconds))
    if (cursor != None):
        url += '?cursor={0}'.format(cursor)

    r=requests.get(url, headers=headers)

    if (r.status_code == 200):
        responseJson=r.json()
        nextCursor=None
        if '_next' in responseJson:

            nextCursor=responseJson['_next']

        for item in responseJson['comments']:
            try:
                date=datetime.strptime(
                    item['created_at'], DATETIME_JSON)
            except:
                try:
                     date=datetime.strptime(
                         item['created_at'], DATETIME_JSON2)
                except:
                    date=None
            comments.append(Comment(name=item['commenter']['display_name'],
                            comment=item['message']['body'], id=item['_id'], date=date))
    return comments, nextCursor

def dumpVideo(video, seconds):
    first_date=None
    last_date=None
    cursor=None
    iteration=0
    comments, cursor=getComments(video, seconds)
    while cursor != None:
        com, cursor=getComments(video, cursor=cursor)
        comments += com
        iteration += 1
    print('Comments {0} Iterations {1}'.format(len(comments), iteration))
    return comments

def main(argv):
    video=None
    sec=None
    relative=False
    try:
        opts, args=getopt.getopt(argv, 'v:s:r', ['video', 'sec', 'relative'])
    except getopt.GetoptError:
        print('test.py -i <video> -s <sec>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <video> -s <sec>')
            sys.exit()
        elif opt in ('-v', '--video'):
            video=arg
        elif opt in ('-s', '--sec'):
            sec=arg
        elif opt in ('-r', '--relative'):
            relative=True

    print('Video : ', video)

    comments=dumpVideo(video, sec)

    with open('comments.txt', 'w', encoding='utf-8') as f:
        if (relative):
            rd=comments[0].date
            f.write('\r\n'.join(c.toStrRelative(rd) for c in comments))
        else:
            f.write('\r\n'.join(c.toStr() for c in comments))

if __name__ == '__main__':
    main(sys.argv[1:])
