"""Donation page defaults and Google Form URL."""

GOOGLE_DONATION_FORM_URL = (
    "https://docs.google.com/forms/d/e/1FAIpQLSeizwf7YwX9iCv0Is-mTcjDdEY6vyAZfdtSumT_3vwtoRFN7Q/viewform"
)

DONATION_PROGRAMS = [
    {
        "slug": "articles-writing",
        "icon": "✎",
        "order": 10,
        "title": {
            "en": "Articles Writing",
            "fr": "Rédaction d'articles",
            "rw": "Kwandika inyandiko",
        },
        "description": {
            "en": (
                "<p>We kindly request your support in donating towards our articles writing initiative.</p>"
                "<p>While our authors are committed to sharing Bible-based articles freely, to maintain the high "
                "quality of our articles, we conduct thorough reviews, ensuring accuracy, clarity, and alignment "
                "with our mission. However, these reviews sometimes incur costs, and this is where your support "
                "becomes invaluable.</p>"
                "<p>We appreciate your generosity and assure you that your contribution will directly contribute "
                "to the continued creation and review of impactful content. Thank you for supporting our mission.</p>"
            ),
            "fr": (
                "<p>Nous vous demandons aimablement de soutenir notre initiative de rédaction d'articles.</p>"
                "<p>Nos auteurs partagent gratuitement des articles fondés sur la Bible, mais pour maintenir une "
                "haute qualité, nous effectuons des révisions approfondies qui garantissent l'exactitude, la clarté "
                "et l'alignement avec notre mission. Ces révisions entraînent parfois des coûts, et c'est là que "
                "votre soutien devient précieux.</p>"
                "<p>Nous apprécions votre générosité et vous assurons que votre contribution soutiendra directement "
                "la création et la révision de contenus percutants. Merci de soutenir notre mission.</p>"
            ),
            "rw": (
                "<p>Turagusaba inkunga mu gikorwa cyacu cyo kwandika inyandiko.</p>"
                "<p>Abanditsi bacu bagomba gusangiza ku buntu inyandiko zishingiye kuri Bibiliya, ariko kugira ngo "
                "tuzigume zifite ireme, dukora isuzuma rikomeye rigenga ukuri, kugaragaza neza no kujyana n'intego "
                "yacu. Ibi ushobora kugera ku biciro, aho inkunga yawe iba ingenzi.</p>"
                "<p>Turashimira ubuntu bwawe kandi twemeza ko inkunga yawe izafasha mu gukomeza gukora no gusuzuma "
                "ibikubiye mu nyandiko zifite ingaruka. Murakoze gushyigikira umurimo wacu.</p>"
            ),
        },
    },
    {
        "slug": "healing-activities",
        "icon": "♡",
        "order": 20,
        "title": {
            "en": "Healing Activities",
            "fr": "Activités de guérison",
            "rw": "Ibikorwa byo gukiza imitima",
        },
        "description": {
            "en": (
                "<p>We are passionate about healing activities that empower and support individuals facing hardships. "
                "Our community engagements and capacity-building sessions for believers cover essential topics related "
                "to healing.</p>"
                "<p>To ensure the success of these impactful activities, we incur costs for materials, facilitation "
                "fees for our dedicated trainers, and refreshments for attendees. While we are committed to providing "
                "support free of charge, events of this nature often require additional assistance.</p>"
                "<p>Your donation will directly contribute to covering these essential costs, enabling us to continue "
                "offering these services and making a positive impact on the lives of those in need.</p>"
            ),
            "fr": (
                "<p>Nous sommes passionnés par les activités de guérison qui renforcent et soutiennent les personnes "
                "qui traversent des difficultés. Nos engagements communautaires et nos sessions de renforcement des "
                "capacités pour les croyants couvrent des sujets essentiels liés à la guérison.</p>"
                "<p>Pour assurer le succès de ces activités, nous avons des coûts pour le matériel, l'animation de "
                "nos formateurs et les rafraîchissements pour les participants. Bien que nous nous engagions à offrir "
                "un soutien gratuit, ce type d'événements nécessite souvent une aide supplémentaire.</p>"
                "<p>Votre don contribuera directement à couvrir ces coûts essentiels et nous permettra de continuer "
                "à offrir ces services et à avoir un impact positif sur la vie de ceux qui en ont besoin.</p>"
            ),
            "rw": (
                "<p>Dushishikajwe n'ibikorwa byo gukiza imitima bigira imbaraga no gufasha abahura n'ibibazo. "
                "Ibikorwa byacu byo mu muryango n'amahugurwa y'abizera akora ku ngingo z'ingenzi zijyanye no gukiza.</p>"
                "<p>Kugira ngo ibi bikorwa bigire ingaruka, dukoresha amafaranga mu bikoresho, honorar y'abahugura "
                "n'ibinyobwa ku bitabiriye. Nubwo twiyemeje gutanga ubufasha ku buntu, ibi bikorwa bisaba inkunga y'inyongera.</p>"
                "<p>Inkunga yawe izafasha mu kwishyura ayo mafaranga akomeye kandi ikadufasha gukomeza gutanga ubu bufasha "
                "no kugira ingaruka nziza ku buzima bw'abakeneye.</p>"
            ),
        },
    },
]

DONATION_METHODS = [
    {
        "key": "equity-rwf",
        "name": "Equity Bank (RWF)",
        "method_type": "bank",
        "bank_name": "Equity Bank",
        "account_name": "The Ransom Evangelistic Centre",
        "account_number": "4012100493038",
        "currency": "RWF",
        "icon": "🏦",
        "order": 10,
        "instructions_en": "Use your full name as the payment reference when transferring to this RWF account.",
        "instructions_fr": "Utilisez votre nom complet comme référence lors du virement vers ce compte RWF.",
        "instructions_rw": "Koresha amazina yawe yuzuye nk'inyandiko igenewe iyo konti ya RWF.",
    },
    {
        "key": "equity-usd",
        "name": "Equity Bank (USD)",
        "method_type": "bank",
        "bank_name": "Equity Bank",
        "account_name": "The Ransom Evangelistic Centre",
        "account_number": "4015112436468",
        "currency": "USD",
        "icon": "🏦",
        "order": 20,
        "instructions_en": "Use your full name as the payment reference when transferring to this USD account.",
        "instructions_fr": "Utilisez votre nom complet comme référence lors du virement vers ce compte USD.",
        "instructions_rw": "Koresha amazina yawe yuzuye nk'inyandiko igenewe iyo konti ya USD.",
    },
    {
        "key": "momo-pay",
        "name": "MoMo Pay",
        "method_type": "mobile_money",
        "mobile_money_number": "*182*8*1*635190*Frw#",
        "currency": "RWF",
        "icon": "📱",
        "order": 30,
        "instructions_en": "Dial the MoMo Pay code on your phone and follow the prompts to complete your donation.",
        "instructions_fr": "Composez le code MoMo Pay sur votre téléphone et suivez les instructions pour finaliser votre don.",
        "instructions_rw": "Kanda kode ya MoMo Pay kuri telefone yawe ukurikize amabwiriza yo kurangiza gutanga inkunga.",
    },
]

IMPACT_ITEMS = {
    "en": [
        "Support Bible-based articles",
        "Help content review and publication",
        "Support healing activities",
        "Help community engagement",
        "Strengthen Gospel-centered teaching",
    ],
    "fr": [
        "Soutenir des articles fondés sur la Bible",
        "Aider à la révision et à la publication",
        "Soutenir les activités de guérison",
        "Aider l'engagement communautaire",
        "Renforcer l'enseignement centré sur l'Évangile",
    ],
    "rw": [
        "Gushyigikira inyandiko zishingiye kuri Bibiliya",
        "Gufasha isuzuma no gutangaza ibikubiye mu nyandiko",
        "Gushyigikira ibikorwa byo gukiza imitima",
        "Gufasha ibikorwa byo mu muryango",
        "Gukomeza inyigisho zishingiye ku Butumwa Bwiza",
    ],
}

FAQ_ITEMS = {
    "en": [
        ("Where does my donation go?", "Your gift supports article writing, review, and healing activities according to the program you choose."),
        ("Can I donate monthly?", "Yes. Select Monthly, Quarterly, or Annually in the donation pledge form."),
        ("Can I donate by Mobile Money?", "Yes. Use MoMo Pay or select Mobile Money in the pledge form."),
        ("Can I donate by bank transfer?", "Yes. Use our Equity Bank RWF or USD accounts listed on this page."),
    ],
    "fr": [
        ("Où va mon don ?", "Votre don soutient la rédaction d'articles, la révision et les activités de guérison selon le programme choisi."),
        ("Puis-je donner chaque mois ?", "Oui. Choisissez Mensuel, Trimestriel ou Annuel dans le formulaire."),
        ("Puis-je donner par Mobile Money ?", "Oui. Utilisez MoMo Pay ou sélectionnez Mobile Money dans le formulaire."),
        ("Puis-je donner par virement bancaire ?", "Oui. Utilisez nos comptes Equity Bank RWF ou USD indiqués sur cette page."),
    ],
    "rw": [
        ("Inkunga yanjye igana he?", "Inkunga yawe ishishikaza kwandika inyandiko, isuzuma n'ibikorwa byo gukiza imitima uhitamo."),
        ("Nshobora gutanga buri kwezi?", "Yego. Hitamo Buri kwezi, Buri gihembwe cyangwa Buri mwaka mu ifishi."),
        ("Nshobora gutanga ukoresheje Mobile Money?", "Yego. Koresha MoMo Pay cyangwa uhitemo Mobile Money mu ifishi."),
        ("Nshobora gutanga ukoresheje banki?", "Yego. Koresha konti za Equity Bank RWF cyangwa USD ziri kuri iyi paji."),
    ],
}

DONATE_UI = {
    "en": {
        "page_title": "Donate",
        "give_with_purpose": "Give with purpose",
        "hero_title": "Support Our Mission",
        "hero_subtitle": (
            "Partner with us to support Bible-based article writing, healing activities, "
            "and Gospel-centered community impact."
        ),
        "donate_now": "Donate Now",
        "view_payment_methods": "View Payment Methods",
        "why_donate": "Why donate?",
        "where_gift_goes": "Where your gift goes",
        "donation_programs": "Donation Programs",
        "programs_empty": "Donation programs will appear here.",
        "support_both": "Support Both Programs",
        "your_impact": "Your impact",
        "ways_to_give": "Ways to give",
        "payment_methods": "Payment Methods",
        "methods_empty": "Payment methods will be published here.",
        "copied": "Copied to clipboard",
        "donation_pledge": "Donation pledge",
        "form_heading": "Tell us how you would like to give",
        "form_intro": (
            "Submitting this form records your intention to give. "
            "It does not process a payment online."
        ),
        "google_form_title": "Google Donation Form",
        "google_form_intro": (
            "Prefer the existing Google Form? You can complete your donation pledge there instead."
        ),
        "open_google_form": "Open Google Form",
        "need_help": "Need help?",
        "need_help_text": (
            "Contact the REC team if you need assistance with bank transfer, MoMo Pay, or your pledge."
        ),
        "faq_heading": "Frequently asked questions",
        "cta_text": (
            "Your support helps us continue sharing wisdom, salvation, and empowerment "
            "through Gospel-centered work."
        ),
        "modal_title": "Choose how to donate",
        "modal_intro": "Complete your pledge on this website or use the Google Donation Form.",
        "modal_website": "Fill donation form on this website",
        "modal_website_hint": "Submit a pledge to the REC team",
        "modal_google": "Open Google Donation Form",
        "modal_google_hint": "Opens in a new tab",
        "donate_articles": "Donate to Articles Writing",
        "donate_healing": "Donate to Healing Activities",
        "submit_pledge": "Submit Donation Pledge",
        "bank": "Bank",
        "account_name": "Account name",
        "account": "Account",
        "copy": "Copy",
        "momo_pay": "MoMo Pay",
        "success_message": (
            "Thank you for your donation pledge. Our team will contact you if needed with next steps."
        ),
    },
    "fr": {
        "page_title": "Faire un don",
        "give_with_purpose": "Donner avec un but",
        "hero_title": "Soutenez notre mission",
        "hero_subtitle": (
            "Associez-vous à nous pour soutenir la rédaction d'articles bibliques, "
            "les activités de guérison et l'impact communautaire centré sur l'Évangile."
        ),
        "donate_now": "Donner maintenant",
        "view_payment_methods": "Méthodes de paiement",
        "why_donate": "Pourquoi faire un don ?",
        "where_gift_goes": "Où va votre don",
        "donation_programs": "Programmes de don",
        "programs_empty": "Les programmes de don apparaîtront ici.",
        "support_both": "Soutenir les deux programmes",
        "your_impact": "Votre impact",
        "ways_to_give": "Façons de donner",
        "payment_methods": "Méthodes de paiement",
        "methods_empty": "Les méthodes de paiement seront publiées ici.",
        "copied": "Copié dans le presse-papiers",
        "donation_pledge": "Promesse de don",
        "form_heading": "Dites-nous comment vous souhaitez donner",
        "form_intro": (
            "Ce formulaire enregistre votre intention de donner. "
            "Il ne traite pas le paiement en ligne."
        ),
        "google_form_title": "Formulaire Google de don",
        "google_form_intro": (
            "Vous préférez le formulaire Google existant ? Vous pouvez y compléter votre promesse de don."
        ),
        "open_google_form": "Ouvrir le formulaire Google",
        "need_help": "Besoin d'aide ?",
        "need_help_text": (
            "Contactez l'équipe REC si vous avez besoin d'aide pour le virement bancaire, MoMo Pay ou votre promesse."
        ),
        "faq_heading": "Questions fréquentes",
        "cta_text": (
            "Votre soutien nous aide à continuer de partager la sagesse, le salut et l'autonomisation "
            "par un travail centré sur l'Évangile."
        ),
        "modal_title": "Choisissez comment donner",
        "modal_intro": "Complétez votre promesse sur ce site ou utilisez le formulaire Google.",
        "modal_website": "Remplir le formulaire sur ce site",
        "modal_website_hint": "Envoyer une promesse de don à l'équipe REC",
        "modal_google": "Ouvrir le formulaire Google de don",
        "modal_google_hint": "S'ouvre dans un nouvel onglet",
        "donate_articles": "Donner pour la rédaction d'articles",
        "donate_healing": "Donner pour les activités de guérison",
        "submit_pledge": "Soumettre une promesse de don",
        "bank": "Banque",
        "account_name": "Nom du compte",
        "account": "Compte",
        "copy": "Copier",
        "momo_pay": "MoMo Pay",
        "success_message": (
            "Merci pour votre promesse de don. Notre équipe vous contactera si nécessaire pour la suite."
        ),
    },
    "rw": {
        "page_title": "Tanga inkunga",
        "give_with_purpose": "Tanga inkunga ufite intego",
        "hero_title": "Shyigikira umurimo wacu",
        "hero_subtitle": (
            "Dufatanye mu gushyigikira kwandika inyandiko zishingiye kuri Bibiliya, "
            "ibikorwa byo gukiza imitima n'ingaruka zishingiye ku Butumwa Bwiza mu muryango."
        ),
        "donate_now": "Tanga inkunga nonaha",
        "view_payment_methods": "Uburyo bwo kwishyura",
        "why_donate": "Kuki utanga inkunga?",
        "where_gift_goes": "Inkunga yawe igana he",
        "donation_programs": "Ibikorwa byo gutera inkunga",
        "programs_empty": "Ibikorwa byo gutera inkunga bizagaragara hano.",
        "support_both": "Shyigikira ibikorwa byombi",
        "your_impact": "Ingaruka yawe",
        "ways_to_give": "Uburyo bwo gutanga",
        "payment_methods": "Uburyo bwo kwishyura",
        "methods_empty": "Uburyo bwo kwishyura buzashyirwa hano.",
        "copied": "Byanditswe mu gikapo",
        "donation_pledge": "Icyifuzo cyo gutanga inkunga",
        "form_heading": "Tubwire uko ushaka gutanga",
        "form_intro": (
            "Kuzuza iyi fishi byandika icyifuzo cyawe cyo gutanga inkunga. "
            "Ntibishyura kuri interineti."
        ),
        "google_form_title": "Ifishi ya Google yo gutanga inkunga",
        "google_form_intro": (
            "Ukunda ifishi ya Google? Ushobora kuzuza icyifuzo cyawe cyo gutanga inkunga aho."
        ),
        "open_google_form": "Fungura ifishi ya Google",
        "need_help": "Ukeneye ubufasha?",
        "need_help_text": (
            "Vugana n'itsinda rya REC niba ukeneye ubufasha mu kwishyura kuri banki, MoMo Pay cyangwa icyifuzo cyawe."
        ),
        "faq_heading": "Ibibazo bikunze kubazwa",
        "cta_text": (
            "Inkunga yawe idufasha gukomeza gusangiza ubwenge, agakiza n'imbaraga "
            "binyuze mu murimo ushingiye ku Butumwa Bwiza."
        ),
        "modal_title": "Hitamo uko watanga inkunga",
        "modal_intro": "Zuza icyifuzo kuri ubu rubuga cyangwa ukoreshe ifishi ya Google.",
        "modal_website": "Zuza ifishi kuri ubu rubuga",
        "modal_website_hint": "Ohereza icyifuzo ku itsinda rya REC",
        "modal_google": "Fungura ifishi ya Google yo gutanga inkunga",
        "modal_google_hint": "Ifunguka mu gice gishya",
        "donate_articles": "Tera inkunga mu kwandika inyandiko",
        "donate_healing": "Tera inkunga mu bikorwa byo gukiza imitima",
        "submit_pledge": "Ohereza icyifuzo cyo gutanga inkunga",
        "bank": "Banki",
        "account_name": "Izina rya konti",
        "account": "Konti",
        "copy": "Koporora",
        "momo_pay": "MoMo Pay",
        "success_message": (
            "Murakoze ku cyifuzo cyanyu cyo gutanga inkunga. Itsinda ryacu rizabavugana niba bikenewe."
        ),
    },
}

FORM_LABELS = {
    "en": {
        "full_name": "Full Names",
        "email": "Email",
        "telephone": "Telephone",
        "program_to_donate": "Program to donate",
        "amount": "Amount",
        "currency": "Currency",
        "donation_commitment": "Donation Commitment",
        "payment_gateway": "Payment Gateway",
        "feedback": "Feedback",
    },
    "fr": {
        "full_name": "Noms complets",
        "email": "Email",
        "telephone": "Téléphone",
        "program_to_donate": "Programme à soutenir",
        "amount": "Montant",
        "currency": "Devise",
        "donation_commitment": "Engagement de don",
        "payment_gateway": "Mode de paiement",
        "feedback": "Message / commentaire",
    },
    "rw": {
        "full_name": "Amazina yose",
        "email": "Email",
        "telephone": "Telefone",
        "program_to_donate": "Igikorwa ushaka gutera inkunga",
        "amount": "Amafaranga",
        "currency": "Ifaranga",
        "donation_commitment": "Igihe cyo gutanga inkunga",
        "payment_gateway": "Uburyo bwo kwishyura",
        "feedback": "Igitekerezo / ubutumwa",
    },
}

FORM_CHOICES = {
    "en": {
        "program_to_donate": [
            ("articles_writing", "Articles Writing"),
            ("healing_activities", "Healing activities"),
            ("both", "Both"),
        ],
        "donation_commitment": [
            ("one_time", "One time"),
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("annually", "Annually"),
        ],
        "payment_gateway": [
            ("cash", "Cash"),
            ("mobile_money", "Mobile Money"),
            ("bank_transfer", "Bank Transfer"),
        ],
    },
    "fr": {
        "program_to_donate": [
            ("articles_writing", "Rédaction d'articles"),
            ("healing_activities", "Activités de guérison"),
            ("both", "Les deux"),
        ],
        "donation_commitment": [
            ("one_time", "Une fois"),
            ("monthly", "Mensuel"),
            ("quarterly", "Trimestriel"),
            ("annually", "Annuel"),
        ],
        "payment_gateway": [
            ("cash", "Espèces"),
            ("mobile_money", "Mobile Money"),
            ("bank_transfer", "Virement bancaire"),
        ],
    },
    "rw": {
        "program_to_donate": [
            ("articles_writing", "Kwandika inyandiko"),
            ("healing_activities", "Ibikorwa byo gukiza imitima"),
            ("both", "Byombi"),
        ],
        "donation_commitment": [
            ("one_time", "Inshuro imwe"),
            ("monthly", "Buri kwezi"),
            ("quarterly", "Buri gihembwe"),
            ("annually", "Buri mwaka"),
        ],
        "payment_gateway": [
            ("cash", "Amafaranga mu ntoki"),
            ("mobile_money", "Mobile Money"),
            ("bank_transfer", "Kohereza kuri banki"),
        ],
    },
}


def donate_ui_for_language(language):
    code = (language or "en").split("-")[0]
    return DONATE_UI.get(code, DONATE_UI["en"])


def form_labels_for_language(language):
    code = (language or "en").split("-")[0]
    return FORM_LABELS.get(code, FORM_LABELS["en"])


def form_choices_for_language(language):
    code = (language or "en").split("-")[0]
    return FORM_CHOICES.get(code, FORM_CHOICES["en"])

