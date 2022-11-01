from urllib.error import HTTPError
import PIL
from PIL import Image
import requests
import discogs_client
from discogs_client.exceptions import HTTPError


class Release:
    def __init__(self, artist_name, album_name, release_number, master_release_number, media_color, media_format, master_image):
        self._artist_name = artist_name
        self._album_name = album_name
        self._release_number = release_number
        self._master_release_number = master_release_number
        self._media_color = media_color
        self._media_format = media_format
        self._master_image = master_image

    def artist_name(self, artist_name=None):
        if artist_name:
            self._artist_name = artist_name
        return self._artist_name

    def album_name(self, album_name=None):
        if album_name:
            self._album_name = album_name
        return self._album_name

    def release_number(self, release_number=None):
        if release_number:
            self._release_number = release_number
        return self._release_number

    def master_release_number(self, master_release_number=None):
        if master_release_number:
            self._master_release_number = master_release_number
        return self._master_release_number

    def media_color(self, media_color=None):
        if media_color:
            self._media_color = media_color
        return self._media_color

    def media_format(self, media_format=None):
        if media_format:
            self._media_format = media_format
        return self._media_format

    def master_image(self, master_image=None):
        if master_image:
            self._master_image = master_image
        return self._master_image

    def getDiscogsReleaseInfo(release_number, d):
        if release_number.isdecimal():
            album_name = d.release(release_number)
            master_id = album_name.master
            artist_name = album_name.artists
            media_format = album_name.formats[0]['name']
            if 'Vinyl' or 'Flexi-disc' or 'Test Pressing' in media_format:
                try:
                    media_color = album_name.formats[0]['text']
                except KeyError:
                    media_color = "Black"
            split = str(album_name).split()
            split[2] = split[2].replace("'", "")
            split[len(split) - 1] = split[len(split) - 1].replace(">", "")
            split[len(split) - 1] = split[len(split) - 1].replace("'", "")
            album_name = ""
            for word in split[2:]:
                album_name += word + " "

            album_name = album_name[0:-1]

            split = str(artist_name).split()
            split[2] = split[2].replace("'", "")
            split[len(split) - 1] = split[len(split) - 1].replace("'>", "")
            artist_name = ""
            for word in split[2:]:
                artist_name += word + " "

            artist_name = artist_name[0:-2]

            split = str(master_id).split()
            if master_id != None:
                master_id = split[1]
                master_image = Release.getDiscogsMasterImage(master_id, d)
            else:
                master_id = None
                master_image = PIL.Image.open('application_files/image_unavailable.png')
            if media_format == 'Vinyl':
                discogs_release = Release(artist_name, album_name, release_number, master_id, media_color, media_format,
                                          master_image)
            else:
                discogs_release = Release(artist_name, album_name, release_number, master_id, media_color, media_format,
                                          master_image)
            return discogs_release

    def getDiscogsMasterImage(master_id, d):
        if master_id != None:
            master = d.master(master_id)
            master = master.fetch('images')
            if master != None:
                master_image = master[0]['uri']
                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    # noqa
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                    "Dnt": "1",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
                    # noqa
                }
                master_image = PIL.Image.open(requests.get(master_image, stream=True, headers=headers).raw)
            else:
                master_image = PIL.Image.open('application_files/image_unavailable.png')
        else:
            master_image = PIL.Image.open('application_files/image_unavailable.png')

        return master_image


    def __str__(self):
        return f'Artist Name = {self._artist_name}, \
        Album Name = {self._album_name}, \
        Release Number = {self._release_number} \
        Master Release Number = {self._master_release_number}, \
        Media Color = {self._media_color}, \
        Media Format = {self._media_format}'

class Artist:
    def __init__(self, name):
        self._artist_name = name
        self._appearance_counter = 0

    def artist_name(self, artist_name=None):
        if artist_name:
            self._artist_name = artist_name
        return self._artist_name

    def appearance_counter(self, appearance_counter=None):
        if appearance_counter:
            self._appearance_counter = appearance_counter
        return self._appearance_counter

class PastSearch:
    def __init__(self, search_date, search_query, found_releases, identified_color, cover_art, media_art):
        self._search_date = search_date
        self._search_query = search_query
        self._found_releases = found_releases
        self._identified_color = identified_color
        self._cover_art = cover_art
        self._media_art = media_art

    def search_date(self, search_date=None):
        if search_date:
            self._search_date = search_date
        return self._search_date

    def search_query(self, search_query=None):
        if search_query:
            self._search_query = search_query
        return self._search_query

    def found_releases(self, found_releases=None):
        if found_releases:
            self._found_releases = found_releases
        return self._found_releases

    def identified_color(self, identified_color=None):
        if identified_color:
            self._identified_color = identified_color
        return self._identified_color

    def cover_art(self, cover_art=None):
        if cover_art:
            self._cover_art = cover_art
        return self._cover_art

    def media_art(self, media_art=None):
        if media_art:
            self._media_art = media_art
        return self._media_art