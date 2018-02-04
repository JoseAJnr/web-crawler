import requests
import json
import argparse
from xml.etree import ElementTree
from bs4 import BeautifulSoup


def treat_description(description):
    """
    Method to get the description and return it's content
    :param str description: The HTML as a string
    :return list[dict]: A list of dictionaries with all tag content treated
    """
    result = list()
    links_dict = dict(type='links', content=[])
    desc_html = BeautifulSoup(description, 'html.parser')
    for tag in desc_html.find_all():
        type_dict = _tag_to_dict(tag)
        if type_dict:
            if tag.name != 'a':
                result.append(type_dict)
            else:
                links_dict['content'].append(type_dict)

    result.append(links_dict)

    return result


def _tag_to_dict(element):
    """
    Method to categorize the elements from description
    :param bs4.element.Tag element: The element tag that must have the info extracted
    :return dict: A dictionary with all info treated
    """
    if element.name == 'a':
        result = element['href']
    elif element.name == 'img':
        result = dict(type='image', content=element['src'])
    # Eliminating lines without content
    elif element.name == 'p' and element.text.replace('\t', '').replace('\xa0', '').strip('\n'):
        result = dict(type='text', content=element.text.replace('\t', '').replace('\xa0', '').strip('\n'))
    else:
        return
    return result


def main():
    # Making the request to the feed URL
    data = requests.get('http://revistaautoesporte.globo.com/rss/ultimas/feed.xml')

    # Transforming the text in a xml object
    tree = ElementTree.ElementTree(ElementTree.fromstring(data.text))

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
