import os
import csv
import json
import re

media_dir = '/media/andrew/Russell/Media/'
mnt_dir_tv = media_dir + 'TV'
mnt_dir_movies = media_dir + 'Movies'
mnt_dir_commercials = media_dir + 'commercials'
mnt_dir_bumps = media_dir + 'bumps'
holiday_tv_file = './plex_holiday_shows.csv'
holiday_movie_file = './plex_holiday_movies.csv'
fieldstore_catalog_path = './FieldStation42/catalog'

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

def make_dir_if_not_exists(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)

def make_symlink_if_not_exists(src, trg):
    if not os.path.exists(trg):
        os.symlink(src, trg)

holiday_tv_shows = grab_holiday_specials()

def parse_episode(episode_name):
    exp = r'S(\d+)\s?E(\d+)'
    match = re.search(exp, episode_name)
    if match:
        return int(match.group(1)), int(match.group(2))
    else:
        return None, None

def recurse_tagging(contents, curr_dir, first_level=False):
    for tag, val in contents.items():
        print("Tag", tag)
        print("Val", val)
        next_dir = f"{curr_dir}/{tag}"
        make_dir_if_not_exists(next_dir)
        if first_level: # only run on the first level
            if tag == 'commercials' or tag == 'bump': # if it's commercial or bumps, hanlde appropriately
                mnt_dir = mnt_dir_bumps if tag == "bump" else mnt_dir_commercials
                for folder in val:
                    make_symlink_if_not_exists(f"{mnt_dir}/{folder}", f"{next_dir}/{folder}")
                continue
        if type(val) == list: # if it's a list of things, locate them and make the symlink
            for media_name in val:
                symlink_files(media_name, channel_name, next_dir, media_type="tv" if "/tv" in next_dir else "movie")
        elif type(val) == dict: # if the next goes deeper, make the dir then recurse
            recurse_tagging(val, next_dir)
    return

def symlink_files(media_name, channel_name, curr_dir, media_type="tv"):
    found = False
    if media_type == "tv":
        print("Current dir", curr_dir)
        for show in os.listdir(mnt_dir_tv): # loop through all our tv
            if show.capitalize().startswith(media_name.capitalize()): # see if we find the folder
                found = True # mark folder as found
                print("Linking ", show)
                make_dir_if_not_exists(f"{curr_dir}/{media_name}")
                for s in os.listdir(f"{mnt_dir_tv}/{show}"): # open the folder
                    if os.path.isdir(f"{mnt_dir_tv}/{show}/{s}"): # ensure object is folder
                        for e in os.listdir(f"{mnt_dir_tv}/{show}/{s}"): # loop through objs in seasons folder
                            if os.path.isfile(f"{mnt_dir_tv}/{show}/{s}/{e}"): # ensure objs in seasons are files (episodes)
                                if e.endswith(".srt") or e == '.DS_Store': # if it's a subtitle file or if it's the .DS_Store,  ignore
                                    continue
                                season, ep = parse_episode(e) # attempt to parse the season/episode
                                if season and ep: # if we found a season/ep
                                    holiday_name = f"{media_name} S{season}E{ep}" # create a naming convention
                                    # print("Holiday Name", holiday_name)
                                    if holiday_name in holiday_tv_shows: # check if holiday episode
                                        print("Found holiday episode", holiday_name) # tell user we got a holiday episode
                                        make_dir_if_not_exists(f"{curr_dir}/{holiday_tv_shows[holiday_name]}")
                                        make_dir_if_not_exists(f"{curr_dir}/{holiday_tv_shows[holiday_name]}/{media_name}")
                                        make_symlink_if_not_exists(f"{mnt_dir_tv}/{show}/{s}/{e}", f"{curr_dir}/{holiday_tv_shows[holiday_name]}/{media_name}/{e}")
                                        continue
                                # print("Make symlink for ", e)
                                make_symlink_if_not_exists(f"{mnt_dir_tv}/{show}/{s}/{e}", f"{curr_dir}/{media_name}/{e}")
                                pass
                break
    if not found:
        print("Could not find directory for media ", media_name)

for channel in os.listdir('channels'):
    channel_name, _ = os.path.splitext(channel)
    channel_path = f"{fieldstore_catalog_path}/{channel_name}"
    if not os.path.exists(channel_path):
        os.mkdir(channel_path)
    with open(f"channels/{channel}") as f:
        contents = json.load(f)
        recurse_tagging(contents, channel_path, first_level=True)
        
        
        
        
        # if not os.path.exists(f"./FieldStation42/catalog/{channel_name}/{init_tag}"):
        #     print(f"Making dir for at ./FieldStation42/catalog/{channel_name}/{init_tag}")
        #     os.mkdir(f"./FieldStation42/catalog/{channel_name}/{init_tag}")
        # if init_tag == "commercials":
            
        # if type(v) == list:
        #     for item in v:
        #         print("Copying directory", item)
        # elif type(v) == dict:
        #     for k1,v1 in v.items():
        #         if os.path.exists(f'./FieldStation42/catalog/{channel_name}/{k}/{k1}'):
        #             print("Skipping making path")
        #         else:
        #             print(f"Making dir for ./FieldStation42/catalog/{channel_name}/{k}/{k1}")
        #             os.mkdir(f'./FieldStation42/catalog/{channel_name}/{k}/{k1}')
        #         for media in v1:
        #             if os.path.exists(f"./FieldStation42/catalog/{channel_name}/{k}/{k1}/{media}"):
        #                 print(f"Skipping making folder for {media}")
        #             else:
        #                 print(f"Making dir for ./FieldStation42/catalog/{channel_name}/{k}/{k1}/{media}")
        #                 os.mkdir(f"./FieldStation42/catalog/{channel_name}/{k}/{k1}/{media}")
        #             symlink_files(media, channel_name, k, title=media, media_type=k1)