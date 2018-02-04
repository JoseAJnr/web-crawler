import requests
import json
from xml.etree import ElementTree
from bs4 import BeautifulSoup


def _handler_parag(tag):
    """
    Function to treat the 'p' tag
    :param bs4.element.Tag tag: The paragraph tag
    :return dict: A dictionary with 'text' type and content
    """
    if not tag.text.replace('\t', '').replace('\xa0', '').strip('\n'):
        return
    return dict(type='text', content=tag.text.replace('\t', '').replace('\xa0', '').strip('\n'))


def _handler_img(tag):
    """
    Function to treat the 'img' tag
    :param bs4.element.Tag tag: The image tag
    :return dict: A dictionary with 'image' type and image url
    """
    return dict(type='image', content=tag['src'])


def _handler_ul(tag):
    """
    Function to treat the 'ul' tag
    :param bs4.element.Tag tag: The unordered marker tag
    :return dict: A dictionary with 'links' type and a list with all links
    """
    result = dict(type='links', source=[])
    for link in tag.find_all('a'):
        result['source'].append(link['href'])

    return result


# Dictionary with functions having the tag.name as key and his handler as value
HANDLER_TAGS = {
    'p': _handler_parag,
    'img': _handler_img,
    'ul': _handler_ul
}


def _tag_to_dict(element):
    """
    Method to categorize the elements from description
    :param bs4.element.Tag element: The element tag that must have the info extracted
    :return dict: A dictionary with all info treated for that tag
    """
    if not element.name:
        return
    return HANDLER_TAGS.get(element.name)(element) if HANDLER_TAGS.get(element.name) else None


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

    # Transforming the text in a xml object and getting his root
    root = ElementTree.ElementTree(ElementTree.fromstring(feed_data.text)).getroot()

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
