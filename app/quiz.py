QUIZ_QUESTIONS = [
    {
        'question': 'Quel est votre type de rendez-vous idéal ?',
        'options': ['Dîner romantique', 'Activité sportive', 'Soirée Netflix', 'Aventure en plein air']
    },
    {
        'question': 'Le plus important dans une relation ?',
        'options': ['La communication', 'La confiance', 'L\'humour', 'L\'aventure']
    },
    {
        'question': 'Animal préféré ?',
        'options': ['🐶 Chien', '🐱 Chat', '🦜 Oiseau', '🐠 Poisson']
    },
    {
        'question': 'Voyage idéal ?',
        'options': ['Plage paradisiaque', 'Ville culturelle', 'Montagne', 'Road trip']
    },
    {
        'question': 'Super-pouvoir choisi ?',
        'options': ['Voler', 'Invisibilité', 'Téléportation', 'Lire les pensées']
    },
    {
        'question': 'Activité du dimanche ?',
        'options': ['Brunch entre amis', 'Sport', 'Série TV', 'Balade nature']
    },
]

def calculate_compatibility(answers1, answers2):
    if not answers1 or not answers2:
        return 0
    matches = sum(1 for a, b in zip(answers1, answers2) if a == b)
    return int((matches / len(answers1)) * 100)
