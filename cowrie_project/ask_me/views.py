from django.shortcuts import render
import requests, random, time
from django.http import JsonResponse
from .models import AttackType, Tips
import json

# Create your views here.
def classification_view(request):
    attack_type = None
    description = None
    
    if request.method == 'POST':
        data = {
            'username': request.POST.get('username'),
            'input': request.POST.get('input'),
            'protocol': request.POST.get('protocol'),
            'duration': request.POST.get('duration'),
            'data': request.POST.get('data'),
            'keyAlgs': request.POST.get('keyAlgs'),
            'message': request.POST.get('message'),
            'eventid': request.POST.get('eventid'),
            'kexAlgs': request.POST.get('kexAlgs')
        }

        backend_url = "https://ewe-happy-centrally.ngrok-free.app/classify"  # Replace with your Flask backend URL
        response = requests.post(backend_url, json=data)

        if response.status_code == 200:
            result = response.json()
            attack_type = result.get('attack_type')

            # Look up the description from the database
            try:
                attack_type_entry = AttackType.objects.get(attack_type=attack_type)
                description = attack_type_entry.description
            except AttackType.DoesNotExist:
                description = "No description available for this attack type."

    return render(request, 'ask_me/classification.html', {'attack_type': attack_type, 'description': description})

def qa_view(request):
    answer = None
    question = None
    
    tips = list(Tips.objects.all())
    tips_data = [{'content': tip.content} for tip in tips] 
    
    if request.method == 'POST':
        question = request.POST.get('question')
        backend_url = "https://ewe-happy-centrally.ngrok-free.app/qa" 
        response = requests.post(backend_url, json={'question': question})
        if response.status_code == 200:
            answer = response.json().get('answer')

    random.shuffle(tips)

    return render(request, 'ask_me/qa.html', {
        'answer': answer, 
        'question': question, 
        'tips': json.dumps(tips_data)  
    })

def summary_view(request):
    summary = None
    paragraph = None

    if request.method == 'POST':
        paragraph = request.POST.get('paragraph')

        backend_url = "https://ewe-happy-centrally.ngrok-free.app/summarize"  # Replace with your Flask backend URL
        
        try:
            response = requests.post(backend_url, json={'paragraph': paragraph})
            response.raise_for_status()
            summary = response.json().get('summary')
        except requests.RequestException as e:
            print(f"Request failed: {e}")

    return render(request, 'ask_me/summary.html', {'summary': summary, 'paragraph': paragraph})
