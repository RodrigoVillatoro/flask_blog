from my_app import app, db
import admin
import api
import models
import views

from entries.blueprint import entries
from feed.blueprint import feed

app.register_blueprint(entries, url_prefix='/entries')
app.register_blueprint(feed, url_prefix='/feed')

if __name__ == '__main__':
    app.run()
