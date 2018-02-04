import requests
import json
from xml.etree import ElementTree
from bs4 import BeautifulSoup


def _treat_parag(tag):
    if not tag.text.replace('\t', '').replace('\xa0', '').strip('\n'):
        return
    return dict(type='text', content=tag.text.replace('\t', '').replace('\xa0', '').strip('\n'))


def _treat_img(tag):
    return dict(type='image', content=tag['src'])


def _treat_ul(tag):
    result = dict(type='links', source=[])
    for link in tag.find_all('a'):
        result['source'].append(link['href'])

    return result


TREAT_TAGS = {
    'p': _treat_parag,
    'img': _treat_img,
    'ul': _treat_ul
}


def _tag_to_dict(element):
    """
    Method to categorize the elements from description
    :param bs4.element.Tag element: The element tag that must have the info extracted
    :return dict: A dictionary with all info treated
    """
    if not element.name:
        return
    return TREAT_TAGS.get(element.name)(element) if TREAT_TAGS.get(element.name) else None


def treat_description(description):
    """
    Method to get the description and return it's content
    :param str description: The HTML as a string
    :return list[dict]: A list of dictionaries with all tag content treated
    """
    result = list()
    desc_html = BeautifulSoup(description, 'html.parser')
    for tag in desc_html.find_all():
        type_dict = _tag_to_dict(tag)
        if type_dict:
            result.append(type_dict)

    return result


def main():
    # Making the request to the feed URL
    feed_data = requests.get('http://revistaautoesporte.globo.com/rss/ultimas/feed.xml')

    # Transforming the text in a xml object
    tree = ElementTree.ElementTree(ElementTree.fromstring(feed_data.text))

    # Getting XML root
    root = tree.getroot()

    # Initiating the result json
    final = {
        'feed': []
    }

    # Looping in items
    for item in root.iter('item'):
        final['feed'].append(dict(title=item.find('title').text,
                                  link=item.find('link').text,
                                  description=treat_description(item.find('description').text)))
    # Writing Json file
    with open('crawled.json', 'w') as final_file:
        json.dump(final, final_file, indent=4,  ensure_ascii=False)

if __name__ == '__main__':
    main()
