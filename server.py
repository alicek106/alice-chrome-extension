from flask import Flask, request
from flask_cors import CORS
from requests import get
import boto3
import pymysql

import logging
import os
import uuid
import time

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, resources={r'/*': {'origins': '*'}}, supports_credentials=True)

logging.getLogger('flask_cors').level = logging.DEBUG
logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO
)


def upload_folder_to_s3(s3bucket, inputDir, s3Path):
    os.system("ls -ltR " + inputDir)
    logging.info("Local Source : {}".format(inputDir))
    logging.info("Dest S3path : {}".format(s3Path))

    try:
        for path, subdirs, files in os.walk(inputDir):
            for file in files:
                dest_path = path.replace(inputDir, "")
                __s3file = os.path.normpath(s3Path + '/' + dest_path + '/' + file)
                __local_file = os.path.join(path, file)
                logging.info("Upload : {} to Target {}".format(__local_file, __s3file))
                s3bucket.upload_file(__local_file, __s3file)
                logging.info("Succeeded to upload files to s3")
    except Exception as e:
        logging.error("Failed to upload files to s3")
        logging.error(e)
        raise e


def download(url, file_name):
    with open(file_name, "wb") as file:
        response = get(url)
        file.write(response.content)


@app.route('/', methods=['POST'])  # post echo api
def post_echo_call():
    param = request.get_json()
    logging.info(param)

    image_links = param["imageLinks"]
    albums_name = param["identifierName"]
    episode_number = param["identifierNumber"]

    if len(image_links) == 0:
        return {'status':'empty image list'}, 400

    random_uid = str(uuid.uuid4())
    os.mkdir('./' + random_uid)

    for i, imageLink in enumerate(image_links):
        download(imageLink, './' + random_uid + '/' + str(i + 1) + '.jpg')

    s3 = boto3.resource('s3', region_name='ap-northeast-2')
    s3bucket = s3.Bucket(os.environ['S3_BUCKET_NAME'])
    upload_folder_to_s3(s3bucket, random_uid, "albums_images/" + random_uid)

    # Test connection info.
    conn = pymysql.connect(host='192.168.56.100',
                           user='alice',
                           password='alice',
                           db='alice',
                           charset='utf8')

    albumsQuerySql = "select * from Albums where Title = %s;"
    episodeSql = "insert into Episodes (AlbumsID, Uploader, ThumbnailUrl, UploadDate, EpisodeNumber) values (%s, %s, %s, %s, %s);"
    episodeSelectSql = "select * from Episodes where AlbumsID = %s and EpisodeNumber = %s;"
    imageSql = "insert into EpisodeImages (Seq, Link, AlbumsID, EpisodesID, EpisodesNumber) values (%s, %s, %s, %s, %s);"

    with conn:
        cur = conn.cursor()
        cur.execute(albumsQuerySql, (albums_name))
        result = cur.fetchone()
        albumsId = result[0]
        episodesCount = int(result[4]) + 1

        cur.execute(episodeSql, (albumsId, 'root', 'thumbnailUrl', int(time.time()), int(episode_number)))
        conn.commit()

        cur.execute(episodeSelectSql, (albumsId, int(episode_number)))
        result = cur.fetchone()
        episodeId = result[0]

        for i, imageLink in enumerate(image_links):
            cur.execute(imageSql, (
                int(i + 1), random_uid + '/' + str(i + 1) + '.jpg', int(albumsId), int(episodeId), int(episode_number)))

        cur.execute('update Albums set EpisodesCount = %s where ID = %s;', (episodesCount, albumsId))
        conn.commit()

    return {"status": "ok"}, 200


if __name__ == "__main__":
    app.run(port=8000)
