import io
from spotifyauth import startup
from flask import Flask, render_template, redirect, request, url_for, session, Response

from src.plotter import gen_plot
from src.spotify import get_playlists

from flask import jsonify, json

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    auth = startup.getAccessToken()
    if auth:
        # Get all the playlists for the authenticated user
        playlists = get_playlists(startup.getAccessToken()[0])

    else:
        # User is not authenticated, authenticate user with spotify
        response = startup.getUser()
        return redirect(response, code=302)
    if (request.method == 'POST'):
        # Graph Creation
        choice = request.form.get('playlists') # Get selected playlist
        text_color = request.form.get('text')
        background_color = request.form.get('background')
        title = request.form.get('title')
        freq = int(request.form.get('increment'))
        song_count = int(request.form.get('song_count'))
        #chart = gen_plot(startup.getAccessToken()[0], choice, background_color, title, text_color, freq, song_count) # Create the plot
        return render_template('chart.html', playlists=playlists) # Render the plot

    else:
        if auth:
            # User is already authenticated, render the page
            return render_template('chart.html', playlists=playlists)
        else:
            # User is not authenticated, authenticate user with spotify
            response = startup.getUser()
            return redirect(response, code=302)
@app.route('/_generate')
def generate():
    print(request.args.get('a'))
    choice = request.args.get('playlist') # Get selected playlist
    freq = int(request.args.get('freq'))
    song_count = int(request.args.get('song_count'))
    text_color = request.args.get('text_color')
    background_color = request.args.get('background_color')
    title = request.args.get('title')

    chart = gen_plot(startup.getAccessToken()[0], choice, background_color, title, text_color, freq, song_count) # Create the plot
    print(chart)
    return jsonify(chart=chart)

@app.route('/callback/')
def callback():
    # Authenticate user with spotify
    startup.getUserToken(request.args['code'])
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(threaded=True, port=5000) # Start the webserver
