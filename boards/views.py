from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from boards.models import Board, Topic, Post
from .forms import NewTopicForm

def home(request):
    boards = Board.objects.all()

    return render(request, 'home.html', {'boards': boards})


def boards_topics(request, pk):
    board = get_object_or_404(Board, pk=pk)
    return render(request, 'topics.html', {'board': board})

def topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board_id=pk, pk=topic_pk)
    return render(request, 'topic_posts.html', {'topic': topic})
# Create your views here.

@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    # deprecated! user = User.objects.first()

    if request.method == 'POST' :
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()
            post = Post.objects.create(
                message = form.cleaned_data.get('message'),
                topic = topic,
                created_by = request.user
            )
            return redirect('boards_topics', pk=board.pk)
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})
