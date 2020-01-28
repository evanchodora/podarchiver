#!/usr/bin/env python3

import urllib.request
import requests
import bs4
import os
import json
from datetime import datetime


# Python script to download and archive podcast feeds.
#
# Reads feeds from lines of a `feeds.txt` file. Downloads episode cover art, 
# description information, and MP3 files in organized directories. An 
# archive.log tracks the downloaded episode GUIDs so it will skip already 
# archived episodes when the script is run again.
#
# Evan Chodora, 2020
# https://github.com/evanchodora/podarchiver

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

    # Get and store information about the series
    channel_data = get_channeldata(xml)
    episode_path = 'Podcasts/' + channel_data['title']
    ensure_dir(episode_path)
    open('archive.log', 'a').close()  # Make sure the archive log exists
    
    # Write series information to a file
    json_file = episode_path + '/' + channel_data['title'] + '.json'
    if not os.path.exists(json_file):
        with open(json_file, 'w') as file:
            json.dump(channel_data, file, indent=4)
    
    return channel_data['title'], episode_path
    
def archive_episodes(title, path, xml):

    # Create an array of episode data
    episodes = xml.find_all('item')
    
    # Number of available episodes
    number = str(len(episodes))
    
    print(title + ': ' + 'found ' + number + ' episodes...')
    
    # Loop through each episode
    for i, episode in enumerate(episodes):
        ep_title = episode.title.string
        try:
            ep_num = episode.find('itunes:episode').string
        except:
            ep_num = ''
        try:    
            ep_link = episode.link.string
        except:
            ep_link = ''
        ep_file = episode.enclosure['url']
        ep_guid = episode.guid.string
        
        ep_date = episode.pubDate.string
        date_format = '%a, %d %b %Y %H:%M:%S %z'
        ep_date = datetime.strptime(ep_date, date_format)
        ep_date = ep_date.strftime('%Y%m%d')
        
        ep_image = episode.find('itunes:image')['href']
        ep_dur = episode.find('itunes:duration').string
        
        # Find the best location for this episode summary:
        ep_summary = episode.find('itunes:summary').string
        
        # Store episode data dictionary
        ep = {'title': ep_title,
              'num': ep_num,
              'link': ep_link,
              'file': ep_file,
              'guid': ep_guid,
              'date': ep_date,
              'image': ep_image,
              'duration': ep_dur,
              'summary': ep_summary
              }
        
        # Status line
        status = ' [' + str(i+1) + '/' + number + ']'
        status = title + ' - ' + ep['title'] + status
        
        # Build root file name
        root_name = path + '/' + title + '_' + ep['date'] + '_' + ep['title']
        
        # Check archive log file if episode already downloaded
        with open('archive.log', 'r') as f:
            if ep['guid'] in f.read():
                print('Skipping: ' + status)
            else:
                print('Downloading: ' + status)
                downloader(title, path, ep, root_name)
        
                # Write episode data file
                json_file = root_name + '.data'
                if not os.path.exists(json_file):
                    with open(json_file, 'w') as file:
                        json.dump(ep, file, indent=4)
                        
                # Add GUID to the archive log
                with open('archive.log', 'a') as file:
                    file.write(ep['guid'] + '\n')
    
    return
    
# Function to download the episode MP3 and cover art
def downloader(title, path, ep, root_name):

    # Cover art
    image_url = ep['image']
    image_name = root_name + '.jpg'
    
    # MP3 file
    ep_url = ep['file']
    ep_name = root_name + '.mp3'
    
    # Download the files using urllib
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]  # Set user-agent
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(image_url, image_name)  # Download cover art
    urllib.request.urlretrieve(ep_url, ep_name)  # Download MP3 file

    return
    
# Function to ensure series archive directory exists
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    return


# Read podcast feeds from the file
feeds = read_feeds(feeds_file)

# Loop through podcast feeds and begin archiving
for feed in feeds:
    xml = get_feedxml(feed)
    title, path = initial_setup(xml)
    archive_episodes(title, path, xml)


