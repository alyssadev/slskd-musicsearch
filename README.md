slskd-musicsearch
=================

A small library to query for a release ID from musicbrainz, then locate and queue downloads for the tracks in that release on an instance of slskd

Installation
------------

* Install `musicbrainzngs` and `slskd-api` from pypi with `pip3 install musicbrainzngs slskd-api`
* Copy the functions in `slskdsearch.py`, or the file itself, into your project (it's MIT license).
* Set the environment variables `SLSKD_HOST` and `SLSKD_KEY` to the path to your slskd instance (`http://hostname:port`) and your [API key for slskd](https://github.com/slskd/slskd/blob/master/docs/config.md#authentication) respectively, or edit the values in the definition for the `slskd` variable.

tl;dr
-----

do the above installation, then run `python3 -i slskdsearch.py`, then find the release ID for the album you want (not the release-group, one of the listed releases, probably the US CD release for western music) and run

```python
album = get_album(pasted_id)
search(album)
```

check slskd/searches to see the search progress, if it's successful it'll queue the files under /downloads and delete the search, if it's unsuccessful it'll show the search ID and you'll have to manually select files because it couldn't do it automatically sorry

Usage
-----

Locate the release ID for the specific version of the album you want. One way you can do this is, go to https://musicbrainz.org/, in the top right search box search for the artist, find the correct artist from the search results, find the correct album in the list, then in the release group for that album you should probably find the release that says CD in the format column and says either US or your country in the country column. The release ID is after `/release/` in that url.

```python
from slskdsearch import get_album, search # skip this if you've copied the functions into your project
MBID = "2e789ca4-020c-37ec-9f64-236c9ae1bd5f"
album = get_album(MBID)
search(album)
# while this is running, check the searches list on slskd, you should see the search progress
# if the search was successful, the function will return True, and the full album will be downloading in the download list in slskd
# if the search was not successful or was not entirely successful, the function will return the search ID, and you should go to /searches/<search ID> in slskd to manually select the files you want
```
