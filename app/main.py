from flask import Flask, send_from_directory, request
from app.download_file_from_gdrive import add_images
import time, json, os, sqlite3, random, string
from flask_cors import CORS
from hashlib import sha512

app = Flask(__name__)
CORS(app)
my_ip = "127.0.0.1"
passwd = "" # Insert your password here

def init_db():
    conn = sqlite3.connect("app/data.db")
    curs = conn.cursor()
 
    curs.execute("""CREATE TABLE IF NOT EXISTS
                        images (
                            image_name text PRIMARY KEY, 
                            status text, 
                            class text, 
                            api_key text
                        )""")
    
    os.system("mkdir app/dataset/")
    files = os.listdir("app/dataset/")
    for file in files:
        file_status = curs.execute("SELECT status FROM images WHERE image_name=?", (file, )).fetchone()

        if file_status == None:
            curs.execute("INSERT INTO images (image_name, status, class, api_key) VALUES (?, ?, ?, ?)", (file, "not processed", "", ""))


    conn.commit()
    curs.close()         

def generate_api_key():
    return ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(32))


@app.route("/api/get", methods=["GET"])
def get_image():
    conn = sqlite3.connect("app/data.db")
    curs = conn.cursor()

    not_processed_images = curs.execute("SELECT image_name FROM images WHERE status='not processed'").fetchall()
    img = random.choice(not_processed_images)[0]
    api_key = generate_api_key()

    curs.execute("UPDATE images SET status='processing', api_key=? WHERE image_name=?", (api_key, img))

    conn.commit()
    curs.close()

    return f"{{'img_name': '{img}', 'api_key': '{api_key}', 'img_link': 'http://{my_ip}/images/{img}'}}"

@app.route("/api/add_images", methods=["POST"])
def add():
    hash = request.form.get("hash")
    link = request.form.get("link")

    if hash != None and link != None:
        if hash == sha512((passwd + link).encode()).hexdigest():
            add_images(link)
            init_db()
            return "OK"

    return "Error"



@app.route("/api/status", methods=["GET"])
def status():
    conn = sqlite3.connect("app/data.db")
    curs = conn.cursor()

    not_processed_images = len(curs.execute("SELECT image_name FROM images WHERE status='not processed'").fetchall())
    processed_images = len(curs.execute("SELECT image_name FROM images WHERE status='processed'").fetchall())
    deleted_images = len(curs.execute("SELECT image_name FROM images WHERE status='deleted'").fetchall())
    in_process_images = len(curs.execute("SELECT image_name FROM images WHERE status='processing'").fetchall())

    return f'{{"not_processed": {not_processed_images}, "processed": {processed_images}, "deleted": {deleted_images}, "in_process": {in_process_images}}}'

@app.route("/api/post", methods=["POST"])
def post_answer():
    img_name = request.form.get("img_name")
    api_key = request.form.get("api_key")
    status = request.form.get("status")
    img_class = request.form.get("class")

    if img_name != None and api_key != None and img_class != None and status != None and status in ["save", "delete"]:
        conn = sqlite3.connect("app/data.db")
        curs = conn.cursor()

        img = curs.execute("SELECT * FROM images WHERE image_name=? and api_key=?", (img_name, api_key)).fetchone()

        if img != None and img[1] == "processing":
            if status == "save":
                curs.execute("UPDATE images SET status='processed', class=? WHERE image_name=? and api_key=?", (img_class, img_name, api_key))
            elif status == "delete":
                curs.execute("UPDATE images SET status='deleted' WHERE image_name=? and api_key=?", (img_name, api_key))

        conn.commit()
        curs.close()

    
        if img != None and img[1] == "processing":
            return "OK"

    return "Error"

@app.route('/images/<path:filename>')
def download_file(filename):
    return send_from_directory("dataset/", filename, as_attachment=True)

init_db()