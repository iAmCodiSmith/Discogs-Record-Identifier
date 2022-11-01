import datetime
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import matplotlib.pyplot as plt

import matplotlib.image as mpimg
from tkinter import Tk  # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename
import discogs_client
import requests
from itertools import takewhile
import collections
import sys

from serpapi import GoogleSearch
from imgurpython import ImgurClient
import pathlib
from PIL import Image
import tensorflow as tf
from tensorflow import keras
from keras import layers
from keras import Sequential
import numpy as np
from release import *

# physical_devices = tf.config.list_physical_devices('GPU')
# tf.config.experimental.set_memory_growth(physical_devices[0], True)

# Enter Imgur Upload key
client_id = ' '
client_secret = ' '
client = ImgurClient(client_id, client_secret)
def imgur_client():
    return client

# Enter Serp API key
params = {
    "api_key": " ",
    "engine": "google_reverse_image",
    "google_domain": "google.com"
}

# Used for maitenence tool
def get_serp_params():
    return params

# Uses the first image (Cover Art) to reverse image search which returns links
# to webpages referencing similar images found.
# These links are searched the most frequently used common words and they are
# returned, words that are unlikely to be helpful are parsed out.
def getArtistAlbum(image_path):
    img = Image.open(image_path)
    width, height = img.size
    img = img.resize((int(width / 4), int(height / 4)), Image.ANTIALIAS)
    img = img.quantize(colors=64)
    img.save(fp='saved_data/upload.png')
    link = client.upload_from_path('saved_data/upload.png', config=None, anon=False)

    search_params = params.copy()
    search_params.update({"image_url": link["link"]})
    search = GoogleSearch(search_params)
    results = search.get_dict()
    results_array = []
    for i in results['image_results']:
        results_array.append(i["title"])

    Title_Text = ""
    for i in results_array:
        Title_Text += str(i) + ' - '
        remove_char = [" - ", "...", ".", "|", ",", ":", " By ", " Album ", " Music ", " Wikipedia ",
                       " Picture ", " Painting ", " Amazon ", " Com ", " Review ", " Reviews ", " Edition ",
                       " Anniversary ", " Limited ", " Spotify ", " Lyrics ", " A ", " Discogs ", " Vinyl ",
                       " Apple ", " Google ", "eBay", "Pitchfork"]  # More unlikely helpful words could be removed from search data
        for each_char in remove_char:
            Title_Text = Title_Text.replace(each_char, " ")
            Title_Text = Title_Text.replace(each_char.lower(), " ")

    split_it = Title_Text.split()
    from collections import Counter
    Counter = Counter(split_it)
    most_occur = Counter.most_common(7)
    the_common_words = ""
    for i in range(len(most_occur)):
        if most_occur[i][1] > 1:
            the_common_words += most_occur[i][0]
            the_common_words += " "
    return the_common_words

# This is the method that trains the machine learning model, it uses images seperated as folders and compares the
# attributes of the images to predict in the future the classification that a new provided image would likely belong to
# This method is not available to the end user.
def getTrainColor(image_path):
    data_dir = pathlib.Path('application_data/vinyl_record_colors/')
    batch_size = 3
    img_height = 128
    img_width = 128

    train_ds = tf.keras.preprocessing.image_dataset_from_directory(
        data_dir,
        validation_split=0.15,
        subset="training",
        seed=123,
        image_size=(img_height, img_width),
        batch_size=batch_size)

    val_ds = tf.keras.preprocessing.image_dataset_from_directory(
        data_dir,
        validation_split=0.15,
        subset="validation",
        seed=123,
        image_size=(img_height, img_width),
        batch_size=batch_size)

    class_names = train_ds.class_names
    normalization_layer = layers.experimental.preprocessing.Rescaling(1. / 128)
    normalized_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))

    num_classes = 12

    model = Sequential([
        layers.experimental.preprocessing.RandomFlip("horizontal_and_vertical",
                                                     input_shape=(img_height,
                                                                  img_width,
                                                                  3)),
        layers.Conv2D(32, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(128, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Dropout(0.1),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dense(num_classes)
    ])

    model.compile(
        optimizer='adam',
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=['accuracy'])

    epochs = 7
    history = model.fit(
        normalized_ds,
        validation_data=val_ds,
        epochs=epochs
    )
    model.save('application_files/record_color_model')

    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']

    loss = history.history['loss']
    val_loss = history.history['val_loss']

    epochs_range = range(epochs)

    plt.figure(figsize=(8, 8))
    plt.subplot(1, 2, 1)
    plt.plot(epochs_range, acc, label='Training Accuracy')
    plt.plot(epochs_range, val_acc, label='Validation Accuracy')
    plt.legend(loc='lower right')
    plt.title('Training and Validation Accuracy')

    plt.subplot(1, 2, 2)
    plt.plot(epochs_range, loss, label='Training Loss')
    plt.plot(epochs_range, val_loss, label='Validation Loss')
    plt.legend(loc='upper right')
    plt.title('Training and Validation Loss')
    plt.show()

    img = keras.preprocessing.image.load_img(
        image_path, target_size=(img_height, img_width)
    )

    img_array = keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)

    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])

    print("This image most likely belongs to {} with a {:.2f} percent confidence."
          .format(class_names[np.argmax(score)], 100 * np.max(score))
          )
    media_color = class_names[np.argmax(score)]
    return media_color

# The model has premptively been trained and saved, here it is loaded to be used with the media image to identify its color.
def getRecordColor(image_path):
    img_height = 128
    img_width = 128
    model = keras.models.load_model('application_files/record_color_model')
    class_names = ['black', 'blue', 'brown', 'green', 'orange', 'pink', 'purple', 'red', 'teal', 'white', 'yellow']
    img = keras.preprocessing.image.load_img(
        image_path, target_size=(img_height, img_width)
    )
    img_array = keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)
    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])
    #Prediction Accuracy
    prediction_accuracy = "This Vinyl Record Is Likely {} With A {:.2f} Percent Confidence.".format(class_names[np.argmax(score)].title(), 100 * np.max(score))
    media_color = class_names[np.argmax(score)]
    return media_color, prediction_accuracy

# Used to identify the common words found in the TrueSearch function below
def most_frequent(List):
    counter = 0
    if len(List) != 0:
        num = List[0]
        for i in List:
            curr_frequency = List.count(i)
            if (curr_frequency > counter):
                counter = curr_frequency
                num = i
        return num

# Gets the master image of a release
def getDiscogsMasterImage(master_id, d):
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
    master = d.master(master_id)
    master = master.fetch('images')
    master_image = master[0]['uri']
    master_image = PIL.Image.open(requests.get(master_image, stream=True,headers=headers).raw)
    return master_image

# The core algorithm of the tool.
# Uses the images selected in the gui to reverse search the album art in the first image and
# identify the color of the vinyl record in the second image to return the Discogs database entry
# of the release in the two images.
def theTrueSearch(the_common_words, identified_color, cover_art, media_art, d):
    from googlesearch import search as gsearch
    query = '"Discogs" ' + the_common_words + ' "' + identified_color + '" vinyl'
    results = []
    result_limit = 10
    for j in gsearch(query):
        result_limit = result_limit - 1
        if '/release/' in j and 'discogs.com' in j:
            results.append(j)
        if result_limit == 0:
            break
    artist = []
    album = []
    master_ids = []
    found_releases = []
    for release in results:
        index_of_release = release.index("/release/")
        discogs_release_id = release[index_of_release + 9:]
        for i in discogs_release_id:
            if not i.isnumeric():
                discogs_release_id = discogs_release_id[:discogs_release_id.index(i)]
                break
        if discogs_release_id.isnumeric():
            release = Release.getDiscogsReleaseInfo(discogs_release_id, d)
            artist.append(release.artist_name())
            album.append(release.album_name())
            master_ids.append(release.master_release_number())
            format = release.media_format()
            if format == 'Vinyl' or format == 'Flexi-disc' or format == 'Test Pressing':
                found_releases.append(release)

    try:
        first_choice = found_releases[0]
        search_date = datetime.datetime.now()
        search_date = search_date.strftime("%Y-%m-%d %H:%M:%S")
        this_search = PastSearch(search_date, query, found_releases, identified_color, cover_art, media_art)

        if most_frequent(master_ids) != None:
            master_image = getDiscogsMasterImage(most_frequent(master_ids), d)
            return query, master_image, first_choice, this_search
    except:
        search_date = datetime.datetime.now()
        search_date = search_date.strftime("%Y-%m-%d %H:%M:%S")
        this_search = PastSearch(search_date, query, None, identified_color, cover_art, media_art)

        if most_frequent(master_ids) != None:
            master_image = getDiscogsMasterImage(most_frequent(master_ids), d)
            return query, master_image, None, this_search
        return query, None, None, this_search