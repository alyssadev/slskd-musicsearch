slskd-musicsearch
=================

A small library to query for a release ID from musicbrainz, then locate and queue downloads for the tracks in that release on an instance of slskd

Installation
------------

* Install `requests`, `musicbrainzngs`, `slskd-api` from pypi with `pip3 install requests musicbrainzngs slskd-api`
* Copy the functions in `slskdsearch.py`, or the file itself, into your project (it's MIT license).
* Set the environment variables `SLSKD_HOST` and `SLSKD_KEY` to the path to your slskd instance (`http://hostname:port`) and your [API key for slskd](https://github.com/slskd/slskd/blob/master/docs/config.md#authentication) respectively, or edit the values in the definition for the `slskd` variable.
* Set the environment variables `LIDARR_HOST` and `LIDARR_KEY` to the path to your lidarr instance (`http://hostname:port`) and your API key for lidarr respectively, or edit the values for the `lidarr` variable.

Usage
-----

do the above installation, then run `python3 -i slskdsearch.py`, then find the release ID for the album you want (not the release-group, one of the listed releases, probably the US CD release for western music) and run

```python
release_id = "pasted_id"
album = get_album(release_id)
search(album)
```

check slskd/searches to see the search progress, if it's successful it'll queue the files under /downloads and delete the search, if it's unsuccessful it'll show the search ID and you'll have to manually select files because it couldn't do it automatically sorry

You can also now tell lidarr to create an entry for the album and artist with

```python
lidarr_album = add_album_to_lidarr(release_id)
```

So far I haven't been able to get Lidarr to import the files from my unsorted folder automatically, you'll want to go to `/wanted/missing`, click Manual Import, and import it like that. But after that you can use

```python
lidarr_retag(lidarr_album["artist"]["id"])
```

to trigger Lidarr to update the metadata in the files. And then your music server should pick up the new files and all should be fine and/or dandy.
