import io
from spotifyauth import startup
from flask import Flask, render_template, redirect, request, url_for, session

from src.plotter import gen_plot
from src.spotify import get_playlists

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    auth = startup.getAccessToken()
    if auth:
        # Get all the playlists for the authenticated user
        playlists = get_playlists(startup.getAccessToken()[0])

    if (request.method == 'GET'):
        if auth:
            # User is already authenticated, render the page
            return render_template('chart.html', playlists=playlists)
        else:
            # User is not authenticated, authenticate user with spotify
            response = startup.getUser()
            return redirect(response, code=302)
    elif (request.method == 'POST'):
        # Graph Creation
        choice = request.form.get('playlists') # Get selected playlist
        chart = gen_plot(startup.getAccessToken()[0], choice) # Create the plot
        return render_template('chart.html', playlists=playlists, chart=chart) # Render the plot

@app.route('/callback/')
def callback():
    # Authenticate user with spotify
    startup.getUserToken(request.args['code'])
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(threaded=True, port=5000) # Start the webserver
