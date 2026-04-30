import random

ICEBREAKERS = {
    'Fun': [
        "🍕 Ananas sur la pizza : pour ou contre ?",
        "Si tu pouvais avoir un super-pouvoir, lequel ?",
        "Quelle est la chose la plus folle que tu aies faite ?",
        "Ton talent caché le plus inutile ?",
        "Karaoké : quelle chanson choisis-tu ?",
    ],
    'Voyage': [
        "🌍 Si tu pouvais vivre n'importe où, ce serait où ?",
        "Un endroit que tu rêves de visiter ?",
        "Plage ou montagne ?",
        "Ton plus beau souvenir de voyage ?",
        "Prochain voyage prévu ?",
    ],
    'Musique': [
        "🎵 La chanson qui te fait toujours danser ?",
        "Le film que tu peux regarder 100 fois ?",
        "Artiste préféré en ce moment ?",
        "Dernier concert auquel tu as assisté ?",
        "Playlist du moment ?",
    ],
    'Nourriture': [
        "🍕 Ton plat signature ?",
        "Café ou thé le matin ?",
        "Un aliment que tu détestes ?",
        "Cuisiner ou commander ?",
        "Meilleur resto que tu aies testé ?",
    ],
    'Personnalité': [
        "Plutôt matinal ou oiseau de nuit ?",
        "Introverti ou extraverti ?",
        "Ta plus grande passion ?",
        "Citation qui t'inspire ?",
        "Qu'est-ce qui te fait rire à coup sûr ?",
    ]
}

def get_random_icebreaker(category=None):
    if category and category in ICEBREAKERS:
        return random.choice(ICEBREAKERS[category])
    cat = random.choice(list(ICEBREAKERS.keys()))
    return {'category': cat, 'message': random.choice(ICEBREAKERS[cat])}

def get_all_categories():
    return list(ICEBREAKERS.keys())
