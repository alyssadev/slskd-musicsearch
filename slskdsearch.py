#!/usr/bin/env python3
import musicbrainzngs
from slskd_api import SlskdClient
from time import sleep
from os import environ

musicbrainzngs.set_useragent("slskd-musicsearch", "0.1", "https://github.com/alyssadev/slskd-musicsearch")
slskd = SlskdClient(environ.get("SLSKD_HOST","http://localhost:5030"), environ.get("SLSKD_KEY",""))

def print_json(d):
    from json import dumps
    print(dumps(d,indent=4))

def get_album(mbid):
    result = musicbrainzngs.get_release_by_id(mbid, includes=["artists", "recordings", "recording-level-rels", "work-rels", "work-level-rels"])["release"]
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
            print(query, s)
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
        print_json(track_names)
        matches = 0
        resp = {"username": result["username"], "files": []}
        for f in result["files"]:
            fn = (f["filename"].split("\\")[-1])
            print(fn)
            _track_names = dict(track_names)
            for n,title in _track_names.items():
                if f"{title[0]}.flac" in fn or (f"{title[1]}.flac" in fn if title[1] else False):
                    del track_names[n]
                    resp["files"].append(f)
                    matches += 1
            if not track_names:
                break
        if matches == len([track["title"] for track in album["tracks"]]):
            slskd.transfers.enqueue(**resp)
            slskd.searches.delete(search["id"])
            return True
        if not matches:
            continue
        resp["matches"] = matches
        lookup.append(resp)
    return search["id"]
