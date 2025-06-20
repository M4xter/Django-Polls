from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.core.mail import send_mail
from django.core.mail import mail_admins
from .models import Choice, Question
from django.template.loader import render_to_string
from django.conf import settings


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published inZ the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.get_object()
        choices = question.choice_set.all()
        total_votes = sum(choice.votes for choice in choices)

        context['total_votes'] = total_votes
        context['labels'] = [choice.choice_text for choice in choices]
        context['votes'] = [choice.votes for choice in choices]
        return context


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "Tu n'as selectionné aucun choix.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        selected_choice.refresh_from_db()

        vote_count = selected_choice.votes

        total_votes = sum(choice.votes for choice in question.choice_set.all())
        if total_votes > 0:
            percentage = round((vote_count / total_votes) * 100, 2)
        else:
            percentage = 0

        html_message = render_to_string("emails/vote_notification.html", {
            "question_text": question.question_text,
            "choice_text": selected_choice.choice_text,
            "percentage": percentage,
            "vote_count": vote_count,
        })

        
        mail_admins(
            subject="Un utilisateur a voté",
            message=f'L\'utilistaeur a voté "{selected_choice.choice_text}" pour la question : "{question}".', # None, # recipient_list=settings.ADMINS
            html_message=html_message
        )
        
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    choices = question.choice_set.all()
    labels = [choice.choice_text for choice in choices]
    votes = [choice.votes for choice in choices]
    
    return render(request, 'polls/results.html', {
        'question': question,
        'labels': labels,
        'votes': votes,
    })