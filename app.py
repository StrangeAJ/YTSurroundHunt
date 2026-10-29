PORT = 10000
import base64
import os
import tempfile

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
import yt_dlp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'randomkey'
CORS(app)

surround_formats = ['256', '258', '325', '327', '328', '338', '380']

_cookies_path = None


def get_cookies_path():
    """Resolve YouTube cookies from env vars (needed on datacenter IPs)."""
    global _cookies_path
    if _cookies_path is not None:
        return _cookies_path or None

    path = os.environ.get('YOUTUBE_COOKIES_FILE')
    if path and os.path.isfile(path):
        _cookies_path = path
        return path

    raw = os.environ.get('YOUTUBE_COOKIES')
    encoded = os.environ.get('YOUTUBE_COOKIES_B64')
    if encoded:
        try:
            raw = base64.b64decode(encoded).decode('utf-8')
        except Exception:
            app.logger.exception('Could not decode YOUTUBE_COOKIES_B64')

    if raw:
        fd, path = tempfile.mkstemp(prefix='yt-cookies-', suffix='.txt')
        with os.fdopen(fd, 'w', encoding='utf-8') as file:
            file.write(raw)
        _cookies_path = path
        return path

    _cookies_path = ''
    return None


def search_youtube(query, cookies=None):
    ydl_opts = {
        'default_search': 'ytsearch10',
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'js_runtimes': {'node': {}, 'deno': {}},
        'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    },
    }

    user_cookies_path = None
    if cookies and cookies.strip():
        fd, user_cookies_path = tempfile.mkstemp(
            prefix='yt-user-cookies-', suffix='.txt')
        with os.fdopen(fd, 'w', encoding='utf-8') as file:
            file.write(cookies)
        ydl_opts['cookiefile'] = user_cookies_path
    else:
        cookies_path = get_cookies_path()
        if cookies_path:
            ydl_opts['cookiefile'] = cookies_path

    proxy = os.environ.get('YOUTUBE_PROXY')
    if proxy:
        ydl_opts['proxy'] = proxy

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(query, download=False)
            results = []
            for entry in (search_results or {}).get('entries') or []:
                if not entry:
                    continue
                audio_qualities = []
                for format in entry.get('formats') or []:
                    if format.get('vcodec') != 'none':  # Skip formats that contain video
                        continue
                    channels = format.get('audio_channels') or 0
                    if format['format_id'] in surround_formats or channels > 2:
                        abr = format.get('abr')
                        audio_qualities.append([
                            format['format_id'],
                            f"{round(abr)}kbps" if abr else f"{channels}ch",
                        ])
                if audio_qualities:
                    results.append({
                        'title': entry.get('title', 'Unknown title'),
                        'url': entry.get('webpage_url'),
                        'audio_qualities': audio_qualities
                    })
            return results
    finally:
        if user_cookies_path:
            try:
                os.remove(user_cookies_path)
            except OSError:
                pass

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])

@app.route('/')
def index():
    return render_template('index.html', form=SearchForm())


@app.route('/search', methods=['POST'])
def search():
    query = (request.form.get('query') or '').strip()
    if not query:
        return jsonify({'error': 'Please enter a search query.'}), 400

    cookies = request.form.get('cookies') or ''
    if len(cookies) > 1_000_000:
        return jsonify({'error': 'Cookies file is too large.'}), 413

    try:
        return jsonify({'results': search_youtube(query, cookies=cookies)})
    except Exception:
        app.logger.exception('Search failed')
        return jsonify({'error': 'An error occurred during the search.'}), 500


@app.route('/healthz')
def healthz():
    return jsonify({'status': 'ok'})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
