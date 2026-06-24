"""Counselling page defaults, contact info, and multilingual UI strings."""

COUNSELLOR_PAGE_URL = "https://yvesgashugi.org/find-a-counsellor/"

CONTACT_INFO = {
    "phones": ["+250 789 029 994", "+250 726 756 656", "+250 788 506 517"],
    "email": "info@gashugiyves.org",
    "address_lines": {
        "en": ["Kinyinya, KG 12 Avenue", "Near Pottery Café Kigali"],
        "fr": ["Kinyinya, avenue KG 12", "Près de Pottery Café Kigali"],
        "rw": ["Kinyinya, KG 12 Avenue", "Hafi ya Pottery Café Kigali"],
    },
    "whatsapp_number": "250789029994",
}

COUNSELLOR_SEED = {
    "seed_key": "yves-gashugi",
    "slug": "yves-gashugi",
    "name": {
        "en": "Yves GASHUGI",
        "fr": "Yves GASHUGI",
        "rw": "Yves GASHUGI",
    },
    "role": {
        "en": "Clinical Psychologist specializing in trauma",
        "fr": "Psychologue clinicien spécialisé en traumatismes",
        "rw": "Umukozi w'ubuzima bwo mu mutwe w'umwuga mu bukene",
    },
    "bio": {
        "en": (
            "<p>Yves Gashugi is a clinical psychologist specializing in trauma. He has undergone various short "
            "courses to enhance his expertise in addressing mental health challenges. He is particularly passionate "
            "about a situational issue among believers who occasionally stigmatize mental health difficulties.</p>"
            "<p>His approach involves active listening to individuals facing hardship and collaborating with them "
            "to develop mutual solutions based on the Bible's narration of their challenges.</p>"
            "<p>He believes that every person possesses inner potential, often obscured by life's adversities, "
            "and it is the duty of a counsellor to unveil that potential, allowing victims to see the light.</p>"
        ),
        "fr": (
            "<p>Yves Gashugi est psychologue clinicien spécialisé en traumatismes. Il a suivi diverses formations "
            "courtes pour renforcer son expertise face aux défis de santé mentale. Il est particulièrement sensible "
            "à la stigmatisation occasionnelle des difficultés de santé mentale parmi les croyants.</p>"
            "<p>Son approche repose sur une écoute active des personnes en difficulté et sur une collaboration "
            "pour élaborer des solutions communes fondées sur la narration biblique de leurs défis.</p>"
            "<p>Il croit que chaque personne possède un potentiel intérieur, souvent obscurci par les épreuves, "
            "et qu'il appartient au conseiller de le révéler pour que la personne puisse voir la lumière.</p>"
        ),
        "rw": (
            "<p>Yves Gashugi ni umukozi w'ubuzima bwo mu mutwe w'umwuga mu bukene. Yakoze amahugurwa amake "
            "yo kongera ubuhanga bwe mu gukemura ibibazo by'ubuzima bwo mu mutwe. Arushijeho kwita ku bibazo "
            "by'ivangura mu buzima bwo mu mutwe mu bizera.</p>"
            "<p>Uburyo akoresha burimo kumva neza abahura n'ibibazo no gukorana nabo mu gushaka ibisubizo "
            "bishingiye ku byanditswe mu Bibiliya bijyanye n'ibibazo byabo.</p>"
            "<p>Yizera ko buri muntu afite imbaraga zo mu mutima, zishobora guhishwa n'ibibazo by'ubuzima, "
            "kandi ni inshingano z'umujyanama kuzigaragaza kugira ngo umuntu abone urumuri.</p>"
        ),
    },
    "phone": "+250 789 029 994",
    "email": "info@gashugiyves.org",
}

APPROACH_QUOTE = {
    "en": "Every person possesses inner potential, often obscured by life's adversities.",
    "fr": "Chaque personne possède un potentiel intérieur, souvent obscurci par les épreuves de la vie.",
    "rw": "Buri muntu afite imbaraga zo mu mutima, zishobora guhishwa n'ibibazo by'ubuzima.",
}

SERVICE_CARDS = {
    "en": [
        ("🫶", "Trauma and hardship support", "Compassionate guidance for people carrying pain, loss, or deep distress."),
        ("👂", "Emotional and spiritual listening", "A respectful space to share what you are facing without judgment."),
        ("👨‍👩‍👧", "Family and relationship support", "Help for families and relationships seeking healing and clarity."),
        ("💬", "Mental health stigma awareness", "Support that addresses stigma and encourages honest conversation."),
        ("✝", "Bible-based reflection", "Counselling shaped by Scripture and the hope found in Christ."),
        ("🌱", "Personal growth and restoration", "Encouragement to rediscover strength, purpose, and renewed hope."),
    ],
    "fr": [
        ("🫶", "Soutien face au traumatisme", "Un accompagnement bienveillant pour ceux qui portent douleur, perte ou détresse."),
        ("👂", "Écoute émotionnelle et spirituelle", "Un espace respectueux pour partager ce que vous traversez sans jugement."),
        ("👨‍👩‍👧", "Soutien familial et relationnel", "De l'aide pour les familles et relations en quête de guérison et de clarté."),
        ("💬", "Sensibilisation à la stigmatisation", "Un soutien qui combat la stigmatisation et favorise la parole libre."),
        ("✝", "Réflexion fondée sur la Bible", "Un accompagnement inspiré des Écritures et de l'espérance en Christ."),
        ("🌱", "Croissance personnelle et restauration", "De l'encouragement pour retrouver force, sens et espérance."),
    ],
    "rw": [
        ("🫶", "Gufasha mu bukene n'ibibazo bikomeye", "Ubujyanama bwuje impuhwe ku bantu bahuye n'ububabare cyangwa impfu."),
        ("👂", "Kumva no gushyigikira mu mutima", "Ahantu h'icyubahiro ho gusangiza ibyo uhura nabyo utinya guceceka."),
        ("👨‍👩‍👧", "Gufasha imiryango n'imibanire", "Ubufasha ku miryango n'abantu bashaka gukira no gusobanukirwa."),
        ("💬", "Kurwanya ivangura mu buzima bwo mu mutwe", "Gushyigikira kuvugira ku buzima bwo mu mutwe mu mucyo."),
        ("✝", "Gusuzuma bishingiye kuri Bibiliya", "Ubujyanama bushingiye ku Byanditswe n'icyizere muri Kristo."),
        ("🌱", "Gukura no kugaruka mu mutima", "Gushishikariza kongera kubona imbaraga, intego n'icyizere."),
    ],
}

TRUST_BADGES = {
    "en": [
        "Trauma-informed support",
        "Bible-based guidance",
        "Confidential listening",
        "Personal healing journey",
    ],
    "fr": [
        "Soutien informé par le traumatisme",
        "Accompagnement biblique",
        "Écoute confidentielle",
        "Parcours de guérison personnel",
    ],
    "rw": [
        "Ubufasha bushingiye ku bukene",
        "Ubujyanama bushingiye kuri Bibiliya",
        "Kumva mu ibanga",
        "Urugendo rwo gukira",
    ],
}

FAQ_ITEMS = {
    "en": [
        (
            "Is counselling confidential?",
            "Yes. Your request and conversation are handled with care and appropriate confidentiality.",
        ),
        (
            "Who can request counselling?",
            "Individuals, families, and believers seeking compassionate Christian guidance may reach out.",
        ),
        (
            "Can I book by phone?",
            "Yes. You may call any of the listed numbers or submit the request form on this page.",
        ),
        (
            "Is the counselling Bible-based?",
            "Yes. REC counselling integrates compassionate listening with biblical reflection and hope.",
        ),
        (
            "Can I choose my preferred language?",
            "Yes. You can indicate English, French, or Kinyarwanda when submitting your request.",
        ),
    ],
    "fr": [
        (
            "L'accompagnement est-il confidentiel ?",
            "Oui. Votre demande et vos échanges sont traités avec soin et confidentialité.",
        ),
        (
            "Qui peut demander un accompagnement ?",
            "Les personnes, familles et croyants cherchant un soutien chrétien bienveillant peuvent nous contacter.",
        ),
        (
            "Puis-je réserver par téléphone ?",
            "Oui. Vous pouvez appeler l'un des numéros indiqués ou envoyer le formulaire sur cette page.",
        ),
        (
            "L'accompagnement est-il fondé sur la Bible ?",
            "Oui. L'accompagnement REC associe écoute compatissante et réflexion biblique.",
        ),
        (
            "Puis-je choisir ma langue ?",
            "Oui. Vous pouvez indiquer l'anglais, le français ou le kinyarwanda dans votre demande.",
        ),
    ],
    "rw": [
        (
            "Ubujyanama burimo ibanga?",
            "Yego. Ubusabe bwawe n'ibyo uvuga bitabwaho mu buryo bw'ibanga kandi bucungwa neza.",
        ),
        (
            "Ni nde ushobora gusaba ubujyanama?",
            "Abantu, imiryango n'abizera bashaka ubujyanama bwa Gikristo bwuje impuhwe barashobora kutwandikira.",
        ),
        (
            "Nshobora gusaba kuri telefone?",
            "Yego. Ushobora guhamagara kuri nimero ziri hano cyangwa kohereza ifishi kuri iyi paji.",
        ),
        (
            "Ubujyanama bushingiye kuri Bibiliya?",
            "Yego. Ubujyanama bwa REC buhuza kumva neza n'ibisobanuro bishingiye kuri Bibiliya.",
        ),
        (
            "Nshobora guhitamo ururimi nkunda?",
            "Yego. Ushobora kwerekana icyongereza, igifaransa cyangwa ikinyarwanda mu busabe bwawe.",
        ),
    ],
}

COUNSELLING_UI = {
    "en": {
        "page_title": "Find a Counsellor",
        "hero_eyebrow": "Compassionate Christian care",
        "hero_title": "Find a Counsellor",
        "hero_subtitle": (
            "Receive compassionate, Bible-based counselling support for healing, personal growth, and restored hope."
        ),
        "book_now": "Book Now",
        "learn_about": "Learn About Counselling",
        "how_can_help": "How Counselling Can Help",
        "our_approach": "Our Counselling Approach",
        "approach_intro": (
            "Our counselling approach combines active listening, collaboration, and Bible-based reflection. "
            "We walk with individuals facing hardship, helping them discover practical next steps rooted in faith and hope."
        ),
        "request_heading": "Request Counselling",
        "request_intro": (
            "Tell us a little about what you need. Our team will review your request and contact you using your preferred method."
        ),
        "confidential_request": "Confidential request",
        "submit_request": "Request Counselling",
        "success_message": "Thank you. Your counselling request has been received. Our team will contact you soon.",
        "contact_heading": "Contact & Visit",
        "phone": "Phone",
        "email": "Email",
        "location": "Location",
        "call_now": "Call Now",
        "whatsapp": "WhatsApp",
        "faq_heading": "Frequently asked questions",
        "cta_text": "You do not have to walk through hardship alone.",
        "placeholder_initials": "REC",
        "no_counsellors": "Counsellor profiles will appear here soon.",
    },
    "fr": {
        "page_title": "Trouver un conseiller",
        "hero_eyebrow": "Accompagnement chrétien bienveillant",
        "hero_title": "Trouver un conseiller",
        "hero_subtitle": (
            "Recevez un accompagnement compatissant et biblique pour la guérison, la croissance personnelle et l'espérance retrouvée."
        ),
        "book_now": "Réserver maintenant",
        "learn_about": "En savoir plus sur l'accompagnement",
        "how_can_help": "Comment l'accompagnement peut aider",
        "our_approach": "Notre approche d'accompagnement",
        "approach_intro": (
            "Notre approche associe écoute active, collaboration et réflexion biblique. "
            "Nous accompagnons les personnes en difficulté vers des étapes concrètes fondées sur la foi et l'espérance."
        ),
        "request_heading": "Demander un accompagnement",
        "request_intro": (
            "Dites-nous ce dont vous avez besoin. Notre équipe examinera votre demande et vous contactera selon votre préférence."
        ),
        "confidential_request": "Demande confidentielle",
        "submit_request": "Demander un accompagnement",
        "success_message": "Merci. Votre demande d'accompagnement a été reçue. Notre équipe vous contactera bientôt.",
        "contact_heading": "Contact et visite",
        "phone": "Téléphone",
        "email": "Email",
        "location": "Adresse",
        "call_now": "Appeler",
        "whatsapp": "WhatsApp",
        "faq_heading": "Questions fréquentes",
        "cta_text": "Vous n'avez pas à traverser l'épreuve seul.",
        "placeholder_initials": "REC",
        "no_counsellors": "Les profils de conseillers apparaîtront ici bientôt.",
    },
    "rw": {
        "page_title": "Shaka umujyanama",
        "hero_eyebrow": "Ubujyanama bwa Gikristo bwuje impuhwe",
        "hero_title": "Shaka umujyanama",
        "hero_subtitle": (
            "Akira ubujyanama bwuje impuhwe bushingiye kuri Bibiliya mu gukira, gukura no kongera icyizere."
        ),
        "book_now": "Saba gahunda",
        "learn_about": "Menya ubujyanama",
        "how_can_help": "Uko ubujyanama bwagufasha",
        "our_approach": "Uburyo dukoresha mu bujyanama",
        "approach_intro": (
            "Uburyo dukoresha buhuza kumva neza, gukorana n'abantu n'ibisobanuro bishingiye kuri Bibiliya. "
            "Dugendana n'abahura n'ibibazo tubafasha kubona intambwe zishingiye ku kwizera n'icyizere."
        ),
        "request_heading": "Saba ubujyanama",
        "request_intro": (
            "Tubwire uko twagufasha. Itsinda ryacu rizasuzuma ubusabe bwawe kandi rizakuvugana uko wabishakiye."
        ),
        "confidential_request": "Ubusabe bw'ibanga",
        "submit_request": "Saba ubujyanama",
        "success_message": "Murakoze. Ubusabe bwanyu bwo kubona ubujyanama bwakiriwe. Itsinda ryacu rizabavugana vuba.",
        "contact_heading": "Twandikire / udusure",
        "phone": "Telefone",
        "email": "Email",
        "location": "Aho duherereye",
        "call_now": "Hamagara nonaha",
        "whatsapp": "WhatsApp",
        "faq_heading": "Ibibazo bikunze kubazwa",
        "cta_text": "Ntugomba kwiyangana mu bibazo wenyine.",
        "placeholder_initials": "REC",
        "no_counsellors": "Umwirondoro w'umujyanama uzagaragara hano vuba.",
    },
}

FORM_LABELS = {
    "en": {
        "full_name": "Full name",
        "email": "Email",
        "phone": "Phone",
        "preferred_language": "Preferred language",
        "counselling_type": "Type of support",
        "preferred_contact_method": "Preferred contact method",
        "message": "How can we help?",
    },
    "fr": {
        "full_name": "Nom complet",
        "email": "Email",
        "phone": "Téléphone",
        "preferred_language": "Langue préférée",
        "counselling_type": "Type d'accompagnement",
        "preferred_contact_method": "Mode de contact préféré",
        "message": "Comment pouvons-nous vous aider ?",
    },
    "rw": {
        "full_name": "Amazina yose",
        "email": "Email",
        "phone": "Telefone",
        "preferred_language": "Ururimi ukunda",
        "counselling_type": "Ubwoko bw'ubufasha",
        "preferred_contact_method": "Uburyo bwo kuvugana",
        "message": "Twagufasha dute?",
    },
}

FORM_CHOICES = {
    "en": {
        "preferred_language": [("en", "English"), ("fr", "French"), ("rw", "Kinyarwanda")],
        "counselling_type": [
            ("trauma", "Trauma support"),
            ("spiritual", "Spiritual counselling"),
            ("family", "Family counselling"),
            ("healing", "Healing support"),
            ("general", "General support"),
        ],
        "preferred_contact_method": [
            ("phone", "Phone"),
            ("email", "Email"),
            ("whatsapp", "WhatsApp"),
        ],
    },
    "fr": {
        "preferred_language": [("en", "Anglais"), ("fr", "Français"), ("rw", "Kinyarwanda")],
        "counselling_type": [
            ("trauma", "Soutien face au traumatisme"),
            ("spiritual", "Accompagnement spirituel"),
            ("family", "Accompagnement familial"),
            ("healing", "Soutien à la guérison"),
            ("general", "Soutien général"),
        ],
        "preferred_contact_method": [
            ("phone", "Téléphone"),
            ("email", "Email"),
            ("whatsapp", "WhatsApp"),
        ],
    },
    "rw": {
        "preferred_language": [("en", "Icyongereza"), ("fr", "Igifaransa"), ("rw", "Ikinyarwanda")],
        "counselling_type": [
            ("trauma", "Gufasha mu bukene"),
            ("spiritual", "Ubujyanama bw'umutima w'Imana"),
            ("family", "Ubujyanama bw'umuryango"),
            ("healing", "Gufasha mu gukira"),
            ("general", "Ubufasha rusange"),
        ],
        "preferred_contact_method": [
            ("phone", "Telefone"),
            ("email", "Email"),
            ("whatsapp", "WhatsApp"),
        ],
    },
}


def counselling_ui_for_language(language):
    code = (language or "en").split("-")[0]
    return COUNSELLING_UI.get(code, COUNSELLING_UI["en"])


def form_labels_for_language(language):
    code = (language or "en").split("-")[0]
    return FORM_LABELS.get(code, FORM_LABELS["en"])


def form_choices_for_language(language):
    code = (language or "en").split("-")[0]
    return FORM_CHOICES.get(code, FORM_CHOICES["en"])


def service_cards_for_language(language):
    code = (language or "en").split("-")[0]
    return SERVICE_CARDS.get(code, SERVICE_CARDS["en"])


def trust_badges_for_language(language):
    code = (language or "en").split("-")[0]
    return TRUST_BADGES.get(code, TRUST_BADGES["en"])


def faq_items_for_language(language):
    code = (language or "en").split("-")[0]
    return FAQ_ITEMS.get(code, FAQ_ITEMS["en"])


def approach_quote_for_language(language):
    code = (language or "en").split("-")[0]
    return APPROACH_QUOTE.get(code, APPROACH_QUOTE["en"])


def contact_address_for_language(language):
    code = (language or "en").split("-")[0]
    return CONTACT_INFO["address_lines"].get(code, CONTACT_INFO["address_lines"]["en"])
