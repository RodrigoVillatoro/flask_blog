from urllib.parse import urljoin
from flask import Blueprint, request, url_for
from werkzeug.contrib.atom import AtomFeed

from app import app
from models import Entry

feed = Blueprint('feed', __name__)


@feed.route('/latest.atom')
def recent_feed():
    feed = AtomFeed(
        'Latest Blog Posts',
        feed_url=request.url,
        url=request.url_root,
        author=request.url_root
    )

    entries = Entry.query.filter(
        Entry.status == Entry.STATUS_PUBLIC
    ).order_by(Entry.created_timestamp.desc()).limit(15).all()

    for entry in entries:
        feed.add(
            entry.title,
            entry.body,
            content_type='html',
            url=urljoin(
                request.url_root,
                url_for('entries.detail', slug=entry.slug)),
            updated=entry.modified_timestamp,
            published=entry.created_timestamp
        )

    return feed.get_response()