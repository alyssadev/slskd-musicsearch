#!/usr/bin/env python3
import musicbrainzngs
from slskd_api import SlskdClient

from requests import get, post
from time import sleep
from os import environ

musicbrainzngs.set_useragent("slskd-musicsearch", "0.1", "https://github.com/alyssadev/slskd-musicsearch")
slskd = SlskdClient(environ.get("SLSKD_HOST","http://localhost:5030"), environ.get("SLSKD_KEY",""))

lidarr = environ.get("LIDARR_HOST","http://localhost:8686"), environ.get("LIDARR_KEY","")

def print_json(d):
    from json import dumps
    print(dumps(d,indent=4))

def get_album(release_id):
    result = musicbrainzngs.get_release_by_id(release_id, includes=["artists", "recordings", "recording-level-rels", "work-rels", "work-level-rels"])["release"]
    tracks = []
    for medium in result["medium-list"]:
        for track in medium["track-list"]:
            tracks.append({
                "title": track["recording"]["title"],
                "alttitle": track["recording"].get("work-relation-list",[{}])[0].get("work",{}).get("title"),
                "length": track["length"]
                })
    return {
            "title": result["title"],
            "artist": result["artist-credit-phrase"],
            "tracks": tracks
           }

def san(inp):
    return inp.replace("\u2019","").replace(",","").replace("'","") if inp else None

def search(album):
    search = None
    query = f"{album['artist']} - {album['title']} flac"
    previous_searches = slskd.searches.get_all()
    for s in previous_searches:
        if s["searchText"] == query:
            # print(query, s)
            search = s
    if not search:
        search = slskd.searches.search_text(f"{album['artist']} - {album['title']} flac")
        try:
            while not slskd.searches.state(search["id"])["isComplete"]:
                sleep(0.5)
        except KeyboardInterrupt:
            pass
    results = slskd.searches.search_responses(search["id"])
    lookup = []
    for result in results:
        track_names = {n:(san(track["title"]),san(track["alttitle"])) for n,track in enumerate(album["tracks"])}
        # print_json(track_names)
        matches = 0
        resp = {"username": result["username"], "files": []}
        for f in result["files"]:
            fn = (f["filename"].split("\\")[-1])
            # print(fn)
            _track_names = dict(track_names)
            for n,title in _track_names.items():
                if f"{title[0]}.flac" in fn or (f"{title[1]}.flac" in fn if title[1] else False):
                    del track_names[n]
                    resp["files"].append(f)
                    matches += 1
            if not track_names:
                break
        if matches == len([track["title"] for track in album["tracks"]]):
            print(resp)
            slskd.transfers.enqueue(**resp)
            #slskd.searches.delete(search["id"])
            return True
        if not matches:
            continue
        resp["matches"] = matches
        lookup.append(resp)
    return search["id"]

def lidarr_get(endpoint, *args, **kwargs):
    if not "headers" in kwargs:
        kwargs["headers"] = {}
    kwargs["headers"]["X-Api-Key"] = lidarr[1]
    return get(lidarr[0] + endpoint, *args, **kwargs).json()

def lidarr_post(endpoint, *args, **kwargs):
    if not "headers" in kwargs:
        kwargs["headers"] = {}
    kwargs["headers"]["X-Api-Key"] = lidarr[1]
    return post(lidarr[0] + endpoint, *args, **kwargs).json()

def lidarr_get_root_folder(index: int=0):
    root_folder = lidarr_get("/api/v1/rootFolder")
    if type(root_folder) is list:
        root_folder = root_folder[index]
    return root_folder

def add_album_to_lidarr(release_id, root_folder_index: int=0):
    release_group_id = musicbrainzngs.get_release_by_id(release_id,includes=["release-groups"])["release"]["release-group"]["id"]
    lidarr_search = lidarr_get("/api/v1/search", params={"term": f"lidarr:{release_group_id}"})
    lidarr_album = lidarr_search[0]["album"]
    lidarr_album["monitored"] = True
    lidarr_album["addOptions"] = {"searchForNewAlbum": False}
    lidarr_album["artist"]["monitored"] = True
    lidarr_album["artist"]["addOptions"] = {"monitor": "missing", "searchForMissingAlbums": False}
    print_json(lidarr_album)
    root_folder = lidarr_get_root_folder(root_folder_index)
    print_json(root_folder)
    # bring in values configured on root folder
    lidarr_album["artist"]["metadataProfileId"] = root_folder["defaultMetadataProfileId"]
    lidarr_album["artist"]["qualityProfileId"] = root_folder["defaultQualityProfileId"]
    lidarr_album["artist"]["rootFolderPath"] = root_folder["path"]
    return lidarr_post("/api/v1/album", json=lidarr_album)

def lidarr_import(root_folder):
    # currently not working
    return lidarr_post("/api/v1/command", json={"name": "DownloadedAlbumsScan", "path": root_folder["path"]})

def lidarr_retag(artist_id):
    retag_list = lidarr_get("/api/v1/retag", params={"artistId": artist_id})
    retag_data = {"artistId": artist_id, "files": [t["trackFileId"] for t in retag_list], "name": "RetagFiles"}
    return lidarr_post("/api/v1/command", json=retag_data)
