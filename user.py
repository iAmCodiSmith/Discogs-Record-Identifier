import pickle
from release import Release
from urllib.error import HTTPError
import discogs_client

class DataStructure:
    def __init__(self, d):
        self.d = d
        self._all_releases = []
        self._all_release_numbers = []
        self._past_searches = []
        username = d.identity()
        username = username.username

        self.current_user = DiscogsUser(username, d)

        try:
            with open('saved_data/all_releases.pkl', 'rb') as release_pickle:
                previously_loaded_releases = pickle.load(release_pickle)
                for release in previously_loaded_releases:
                    self._all_releases.append(release)
                    self._all_release_numbers.append(release.release_number())
        except FileNotFoundError:
            print("No Releases Saved...")

        x = 0
        y = 0
        while x < 10:
            try:
                if self.current_user._collection_release_numbers[y] in self._all_release_numbers:
                    release = self.getRelease(self.current_user._collection_release_numbers[y])
                    if release.master_image() == None:
                        master_image = Release.getDiscogsMasterImage(release.master_release_number(), self.d)
                        release.master_image(master_image)
                        x+=1
                    y += 1


                else:
                    release = Release.getDiscogsReleaseInfo(self.current_user._collection_release_numbers[y], d)
                    self._all_releases.append(release)
                    self._all_release_numbers.append(release.release_number())
                    y += 1
                    x += 1
            except IndexError:
                break

        with open('saved_data/all_releases.pkl','wb') as releases_pickle:
            pickle.dump(self._all_releases, releases_pickle)

        try:

            with open('saved_data/past_searches.pkl', 'rb') as past_search_pickle:
                past_searches = pickle.load(past_search_pickle)
                for past_search in past_searches:
                    self._past_searches.append(past_search)
        except FileNotFoundError:
            print("No Past Searches Saved...")

    def currentUser(self, currentUser = None):
        if currentUser:
            self.current_user = currentUser
        return self.current_user

    def allReleases(self, all_releases=None):
        if all_releases:
            self._all_releases = all_releases
        return self._all_releases

    def allReleaseNumbers(self, all_release_numbers=None):
        if all_release_numbers:
            self._all_release_numbers = all_release_numbers
        return self._all_release_numbers

    def pastSearches(self, past_searches=None):
        if past_searches:
            self._past_searches = past_searches
        return self._past_searches

    def getRelease(self, release_number=None):
        for release in self._all_releases:
            if release_number in release.release_number():
                return release
        print("Release Not Found", release_number)

    def save_new_releases(self, release):
        self._all_releases.append(release)
        with open('saved_data/all_releases.pkl','wb') as releases_pickle:
            pickle.dump(self._all_releases, releases_pickle)

    def saveSearch(self, new_search):
        self._past_searches.append(new_search)
        with open('saved_data/past_searches.pkl', 'wb') as past_searches_pickle:
            pickle.dump(self._past_searches, past_searches_pickle)


class DiscogsUser:
    def __init__(self, username, d):
        self._username = username
        self._collection_release_numbers = []
        self._collection = []
        self._tool_searches = []
        self.getUserCollection(self._username, d)

    def getCollectionReleaseNumbers(self, collection_release_numbers=None):
        if collection_release_numbers:
            self._collection_release_numbers = collection_release_numbers
        return self._collection_release_numbers

    def getUserCollection(self, username, d):
        user_collection = d.identity()
        user_folder = user_collection.collection_folders[0]
        releases = []
        for page in range(user_folder.releases.pages):
            for release in user_folder.releases.page(page):
                release = str(release).split()
                releases.append(release[2:])
                self._collection_release_numbers.append(release[1])
        return 1