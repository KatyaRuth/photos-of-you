import os
import json
import shutil
import requests


def download_photos():
    # Prep the download folder
    folder = 'photos/'
    if not os.path.exists(folder):
        os.makedirs(folder)
    print("Saving photos to " + folder)
    # Download the photos
    with open('tagged.json', 'r') as f:
        for line in f:
            record = json.loads(line)
            img_id = record['media_url'].split('_')[1]
            new_filename = folder + record['fb_date'] + '_' + img_id + '.jpg'
            if os.path.exists(new_filename):
                print("Already Exists (Skipping): {}".format(new_filename))
            else:
                try:
                    r = requests.get(record['media_url'], stream=True)
                    if r.status_code == 200:
                        with open(new_filename, 'wb') as f:
                            r.raw.decode_content = True
                            shutil.copyfileobj(r.raw, f)
                except requests.exceptions.HTTPSConnectionPool:
                    print('Failed to get photo with url: {}'.format(record['media_url']))


if __name__ == '__main__':
    download_photos()
