import os, time, openai, textwrap
from django.core.management.base import BaseCommand
from polls.models import Restaurant

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"     # rapide et moins cher, ou "gpt-4o"

PROMPT_TEMPLATE = textwrap.dedent("""
    Rédige une description engageante (max 500 caractères) pour un restaurant :
    Nom : {name}
    Adresse : {addr}
    Type : {cuisine}

    La description doit :
    • tenir en une ou deux phrases
    • être écrite en français
    • donner envie d'y aller
""").strip()

class Command(BaseCommand):
    help = "Génère et sauvegarde la description de chaque restaurant via OpenAI"

    def handle(self, *args, **opts):
        restos = Restaurant.objects.filter(description="")  # ignore ceux déjà remplis
        for i, r in enumerate(restos, 1):
            prompt = PROMPT_TEMPLATE.format(
                name=r.name,
                addr=r.address or "adresse non précisée",
                cuisine=r.type or "cuisine variée"
            )

            try:
                resp = openai.ChatCompletion.create(
                    model=MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=180,           # ~500 caractères FR ≈ 120 tokens
                    temperature=0.7
                )
                desc = resp.choices[0].message.content.strip()
                r.description = desc[:500]   # sécurité
                r.save(update_fields=["description"])
                self.stdout.write(self.style.SUCCESS(f"[{i}] {r.name} ✓"))
            except Exception as e:
                self.stderr.write(f"[{i}] {r.name} — erreur : {e}")
                time.sleep(2)                # petite pause avant le suivant

            time.sleep(1)                    # throttle soft pour éviter spike
 