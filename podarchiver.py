import requests
import bs4
import os
import json


# User files
feeds_file = 'feeds.txt'
archive_file = 'archive.log'

# Function to read the feed list file into an array
def read_feeds(feeds_file):

    with open(feeds_file, 'r') as f:
        feeds = f.read().splitlines()

    return feeds

# Function to request the XML data for a given feed
def get_feedxml(url):

    response = requests.request("GET", url)
    xml = bs4.BeautifulSoup(response.text, "xml")
    xml.prettify()
    
    return xml
    
# Function to get Podcast series information
def get_channeldata(xml):

    title = xml.title.string  # Podcast title
    link = xml.link.string  # Podcast link URL
    summary = xml.find('itunes:summary').string.split('\n')[0]  # Summary text 
    image_url = xml.find('itunes:image')['href']  # Podcast image url
    
    channel_data = {'title': title,
                    'link': link,
                    'summary': summary,
                    'image_url': image_url
                    }

    return channel_data
    
# Function to pull initial Podcast series data and setup directories for
# archiving episodes and data
def initial_setup(xml):

    channel_data = get_channeldata(xml)
    episode_path = 'Podcasts/' + channel_data['title']
    ensure_dir(episode_path)
    
    json_file = episode_path + '/' + channel_data['title'] + '.json'
    if not os.path.exists(json_file):
        with open(json_file, 'w') as file:
            json.dump(channel_data, file, indent=4)
    
    return channel_data['title'], episode_path
    
# Function to ensure series archive directory exists
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    return

# Read podcast feeds from the file
feeds = read_feeds(feeds_file)

for feed in feeds:
    xml = get_feedxml(feed)
    title, path = initial_setup(xml)

#print(soup.find_all('item'))
#print(soup)
