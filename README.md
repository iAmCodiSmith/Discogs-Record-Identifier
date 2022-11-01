# Discogs-Record-Identifier
## Identifies Discogs Releases from two images: Album sleeve and the wax itself

Uses Discogs API to load your collection.
Once logged in two images can be provided to try and locate its matching Discogs release.
The album is identified using Google's reverse image search so image quality and clarity, as well as relevance (popular enough to show up in a image search) are imperative.
- Search results can be double checked using "link" button to open the release in browser.
- Past searches are saved and can be revisited.

Discogs API has changed since I originally wrote this and limits requests. As a result upon first use only 10 records in your collection will load and 10 will be added ever subsquent login. This is entirely a restriction due to the Discogs API.

![alt text](https://github.com/iAmCodiSmith/Discogs-Record-Identifier/blob/master/readmeImage/main.png)
## Requires Imgur API keys and SerpApi key, both are free and must be entered in "record_identifier.py".
