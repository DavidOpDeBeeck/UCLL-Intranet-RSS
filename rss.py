import time
import argparse
import mechanize
from email import utils
from bs4 import BeautifulSoup
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring


def date_to_rfc822(date):
    """
        Converts a date to the RFC-822 standard
    """
    return utils.formatdate(time.mktime(date.timetuple()), True)

# Command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--username', type=str, help='UCLL username', required=True)
parser.add_argument('-p', '--password', type=str, help='UCLL password', required=True)
parser.add_argument('-o', '--output', type=str, help='Output file path', required=True)
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

# XML Elements
rss = Element('rss')
rss.set('version', '2.0')
channel = SubElement(rss, 'channel')

channel_title = SubElement(channel, 'title')
channel_title.text = 'UCLL Nieuwsberichten'

channel_description = SubElement(channel, 'description')
channel_description.text = 'UC Leuven-Limburg : Nieuwsberichten'

channel_link = SubElement(channel, 'link')
channel_link.text = 'https://intranet.ucll.be'

channel_language = SubElement(channel, 'language')
channel_language.text = 'nl-be'

channel_copyright = SubElement(channel, 'copyright')
channel_copyright.text = 'Copyright UC Leuven-Limburg'

channel_publish_date = SubElement(channel, 'pubDate')
channel_publish_date.text = date_to_rfc822(datetime.now())

channel_last_build_date = SubElement(channel, 'lastBuildDate')
channel_last_build_date.text = date_to_rfc822(datetime.now())

channel_generator = SubElement(channel, 'generator')
channel_generator.text = 'https://github.com/DavidOpDeBeeck/UCLL-Intranet-RSS'

channel_image = SubElement(channel, 'image')

channel_image_url = SubElement(channel_image, 'url')
channel_image_url.text = 'https://www.ucll.be/sites/all/themes/balance_theme/apple-touch-icon-precomposed-144x144.png'

channel_image_title = SubElement(channel_image, 'title')
channel_image_title.text = 'UCLL Nieuwsberichten'

channel_image_link = SubElement(channel_image, 'link')
channel_image_link.text = 'https://intranet.ucll.be'

channel_image_width = SubElement(channel_image, 'width')
channel_image_width.text = '144'

channel_image_height = SubElement(channel_image, 'height')
channel_image_height.text = '144'

# HTML identifiers
MESSAGES_URL = 'https://intranet.ucll.be/newsmessages'
MESSAGES_DIV_CLASS = 'view-dringende-berichten-nieuwsberichten'
MESSAGES_DATE_DIV_CLASS = 'field--name-post-date'

MESSAGE_PREFIX_URL = IMAGE_PREFIX = 'https://intranet.ucll.be'
MESSAGE_AUTHOR_CLASS = 'field--name-field-contact'
MESSAGE_ATTACHMENTS_CLASS = 'field--name-field-nieuws-bijlage'
MESSAGE_NEED_TO_KNOW_CLASS = 'field--name-field-nieuws-need-to-know'

PAGE_UL_CLASS = 'pager'
PAGE_LI_CLASS = 'pager__item'

# HTML parsing
messages_html = BeautifulSoup(br.open(MESSAGES_URL).read(), "html.parser")
pages_li = messages_html.find('ul', {'class': PAGE_UL_CLASS}).find_all('li', {'class': PAGE_LI_CLASS})

for page_element in enumerate(pages_li[:-2]):
    messages_html = BeautifulSoup(br.open(MESSAGES_URL + '?page=' + str(page_element[0])).read(), "html.parser")
    messages_h2 = messages_html.find('div', {'class': MESSAGES_DIV_CLASS}).find_all('h2')
    messages_date_div = messages_html.find_all('div', {'class': MESSAGES_DATE_DIV_CLASS})

    for messages_h2_index, message_h2_element in enumerate(messages_h2):
        if message_h2_element.a is not None:
            message_link = MESSAGE_PREFIX_URL + message_h2_element.a.get('href')
            message_html = BeautifulSoup(br.open(message_link).read(), "html.parser")
            message_publish_date = str(messages_date_div[messages_h2_index].find('div').find('div').text)[1:-1]
            message_paragraphs = message_html.find('article').find_all('p')
            message_author = message_html.find('div', {'class': MESSAGE_AUTHOR_CLASS}).a.text
            message_attachments = message_html.find('div', {'class': MESSAGE_ATTACHMENTS_CLASS})
            message_need_to_knows = message_html.find('div', {'class': MESSAGE_NEED_TO_KNOW_CLASS})

            channel_item = SubElement(channel, 'item')

            channel_item_title = SubElement(channel_item, 'title')
            channel_item_title.text = message_h2_element.a.text

            channel_item_link = SubElement(channel_item, 'link')
            channel_item_link.text = message_link

            channel_item_description = SubElement(channel_item, 'description')
            channel_item_description.text = ''

            for paragraph in message_paragraphs:
                channel_item_description.text += str(paragraph).decode("utf8")

            if message_attachments:
                channel_item_description.text += '<h3>Attachment</h3>'
                for attachment in message_attachments.find_all('span'):
                    attachment.find('img')['src'] = IMAGE_PREFIX + attachment.find('img')['src']
                    channel_item_description.text += str(attachment).decode("utf8")

            if message_need_to_knows and message_need_to_knows.find_all('p'):
                channel_item_description.text += '<h3>Need to know</h3>'
                for need_to_know in message_need_to_knows.find_all('p'):
                    channel_item_description.text += str(need_to_know).decode("utf8")

            channel_item_guid = SubElement(channel_item, 'guid')
            channel_item_guid.text = message_link

            channel_item_publish_date = SubElement(channel_item, 'pubDate')
            channel_item_publish_date.text = date_to_rfc822(datetime.strptime(message_publish_date, '%d-%m-%Y'))

            channel_item_author = SubElement(channel_item, 'author')
            channel_item_author.text = message_author

# Save XML to RSS file
rss_file = open(args.output, 'w')
rss_file.write(tostring(rss))
rss_file.close()

