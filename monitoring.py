import environ
import os

from pathlib import Path

import time
import datetime
import json
from django.conf import settings
from utils.convertcurrency import convert
from product.scrape.engineselector import select_engine
# from utils.mail import send_mail
from ebaysdk.trading import Connection
import psycopg2

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def config():
    env = environ.Env()
    BASE_DIR = Path(__file__).resolve().parent
    env.read_env(str(BASE_DIR / ".env"))

    databases = {
        'host': env('DB_HOST'),
        'db_name': env('DB_NAME'),
        'user': env('DB_USER'),
        'password': env('DB_PASSWORD'),
        'port': env('DB_PORT'),
    }

    return databases

def scrape_data(url):
    engine = select_engine(url=url)
    if engine:
        engine = engine()
        try:
            data = engine.scrape_data(source_url = url)

        except Exception as err:
            raise err
        
        return data

def revise_item(ebay_url, ebay_setting):
    if ebay_url == '':
        return False
    
    if ebay_setting['app_id'] == "" or ebay_setting['cert_id'] == "" or ebay_setting['dev_id'] == "" or ebay_setting['ebay_token'] == "":
        return False
    
    item_number = ebay_url.split("/")[-1]

    try:
        api = Connection(appid = ebay_setting['app_id'], devid = ebay_setting['dev_id'], certid = ebay_setting['cert_id'], token = ebay_setting['ebay_token'], config_file=None)
        item = {
            'Item': {
                'ItemID': item_number.strip(),
                'Quantity': 0
            }
        }

        try:
            api.execute('ReviseItem', item)
            return True
        except:
            return False
    
    except:
        return False
    
def send_mail(FROM, PSW, TO, title, text):
    server = smtplib.SMTP(host="smtp.office365.com", port = 587)
    server.starttls()
    server.login(FROM, PSW)

    msg = MIMEMultipart("alternative")
    msg["From"] = FROM
    msg["To"] = TO
    msg["Subject"] = title

    text_part = MIMEText(text, "plain")
    msg.attach(text_part)
    
    server.sendmail(FROM, TO, msg.as_string())
    server.quit()

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'productmanage.settings')
    params = config()
     
    while True:
        with open(file=str(settings.BASE_DIR / 'utils/settings_attrs.txt'),  mode='r', encoding='utf-8') as f:
            settings_attrs = f.read()

        setting = json.loads(settings_attrs)

        FROM = setting['email_address']
        PSW = setting['psw']
        varience = setting['variable_price']

        try:
            conn = psycopg2.connect(
                database = params['db_name'],
                host = params['host'],
                user = params['user'],
                password = params['password'],
                port = params['port']
            )
            
            sql = "SELECT email, app_id, cert_id, dev_id, ebay_token FROM users_user WHERE is_superuser = TRUE"

            cur = conn.cursor()
            cur.execute(sql)
            row = cur.fetchone()

            TO = row[0]

            ebay_setting = {
                'app_id' : row[1],
                'cert_id' : row[2],
                'dev_id' : row[3],
                'ebay_token' : row[4]
            }

            sql = "SELECT * FROM product_product ORDER BY id ASC"

            cur = conn.cursor()
            cur.execute(sql)

            rows = cur.fetchall()


            for row in rows:
                url = row[5]
                ebay_url = row[6]
                price = int(row[7])

                if url == '':
                    continue
                
                data = scrape_data(url)                 

                if data['nothing']:
                    sql = "INSERT INTO product_deletedlist (created_at, updated_at, product_name, ec_site, purchase_url, ebay_url, purchase_price, sell_price_en, profit, profit_rate, prima, shipping, quantity, notes, created_by, deleted_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    val = (row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], datetime.datetime.now())

                    cur.execute(sql, val)
                    conn.commit()

                    # delete record
                    item_number = int(row[0])
                    sql = f"DELETE FROM product_product WHERE id = {item_number}"

                    cur.execute(sql)
                    conn.commit()

                    # set ebay product quantity 0
                    if ebay_url != '':
                        revise_item(ebay_url, ebay_setting)

                # check variance change
                purchase_price = int(data['purchase_price'])
                
                if price > 0 and abs(purchase_price - price) > int(varience):
                    title = "商品の価格変動！\n"
                    text = row[3] + "\n"
                    text += row[5] + "\n"
                    text += row[6]
                    
                    send_mail(FROM, PSW, TO, title, text)

            conn.close()

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        time.sleep(600)

if __name__ == '__main__':
    main()
