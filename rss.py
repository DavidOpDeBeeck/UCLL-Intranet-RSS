import time
import sys
import argparse
import mechanize
from email import utils
from bs4 import BeautifulSoup
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring

reload(sys)
sys.setdefaultencoding("utf8")


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
rss = Element('rss', version='2.0')

channel = SubElement(rss, 'channel')
channel_title = SubElement(channel, 'title')
channel_description = SubElement(channel, 'description')
channel_link = SubElement(channel, 'link')
channel_language = SubElement(channel, 'language')
channel_copyright = SubElement(channel, 'copyright')
channel_publish_date = SubElement(channel, 'pubDate')
channel_last_build_date = SubElement(channel, 'lastBuildDate')
channel_generator = SubElement(channel, 'generator')
channel_image = SubElement(channel, 'image')

channel_image_url = SubElement(channel_image, 'url')
channel_image_title = SubElement(channel_image, 'title')
channel_image_link = SubElement(channel_image, 'link')
channel_image_width = SubElement(channel_image, 'width')
channel_image_height = SubElement(channel_image, 'height')

channel_title.text = channel_image_title.text = 'UCLL Nieuwsberichten'
channel_description.text = 'UC Leuven-Limburg : Nieuwsberichten'
channel_link.text = channel_image_link.text = 'https://intranet.ucll.be'
channel_language.text = 'nl-be'
channel_copyright.text = 'Copyright UC Leuven-Limburg'
channel_publish_date.text = channel_last_build_date.text = date_to_rfc822(datetime.now())
channel_generator.text = 'https://github.com/DavidOpDeBeeck/UCLL-Intranet-RSS'
channel_image_url.text = 'https://www.ucll.be/sites/all/themes/balance_theme/apple-touch-icon-precomposed-144x144.png'
channel_image_width.text = channel_image_height.text = '144'

# HTML identifiers
messages_url = 'https://intranet.ucll.be/newsmessages'
messages_class = 'view-dringende-berichten-nieuwsberichten'
messages_date_class = 'field--name-post-date'

message_prefix_url = image_prefix_url = link_prefix_url = category_prefix_url = 'https://intranet.ucll.be'
message_author_class = 'field--name-field-contact'
message_description_class = 'field--type-text-with-summary'
message_description_item_class = 'field__item'
message_attachments_class = 'field--name-field-nieuws-bijlage'
message_ntk_class = 'field--name-field-nieuws-need-to-know'
message_category_class = 'field--name-field-tags'

page_list_class = 'pager'
page_item_class = 'pager__item'

# HTML parsing
page_html = BeautifulSoup(br.open(messages_url).read(), "html.parser")
page_items_html = page_html.find('ul', {'class': page_list_class}).find_all('li', {'class': page_item_class})

for page_element in enumerate(page_items_html[:-2]):  # Remove 'volgende' and 'last' from the page items
    page_html = BeautifulSoup(br.open(messages_url + '?page=' + str(page_element[0])).read(), "html.parser")
    messages_h2 = page_html.find('div', {'class': messages_class}).find_all('h2')
    messages_date_div = page_html.find_all('div', {'class': messages_date_class})

    for messages_h2_index, message_h2_element in enumerate(messages_h2):
        if message_h2_element.a is not None:
            message_url = message_prefix_url + message_h2_element.a.get('href')
            message_html = BeautifulSoup(br.open(message_url).read(), "html.parser")
            message_publish_date = str(messages_date_div[messages_h2_index].find('div').find('div').text)[1:-1]
            message_description = message_html.find(
                'div', {'class': message_description_class}).find_all(
                'div', {'class': message_description_item_class})
            message_author = message_html.find('div', {'class': message_author_class}).a.text
            message_attachments = message_html.find('div', {'class': message_attachments_class})
            message_need_to_knows = message_html.find('div', {'class': message_ntk_class})
            message_categories = message_html.find('div', {'class': message_category_class})

            channel_item = SubElement(channel, 'item')
            channel_item_title = SubElement(channel_item, 'title')
            channel_item_link = SubElement(channel_item, 'link')
            channel_item_description = SubElement(channel_item, 'description')
            channel_item_guid = SubElement(channel_item, 'guid')
            channel_item_publish_date = SubElement(channel_item, 'pubDate')
            channel_item_author = SubElement(channel_item, 'author')

            channel_item_title.text = message_h2_element.a.text
            channel_item_link.text = channel_item_guid.text = message_url
            channel_item_description.text = ''
            channel_item_publish_date.text = date_to_rfc822(datetime.strptime(message_publish_date, '%d-%m-%Y'))
            channel_item_author.text = message_author

            for message_description_item in message_description:
                for message_description_text in message_description_item.find_all():
                    message_description_links = message_description_text.find_all('a')
                    for message_description_link in message_description_links:  # If link is relative add prefix
                        if message_description_link and message_description_link['href'][0] == '/':
                            message_description_link['href'] = link_prefix_url + message_description_link['href']
                    channel_item_description.text += str(message_description_text).decode("utf8")

            if message_attachments:  # Only add attachments if found
                channel_item_description.text += '<h3>Attachment</h3>'
                for attachment in message_attachments.find_all('span'):
                    attachment.find('img')['src'] = image_prefix_url + attachment.find('img')['src']
                    channel_item_description.text += str(attachment).decode("utf8")

            if message_need_to_knows and message_need_to_knows.find_all('p'):  # Only add 'Need to know' if found
                channel_item_description.text += '<h3>Need to know</h3>'
                for need_to_know in message_need_to_knows.find_all('p'):
                    channel_item_description.text += str(need_to_know).decode("utf8")

            if message_categories and message_categories.find_all('a'):  # Only add categories if found
                for message_category in message_categories.find_all('a'):
                    channel_item_category = SubElement(channel_item, 'category',
                                                       domain=category_prefix_url + message_category['href'])
                    channel_item_category.text = message_category.text

output_file = open(args.output, 'w')
output_file.write(tostring(rss))
output_file.close()

