PORT = 10000
from flask import Flask, request, render_template
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

surround_formats = ['256', '258', '325', '327', '328', '338', '380']

def search_youtube(query):
    ydl_opts = {
        'default_search': 'ytsearch10',
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    },
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        search_results = ydl.extract_info(query, download=False)
        results = []
        for entry in search_results['entries']:
            audio_qualities = []
            for format in entry['formats']:
                if format['vcodec'] == 'none':  # This format is audio-only
                    if format['format_id'] in surround_formats:
                        audio_qualities.append([format['format_id'], f"{format['abr']}kbps"])
            if audio_qualities:
                results.append({
                    'title': entry['title'],
                    'url': entry['webpage_url'],
                    'audio_qualities': audio_qualities
                })
        return results

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        results = search_youtube(query)
        return render_template('index.html', results=results)
    return render_template('index.html', results=None)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
