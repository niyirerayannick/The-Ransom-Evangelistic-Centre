"""Who we are page UI strings."""

MINISTRY_PATHWAYS = {
    "en": [
        {
            "icon": "✎",
            "title": "Articles & teaching",
            "text": "Gospel-centred writing that helps people understand Scripture and grow in wisdom.",
            "link_label": "Browse articles",
            "link_key": "news",
        },
        {
            "icon": "▤",
            "title": "Books & resources",
            "text": "Long-form Christian resources for deeper learning, discipleship, and ministry.",
            "link_label": "View books",
            "link_key": "books",
        },
        {
            "icon": "♡",
            "title": "Counselling care",
            "text": "Compassionate connections for individuals, families, and leaders seeking guidance.",
            "link_label": "Find a counsellor",
            "link_key": "counsellor",
        },
    ],
    "fr": [
        {
            "icon": "✎",
            "title": "Articles et enseignement",
            "text": "Des écrits centrés sur l’Évangile pour comprendre les Écritures et grandir en sagesse.",
            "link_label": "Parcourir les articles",
            "link_key": "news",
        },
        {
            "icon": "▤",
            "title": "Livres et ressources",
            "text": "Des ressources chrétiennes approfondies pour la formation et le ministère.",
            "link_label": "Voir les livres",
            "link_key": "books",
        },
        {
            "icon": "♡",
            "title": "Accompagnement",
            "text": "Des connexions bienveillantes pour les personnes, familles et responsables en quête de guidance.",
            "link_label": "Trouver un conseiller",
            "link_key": "counsellor",
        },
    ],
    "rw": [
        {
            "icon": "✎",
            "title": "Inyandiko n’inyigisho",
            "text": "Inyandiko zishingiye ku Butumwa Bwiza zifasha gusobanukirwa Ibyanditswe no gukura mu bwenge.",
            "link_label": "Soma inyandiko",
            "link_key": "news",
        },
        {
            "icon": "▤",
            "title": "Ibitabo n’ibikoresho",
            "text": "Ibikoresho by’ubwoko bwa Gikristo byuzuzanya kwiga no gukora umurimo w’ubusugire.",
            "link_label": "Reba ibitabo",
            "link_key": "books",
        },
        {
            "icon": "♡",
            "title": "Ubujyanama",
            "text": "Guhuza abantu n’abafasha mu buryo bwujuje impuhwe ku giti cyabo, mu miryango no mu buyobozi.",
            "link_label": "Shaka umujyanama",
            "link_key": "counsellor",
        },
    ],
}


def ministry_pathways_for_language(language):
    return MINISTRY_PATHWAYS.get(language, MINISTRY_PATHWAYS["en"])
