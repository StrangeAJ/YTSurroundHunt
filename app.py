PORT = 10000
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

def search_youtube(query):
    ydl_opts = {
        'default_search': 'ytsearch10',
        'quiet': True,
        'no_warnings': True,
        'js_runtimes': {'node': {}, 'deno': {}},
        'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    },
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        search_results = ydl.extract_info(query, download=False)
        results = []
        for entry in search_results.get('entries') or []:
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
    try:
        return jsonify({'results': search_youtube(query)})
    except Exception:
        app.logger.exception('Search failed')
        return jsonify({'error': 'An error occurred during the search.'}), 500


@app.route('/healthz')
def healthz():
    return jsonify({'status': 'ok'})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
