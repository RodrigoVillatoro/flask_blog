from flask_restless import ProcessingException

from app import api
from entries.forms import CommentForm
from models import Comment


def post_preprocessor(data, **kwargs):
    form = CommentForm(data=data)
    if form.validate():
        return form.data
    else:
        raise ProcessingException(
            description='Invalid form submission.',
            code=400
        )


api.create_api(Comment, methods=['GET', 'POST'], preprocessors={
    'POST': [post_preprocessor]
})
