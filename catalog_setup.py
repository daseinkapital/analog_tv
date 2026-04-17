import os
import shutil
import csv
import json
import re
import logging
import sys
import argparse

media_dir = '/home/andrew/Shared/'
mnt_dir_tv = media_dir + 'tv'
mnt_dir_movies = media_dir + 'movies'
mnt_dir_commercials = media_dir + 'commercials'
mnt_dir_bumps = media_dir + 'bumps'
holiday_tv_file = './plex_holiday_shows.csv'
holiday_movie_file = './plex_holiday_movies.csv'
fieldstore_catalog_path = './FieldStation42/catalog'
fieldstore_confs_path = './FieldStation42/confs'

other_paths = {
    'jazzercise': media_dir + 'jazzercise',
    'mtv': media_dir + 'music_videos',
    'slow_tv': media_dir + 'slow_tv',
    'home': media_dir + 'personal/Video/Hi-8 clips'
}

supported_formats = ["mp4", "mpg", "mpeg", "avi", "mov", "mkv", "ts", "m4v", "webm", "wmv"]

def build_parser():
    parser = argparse.ArgumentParser(
        description="Catalog setup settings"
    )

    parser.add_argument(
        "-c",
        "--channel",
        nargs="*",
        help="Specific channel to rerun",
    )

    parser.add_argument(
        "-r",
        "--remove",
        action="store_true",
        help="Remove broken symlinks",
    )

    parser.add_argument(
        "-u",
        "--update-confs",
        help="Replace current conf",
    )

    return parser



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
    build_dir = ''
    for partial_dir in directory.split('/'):
        build_dir += partial_dir + '/'
        if not os.path.exists(build_dir):
            os.mkdir(build_dir)

def make_symlink_if_not_exists(src, trg):
    if not os.path.islink(trg):
        if not os.path.exists(trg):
            print(f"Creating symlink to {trg}")
            os.symlink(src, trg)

holiday_tv_shows = grab_holiday_specials()

def establish_ppv_simlink(channel_path):
    for movie in os.listdir(mnt_dir_movies):
        for s in os.listdir(f"{mnt_dir_movies}/{movie}"): # open the folder
            for filetype in supported_formats:
                if s.endswith('.' + filetype):
                    make_symlink_if_not_exists(f"{mnt_dir_movies}/{movie}/{s}", f"{channel_path}/{s}")



def parse_episode(episode_name):
    exp = r'S(\d+)\s?E(\d+)'
    match = re.search(exp, episode_name)
    if match:
        return int(match.group(1)), int(match.group(2))
    else:
        return None, None

def recurse_tagging(contents, curr_dir, first_level=False):
    for tag, val in contents.items():
        next_dir = f"{curr_dir}/{tag}"
        make_dir_if_not_exists(next_dir)
        if first_level: # only run on the first level
            if tag == 'commercials' or tag == 'bump': # if it's commercial or bumps, hanlde appropriately
                mnt_dir = mnt_dir_bumps if tag == "bump" else mnt_dir_commercials
                for folder in val:
                    if '/' in folder:
                        make_dir_if_not_exists(f"{next_dir}/{'/'.join(folder.split('/')[:-1])}") # allows for greater subfolder specifications
                    make_symlink_if_not_exists(f"{mnt_dir}/{folder}", f"{next_dir}/{folder}")
                continue
        if type(val) == list: # if it's a list of things, locate them and make the symlink
            for media_name in val:
                symlink_files(media_name, curr_dir.split('/')[-1], next_dir, media_type="tv" if "/tv" in next_dir else "movie")
        elif type(val) == dict: # if the next goes deeper, make the dir then recurse
            recurse_tagging(val, next_dir)
    return

def symlink_files(media_name, channel_name, curr_dir, media_type="tv"):
    found = False
    if media_type == "tv":
        for show in os.listdir(mnt_dir_tv): # loop through all our tv
            if show.capitalize().startswith(media_name.capitalize()): # see if we find the folder
                found = True # mark folder as found
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
                                        make_dir_if_not_exists(f"{curr_dir}/{holiday_tv_shows[holiday_name]}")
                                        make_dir_if_not_exists(f"{curr_dir}/{holiday_tv_shows[holiday_name]}/{media_name}")
                                        make_symlink_if_not_exists(f"{mnt_dir_tv}/{show}/{s}/{e}", f"{curr_dir}/{holiday_tv_shows[holiday_name]}/{media_name}/{e}")
                                        continue
                                # print("Make symlink for ", e)
                                make_symlink_if_not_exists(f"{mnt_dir_tv}/{show}/{s}/{e}", f"{curr_dir}/{media_name}/{e}")
                                pass
                break
    elif media_type == 'movie':
        for movie in os.listdir(mnt_dir_movies): # loop through all our movies
            if movie.capitalize().startswith(media_name.capitalize()): # see if we find the folder
                found = True # mark folder as found
                make_dir_if_not_exists(f"{curr_dir}/{media_name}")
                for s in os.listdir(f"{mnt_dir_movies}/{movie}"): # open the folder
                    for filetype in supported_formats:
                        if s.endswith('.' + filetype):
                            make_symlink_if_not_exists(f"{mnt_dir_movies}/{movie}/{s}", f"{curr_dir}/{media_name}/{s}")
                            break
    if not found:
        print("Could not find directory for media ", media_name)

def check_items_in_path_folder_or_file(path):
    for item in os.listdir(path):
        if os.path.isdir(path + '/' + item):
            check_items_in_path_folder_or_file(path + '/' + item)
        if os.path.islink(path + '/' + item) and not os.path.exists(path + '/' + item):
            os.unlink(path + '/' + item)

def recurse_adding_media(channel_path, src):
    for item in os.listdir(src):
        if os.path.isdir(f"{src}/{item}"):
            recurse_adding_media(channel_path, f"{src}/{item}")
        elif os.path.isfile(f"{src}/{item}"):
            filetype = item.split('.')[-1]
            if filetype in supported_formats:
                make_symlink_if_not_exists(f"{src}/{item}", f"{channel_path}/{item}")

def add_misc_videos(channel_name, channel_path):
    make_dir_if_not_exists(f"{channel_path}/commercials")
    make_dir_if_not_exists(f"{channel_path}/bumps")
    if channel_name == 'mtv':
        recurse_adding_media(f"{channel_path}/commercials", f"{mnt_dir_commercials}/channels/mtv")
        recurse_adding_media(f"{channel_path}/bumps", f"{mnt_dir_bumps}/mtv")
    make_dir_if_not_exists(f"{channel_path}/{channel_name}")
    recurse_adding_media(f"{channel_path}/{channel_name}", other_paths[channel_name])

def process_seasonal():
    channel_path = f"{fieldstore_catalog_path}/seasonal"
    holiday_shows = grab_holiday_specials()
    for key, month in holiday_shows.items():
        # Parse key: "Show S{season}E{episode}"
        parts = key.rsplit(' S', 1)
        show_name = parts[0]
        se_part = parts[1]  # "1E2" for S1E2
        season_str, ep_str = se_part.split('E')
        season = int(season_str)
        ep = int(ep_str)
        
        # Find show folder
        show_folder = None
        for folder in os.listdir(mnt_dir_tv):
            if folder.lower().startswith(show_name.lower()):
                show_folder = folder
                break
        if not show_folder:
            print(f"Could not find folder for show {show_name}")
            continue
        
        # Look for the episode
        found = False
        for s in os.listdir(f"{mnt_dir_tv}/{show_folder}"):
            season_path = f"{mnt_dir_tv}/{show_folder}/{s}"
            if os.path.isdir(season_path):
                for e in os.listdir(season_path):
                    if os.path.isfile(f"{season_path}/{e}"):
                        if e.endswith(".srt") or e == '.DS_Store':
                            continue
                        file_season, file_ep = parse_episode(e)
                        if file_season == season and file_ep == ep:
                            # Found the episode
                            make_dir_if_not_exists(f"{channel_path}/{month}")
                            make_dir_if_not_exists(f"{channel_path}/{month}/{show_name}")
                            make_symlink_if_not_exists(f"{season_path}/{e}", f"{channel_path}/{month}/{show_name}/{e}")
                            found = True
                            break
                if found:
                    break
        if not found:
            print(f"Could not find episode S{season}E{ep} for {show_name}")


def process_channel(channel_name):
    channel_path = f"{fieldstore_catalog_path}/{channel_name}"
    if not os.path.exists(channel_path):
        os.mkdir(channel_path)
    if channel_name == "ppv":
        establish_ppv_simlink(channel_path)
        return
    elif channel_name in ["mtv", "slow_tv", "jazzercise", "home"]:
        add_misc_videos(channel_name, channel_path)
        return
    if channel_name == "seasonal":
        process_seasonal()
    with open(f"channels/{channel_name}.json") as f:
        contents = json.load(f)
        print(channel)
        recurse_tagging(contents, channel_path, first_level=True)

def replace_conf(name):
    for conf in os.listdir('./confs'):
        if name in conf:
            shutil.copy(f"./confs/{conf}", f"{fieldstore_confs_path}/{conf}")


parser = build_parser()
args = parser.parse_args()

if args.remove:
    #clean up all symlinks that may have broken (either deleted or filename change)
    for channel in os.listdir(fieldstore_catalog_path):
        print(channel)
        check_items_in_path_folder_or_file(f"{fieldstore_catalog_path}/{channel}")

if args.channel:
    channel = args.channel[0]
    process_channel(channel)
    if args.update_confs:
        replace_conf(channel)

else:
    for channel in os.listdir('channels'):
        channel_name, _ = os.path.splitext(channel)
        print(channel_name)
        process_channel(channel_name)

        if args.update_confs:
            replace_conf(channel_name)