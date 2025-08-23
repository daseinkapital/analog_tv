import os
import csv
import json
import re

mnt_dir_tv = '/Volumes/tv'
mnt_dir_movies = '/Volumes/movies'
holiday_tv_file = './plex_holiday_shows.csv'
holiday_movie_file = './plex_holiday_movies.csv'
fieldstore_catalog_path = './FieldStation42/catalog/'

def grab_holiday_specials(media_type='tv'):
    if media_type == 'tv':
        with open(holiday_tv_file) as f:
            file = csv.DictReader(f)
            rows = list(file)
            show_map = {}
            for row in rows:
                key = f"{row['Show']} S{row['S']}E{row['E']}"
                show_map[key] =  row['Month']
    return show_map


holiday_tv_shows = grab_holiday_specials()

def parse_episode(episode_name):
    exp = r'S(\d{2})E(\d{2})'
    match = re.match(exp, episode_name)
    if match:
        return int(match.group(1)), int(match.group(2))
    else:
        return

def symlink_files(media_name, media_type="tv"):
    found = False
    if media_type == "tv":
        for dir in os.listdir(mnt_dir_tv):
            if dir.capitalize().startswith(media_name.capitalize()):
                found = True
                print("Linking ", dir)
                for s in os.listdir(f"{mnt_dir_tv}/{dir}"):
                    if os.path.isdir(f"{mnt_dir_tv}/{dir}/{s}"):
                        for e in os.listdir(f"{mnt_dir_tv}/{dir}/{s}"):
                            if os.path.isfile(f"{mnt_dir_tv}/{dir}/{s}/{e}"):
                                # print("Making symlink for ", e)
                                pass
                break
    if not found:
        print("Could not find directory for media ", media_name)

for channel in os.listdir('channels'):
    channel_name, _ = os.path.splitext(channel)
    with open(f"channels/{channel}") as f:
        contents = json.load(f)
    for k,v in contents.items():
        print(f"Making dir for at ./FieldStation42/catalog/{channel_name}/{k}")
        if type(v) == list:
            for item in v:
                print("Copying directory", item)
        elif type(v) == dict:
            for k1,v1 in v.items():
                print(f"Making dir for ./FieldStation42/catalog/{channel_name}/{k}/{k1}")
                for media in v1:
                    print(f"Making dir for ./FieldStation42/catalog/{channel_name}/{k}/{k1}/{media}")
                    symlink_files(media, k1)