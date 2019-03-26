# photos-of-you
Get all of the Facebook "photos of you" that you're tagged in.

Credit to https://github.com/jcontini/fb-photo-downloader for most of the chromedriver code, I've never worked with selenium before and was able to use a lot of this code. I just rewrote a bunch of it for downloading and for exception handling, and I didn't care too much about certain edge cases (video, for example).

## Usage

You need to have chromedriver in your PATH. You can download chromedriver here: http://chromedriver.chromium.org/downloads. Once you download, make sure it is on your PATH.

```
pip install -r requirements.txt
python get_photo_urls.py -u <fb-email> -p <ya-password>
python download_photos.py
```
