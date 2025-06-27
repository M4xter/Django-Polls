from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.shortcuts import render
from django.views import generic
from django.utils import timezone
from django.core.mail import send_mail
from django.core.mail import mail_admins
from .models import Choice, Question
from django.template.loader import render_to_string
from django.conf import settings
import requests
from django.http import JsonResponse
from .utils import get_client_ip, get_geoip_details
from .models import Response
from .models import Restaurant


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

def response_list_json(request):
    responses = Response.objects.all()
    data = []
    for r in responses:
        data.append({
            "id": r.id,
            "response_text": r.response_text,
            "longitude": r.longitude,
            "latitude": r.latitude,
        })
    return JsonResponse(data, safe=False)

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

        ip_address = get_client_ip(request)
        geo = get_geoip_details(ip_address)

        percentage = round((vote_count / total_votes) * 100, 2) if total_votes > 0 else 0

        ip_address = get_client_ip(request)

        try:
            url = f"https://api.hackertarget.com/geoip/?q={ip_address}&output=json"
            response = requests.get(url, timeout=5)
            geo_data = response.json() if response.status_code == 200 else {}
        except requests.RequestException:
            geo_data = {}

        country = geo_data.get("country", "Inconnu")
        city = geo_data.get("city", "Inconnue")
        longitude = geo_data.get("longitude")
        latitude = geo_data.get("latitude")

        if latitude is not None and longitude is not None:
            response_text = selected_choice.choice_text
            Response.objects.create(question=question, response_text=response_text, latitude=latitude, longitude=longitude)

        html_message = render_to_string("emails/vote_notification.html", {
            "question_text": question.question_text,
            "choice_text": selected_choice.choice_text,
            "percentage": percentage,
            "vote_count": vote_count,
            "ip_address": ip_address,
            "country": country,
            "longitude": longitude,
            "latitude": latitude,
            "city": city,
        })

        message = f"""Un utilisateur a voté "{selected_choice.choice_text}" pour la question :
"{question.question_text}".
Adresse IP : {ip_address}
Pays : {country}
Ville : {city}"""

        mail_admins(
            subject="Un utilisateur a voté",
            message=message,
            html_message=html_message
        )

        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    choices = question.choice_set.all()
    labels = [choice.choice_text for choice in choices]
    votes = [choice.votes for choice in choices]

    # Ajoute l'ID à la session si pas déjà présent
    polls_seen_ids = request.session.get('polls_seen', [])
    if question_id not in polls_seen_ids:
        polls_seen_ids.append(question_id)
        request.session['polls_seen'] = polls_seen_ids

    polls_total = Question.objects.count()

    return render(request, 'polls/results.html', {
        'question': question,
        'labels': labels,
        'votes': votes,
        'polls_seen': len(polls_seen_ids),
        'polls_total': polls_total
    })

def map_view(request):
    return render(request, 'map.html')

def restaurants_json(request):
    features = []

    for r in Restaurant.objects.all():
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [r.longitude, r.latitude]
            },
            "properties": {
                "name": r.name,
                "type": r.type,
                "id": r.id,
                "longitude": r.longitude,
                "latitude": r.latitude,
                "address": r.address,
                "description": r.description,
                "image_url": r.image_url,
            }
        })

    return JsonResponse({
        "type": "FeatureCollection",
        "features": features
    })

def index(request):
    questions = Question.objects.all()
    polls_total = questions.count()
    
    polls_seen = len(request.session.get('polls_seen', []))

    return render(request, 'polls/index.html', {
        'questions': questions,
        'polls_seen': polls_seen,
        'polls_total': polls_total
    })

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    # On ajoute l'ID à la liste des sondages vus dans la session
    polls_seen_ids = request.session.get('polls_seen', [])

    if question_id not in polls_seen_ids:
        polls_seen_ids.append(question_id)
        request.session['polls_seen'] = polls_seen_ids

    polls_total = Question.objects.count()

    return render(request, 'polls/detail.html', {
        'question': question,
        'polls_seen': len(polls_seen_ids),
        'polls_total': polls_total
    })