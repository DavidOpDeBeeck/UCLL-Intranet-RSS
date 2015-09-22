import mechanize
import argparse
from datetime import datetime
from bs4 import BeautifulSoup
from xml.etree.ElementTree import Element, SubElement, tostring

parser = argparse.ArgumentParser()
parser.add_argument('-username', help='UCLL username')
parser.add_argument('-password', help='UCLL password')
args = parser.parse_args()

# Browser
br = mechanize.Browser()
cj = mechanize.CookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.addheaders = [('User-agent', 'Chrome')]

# Open redirect to https://idp.kuleuven.be/idp/view/login.htm
br.open('https://intranet.ucll.be/Shibboleth.sso/Login?target=https%3A%2F%2Fintranet.ucll.be%2F%3Fq%3Dshib_login%2Fhome')

# Find login form
br.select_form(nr=0)

# Fill in login details
br.form['username'] = args.username
br.form['password'] = args.password

# Submit the form
br.submit()

# Submit the javascript is disabled form
br.select_form(nr=0)
br.submit()

soup = BeautifulSoup(br.open('https://intranet.ucll.be/newsmessages').read(), "html.parser")
notices = soup.find('div', {'class': 'view-dringende-berichten-nieuwsberichten'}).find_all('h2')
notices_dates = soup.find_all('div', {'class': 'field--name-post-date'})

rss = Element('rss')
channel = SubElement(rss, 'channel')

channel_item_title = SubElement(channel, 'title')
channel_item_title.text = 'UCLL Nieuwsberichten'

channel_item_description = SubElement(channel, 'description')
channel_item_description.text = 'UC Leuven-Limburg : Nieuwsberichten'

channel_item_link = SubElement(channel, 'link')
channel_item_link.text = 'https://intranet.ucll.be/newsmessages'

channel_language = SubElement(channel, 'language')
channel_language.text = 'nl-be'

channel_generator = SubElement(channel, 'generator')
channel_generator.text = 'https://github.com/DavidOpDeBeeck/UCLL-Intranet-RSS'

channel_copyright = SubElement(channel, 'copyright')
channel_copyright.text = 'Copyright UCLL'

channel_publish_date = SubElement(channel, 'pubDate')
channel_publish_date.text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

channel_last_build_date = SubElement(channel, 'lastBuildDate')
channel_last_build_date.text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

for notice_index, notice in enumerate(notices):
    if notice.a is not None and notice.a.get('href') != "/newsmessages":
        link = 'https://intranet.ucll.be' + notice.a.get('href')

        channel_item = SubElement(channel, 'item')

        channel_item_title = SubElement(channel_item, 'title')
        channel_item_title.text = notice.a.text

        channel_item_link = SubElement(channel_item, 'link')
        channel_item_link.text = link

        soup = BeautifulSoup(br.open(link).read(), "html.parser")
        paragraphs = soup.find('article').find_all('p')
        author = soup.find('div', {'class': 'field--name-field-contact'}).a.text

        channel_item_description = SubElement(channel_item, 'link')
        channel_item_description.text = ''
        for paragraph in paragraphs:
            channel_item_description.text += str(paragraph).decode("utf8")

        publish_date = str(notices_dates[notice_index].find('div').find('div').text)[1:-1]
        channel_publish_date = SubElement(channel_item, 'pubDate')
        channel_publish_date.text = datetime.strptime(publish_date, '%d-%m-%Y').strftime("%a, %d %b %Y %H:%M:%S %z")

        channel_item_author = SubElement(channel_item, 'author')
        channel_item_author.text = author

rss_file = open("rss.xml", 'w')
rss_file.write(tostring(rss))
rss_file.close()
