import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import csv
from pprint import pprint
import ssl
import numpy as np
import os
import email, smtplib, ssl
import os
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import time

print("This program does not support polish characters in file's name.")
if not os.path.exists('files_to_sent'):
    os.mkdir('files_to_sent')
    print("Directory " , 'files_to_sent' ,  " Created ")

if not os.path.exists('sended'):
    os.mkdir('sended')
    print("Directory " , 'sended' ,  " Created ")

'''Type your mails and password'''
sender_email = 'mymail@mail.mail'
receiver_email = 'my_mail@kindle.com'
password = 'my_password'

# to avoid ssl errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url='https://www.rmf24.pl/fakty'

page = requests.get(url)

# pprint(page.text)

# make soup
soup = BeautifulSoup(page.text, 'html.parser')
# pprint(soup)

# find all links on the page
links = np.array([])
for link in soup.find_all('a'):
    # print(link.get('href'))
    links = np.append(links, link.get('href'))


correct_links = np.array([])
for link in links:
    if link.startswith('/raporty/raport') or link.startswith('/fakty/'): # take only news
        link =  'https://www.rmf24.pl' + link
        correct_links = np.append(correct_links, link)

correct_links = np.array(list(set(correct_links)))
# print(correct_links[0])
# test_page = requests.get(correct_links[0])
# print(test_page.text)

# page_content = []
# page_links = []

# dict to store links and their content
pages = {}
# page_soup = BeautifulSoup(test_page.content, 'html.parser')
# pprint(page_soup)

for correct_link in correct_links:
    # print('\n')
    # print(correct_link)
    test_page = requests.get(correct_link)
    page_soup = BeautifulSoup(test_page.content, 'html.parser')
    # page_links.append(correct_link)

    current_content = []
    for content in page_soup.find_all('p'):
        current_content.append(content.get_text())
        # page_content.append(content.get_text())
        # print(content.get_text())
    pages[correct_link] = current_content



# for link, content in pages.items():
#     print('\n')
#     print(link)
#     for c in content:
#         print(c)


'''Sent to kindle part'''
current_date = datetime.date.today()

with open(f"files_to_sent/RMF_{current_date}.txt", "w", encoding="utf-8") as f:   # Opens file and casts as f
    for link, content in pages.items():
        f.write('\n')
        f.write('\n')
        f.write('\n')
        f.write(link)
        f.write('\n')
        for c in content:
            f.write('\n')
            f.write(c)
    # Writing
    # File closed automatically

'''
    For the given path, get the List of all files in the directory tree
'''
from os import listdir
from os.path import isfile, join
onlyfiles = [f for f in listdir('files_to_sent') if isfile(join('files_to_sent', f))]

# filename_path = "files_to_sent/test.txt"  # In same directory as script
# filename = 'test.txt'

print(onlyfiles)

files = []

for file in onlyfiles:
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email

    # Open PDF file in binary mode
    with open('files_to_sent/{}'.format(file), "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {file}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)

    os.replace('files_to_sent/{}'.format(file), 'sended/{}'.format(file))

print('Files send.')
time.sleep(10)



