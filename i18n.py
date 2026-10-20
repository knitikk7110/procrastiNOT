"""
i18n.py  -  languages, country flags and the pickers for procrastiNOT.exe

* Languages: English, Hindi, Marathi, Spanish, French + German, Portuguese, Italian,
  Russian, Turkish, Indonesian, Dutch, Polish (from i18n_extra.py)  (pick in SETTINGS)
* Countries: ~50 with real flag images from the  flags/  folder next to main.py
  (Windows can't draw flag emoji, so flags are shipped as PNG pictures)

How translation works: every label/button in the app passes its text through
translate(). It swaps known English phrases for the chosen language, and leaves
anything it doesn't know in English. To add or fix text, edit the table T below:
    "English phrase": (hindi, marathi, spanish, french),

main.py loads this with:   import i18n; i18n.install(globals(), ProcrastiNotApp)
"""
import os
import re

from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

_MAIN = {}          # main.py's globals (the real dict, so we can swap TECH_FONT etc.)
_APP_DIR = os.getcwd()
_BASE_FONT = ""
CUR = "en"

_NEEDED = ["make_label", "section", "NeonPanel", "NeonButton", "PANEL", "PANEL_ALT",
           "CYAN", "PINK", "GREEN", "YELLOW", "WHITE", "MUTED", "EMOJI_FONT",
           "NAV_IDLE", "NAV_ACTIVE"]

# ------------------------------------------------------------------
# languages
# ------------------------------------------------------------------
def _find_deva_font():
    """Windows 10/11 ships Nirmala UI as Nirmala.ttc (older Windows: .ttf), so look
    for every spelling, ignoring upper/lower case, in the system and user font folders."""
    folders = ["C:/Windows/Fonts"]
    local = os.environ.get("LOCALAPPDATA")
    if local:
        folders.append(os.path.join(local, "Microsoft", "Windows", "Fonts"))
    wanted = ("nirmala.ttc", "nirmalaui.ttc", "nirmala.ttf", "nirmalaui.ttf",
              "mangal.ttf", "aparaj.ttf", "kokila.ttf", "utsaah.ttf")
    for folder in folders:
        try:
            have = {n.lower(): n for n in os.listdir(folder)}
        except OSError:
            continue
        for name in wanted:
            if name in have:
                return os.path.join(folder, have[name])
    return ""


DEVA_FONT = _find_deva_font()

LANGUAGES = {
    "en": dict(name="English", ai="English", idx=None, deva=False),
    "hi": dict(name="हिन्दी", ai="Hindi", idx=0, deva=True),
    "mr": dict(name="मराठी", ai="Marathi", idx=1, deva=True),
    "es": dict(name="Español", ai="Spanish", idx=2, deva=False),
    "fr": dict(name="Français", ai="French", idx=3, deva=False),
}


def available_languages():
    return [c for c, d in LANGUAGES.items() if not d["deva"] or DEVA_FONT]


def lang_font(code):
    if LANGUAGES.get(code, {}).get("deva") and DEVA_FONT:
        return DEVA_FONT
    return _BASE_FONT


# ------------------------------------------------------------------
# countries (flag PNGs live in flags/<code>.png)
# ------------------------------------------------------------------
COUNTRIES = [
    ("IN", "India"), ("US", "United States"), ("GB", "United Kingdom"), ("CA", "Canada"),
    ("AU", "Australia"), ("NZ", "New Zealand"), ("IE", "Ireland"), ("DE", "Germany"),
    ("FR", "France"), ("ES", "Spain"), ("IT", "Italy"), ("PT", "Portugal"),
    ("NL", "Netherlands"), ("BE", "Belgium"), ("CH", "Switzerland"), ("SE", "Sweden"),
    ("NO", "Norway"), ("DK", "Denmark"), ("FI", "Finland"), ("PL", "Poland"),
    ("UA", "Ukraine"), ("RU", "Russia"), ("TR", "Turkey"), ("GR", "Greece"),
    ("BR", "Brazil"), ("AR", "Argentina"), ("MX", "Mexico"), ("CO", "Colombia"),
    ("CL", "Chile"), ("JP", "Japan"), ("CN", "China"), ("KR", "South Korea"),
    ("SG", "Singapore"), ("MY", "Malaysia"), ("ID", "Indonesia"), ("PH", "Philippines"),
    ("VN", "Vietnam"), ("TH", "Thailand"), ("PK", "Pakistan"), ("BD", "Bangladesh"),
    ("LK", "Sri Lanka"), ("NP", "Nepal"), ("AE", "United Arab Emirates"),
    ("SA", "Saudi Arabia"), ("QA", "Qatar"), ("EG", "Egypt"), ("NG", "Nigeria"),
    ("KE", "Kenya"), ("ZA", "South Africa"),
]
_COUNTRY_NAMES = dict(COUNTRIES)

# ------------------------------------------------------------------
# translation table      "English": (Hindi, Marathi, Spanish, French)
# ------------------------------------------------------------------
T = {
    # --- navigation ---
    "PLAYER MENU": ("खिलाड़ी मेन्यू", "खेळाडू मेनू", "MENÚ JUGADOR", "MENU JOUEUR"),
    "HOME": ("होम", "मुख्यपृष्ठ", "INICIO", "ACCUEIL"),
    "MISSIONS": ("मिशन", "मोहिमा", "MISIONES", "MISSIONS"),
    "AI HELPER": ("AI सहायक", "AI मदतनीस", "AYUDA IA", "AIDE IA"),
    "MOOD LAB": ("मूड लैब", "मूड लॅब", "LAB DE ÁNIMO", "LABO HUMEUR"),
    "BADGES": ("बैज", "बॅज", "INSIGNIAS", "BADGES"),
    "INSIGHTS": ("आंकड़े", "आकडेवारी", "ESTADÍSTICAS", "STATS"),
    "ROAST ZONE": ("रोस्ट ज़ोन", "रोस्ट झोन", "ZONA ROAST", "ZONE ROAST"),
    "SETTINGS": ("सेटिंग्स", "सेटिंग्ज", "AJUSTES", "RÉGLAGES"),
    "PROFILE": ("प्रोफ़ाइल", "प्रोफाइल", "PERFIL", "PROFIL"),
    "RANKS": ("रैंक", "क्रमवारी", "RANKING", "CLASSEMENT"),
    # --- header / levels ---
    "YOUR LIFE. YOUR QUEST. YOUR RULES.": ("आपकी ज़िंदगी। आपका क्वेस्ट। आपके नियम।", "तुमचं आयुष्य. तुमचा क्वेस्ट. तुमचे नियम.", "TU VIDA. TU MISIÓN. TUS REGLAS.", "TA VIE. TA QUÊTE. TES RÈGLES."),
    "LEVEL": ("लेवल", "लेव्हल", "NIVEL", "NIVEAU"),
    "LVL": ("लेवल", "लेव्हल", "NIV", "NIV"),
    "TOTAL": ("कुल", "एकूण", "TOTAL", "TOTAL"),
    "day streak": ("दिन की स्ट्रीक", "दिवसांची स्ट्रीक", "días de racha", "jours de série"),
    "Procrastinator Rookie": ("टालमटोल करने वाला नौसिखिया", "चालढकल करणारा नवशिका", "Novato Procrastinador", "Novice Procrastinateur"),
    "Snooze Slayer": ("स्नूज़ संहारक", "स्नूझ संहारक", "Matador de Siestas", "Tueur de Snooze"),
    "Quest Gremlin": ("क्वेस्ट शैतान", "क्वेस्ट खोडकर", "Duende de Misiones", "Gremlin des Quêtes"),
    "Focus Knight": ("फोकस नाइट", "फोकस नाइट", "Caballero del Enfoque", "Chevalier du Focus"),
    "Deadline Dragon-Slayer": ("डेडलाइन ड्रैगन-स्लेयर", "डेडलाइन ड्रॅगन-स्लेयर", "Cazador de Plazos", "Tueur de Deadlines"),
    "Productivity Legend": ("प्रोडक्टिविटी लीजेंड", "प्रोडक्टिव्हिटी लिजेंड", "Leyenda de Productividad", "Légende de Productivité"),
    # --- home ---
    "Hey legend": ("अरे लीजेंड", "अरे लिजेंड", "Hola, leyenda", "Salut, légende"),
    "Good morning, legend. Pick one quest.": ("सुप्रभात, लीजेंड। एक क्वेस्ट चुनो।", "सुप्रभात, लिजेंड. एक क्वेस्ट निवडा.", "Buenos días, leyenda. Elige una misión.", "Bonjour, légende. Choisis une quête."),
    "Good afternoon, legend. Still time to lock in.": ("नमस्ते, लीजेंड। अभी भी फोकस करने का समय है।", "नमस्कार, लिजेंड. अजूनही फोकस करायला वेळ आहे.", "Buenas tardes, leyenda. Aún hay tiempo para concentrarte.", "Bon après-midi, légende. Il est encore temps de te concentrer."),
    "Good evening, legend. One more quest?": ("शुभ संध्या, लीजेंड। एक और क्वेस्ट?", "शुभ संध्याकाळ, लिजेंड. आणखी एक क्वेस्ट?", "Buenas noches, leyenda. ¿Una misión más?", "Bonsoir, légende. Une quête de plus ?"),
    "PLAYER STATUS": ("खिलाड़ी स्थिति", "खेळाडू स्थिती", "ESTADO DEL JUGADOR", "STATUT DU JOUEUR"),
    "NEXT UP": ("अगला", "पुढील", "A CONTINUACIÓN", "À SUIVRE"),
    "QUEST CLEAR RATE": ("क्वेस्ट पूर्णता दर", "क्वेस्ट पूर्ण दर", "TASA DE MISIONES", "TAUX DE QUÊTES"),
    "TODAY'S CHAOS QUEST": ("आज का कैओस क्वेस्ट", "आजचा कॅओस क्वेस्ट", "MISIÓN CAÓTICA DE HOY", "QUÊTE CHAOS DU JOUR"),
    "SYSTEM LOG": ("सिस्टम लॉग", "सिस्टम लॉग", "REGISTRO DEL SISTEMA", "JOURNAL SYSTÈME"),
    "SIDEKICK TIP": ("साथी की सलाह", "साथीदाराची टिप", "CONSEJO DEL AYUDANTE", "CONSEIL DU COMPAGNON"),
    "COMPLETED": ("पूर्ण", "पूर्ण", "COMPLETADAS", "TERMINÉES"),
    "ACTIVE": ("सक्रिय", "सक्रिय", "ACTIVAS", "ACTIVES"),
    "LATEST MOOD": ("ताज़ा मूड", "ताजा मूड", "ÚLTIMO ÁNIMO", "DERNIÈRE HUMEUR"),
    "NO DATA": ("कोई डेटा नहीं", "डेटा नाही", "SIN DATOS", "AUCUNE DONNÉE"),
    "Nothing pending. Suspicious. Add a quest!": ("कुछ भी बाकी नहीं। संदिग्ध। एक क्वेस्ट जोड़ो!", "काहीही बाकी नाही. संशयास्पद. एक क्वेस्ट जोडा!", "Nada pendiente. Sospechoso. ¡Añade una misión!", "Rien en attente. Suspect. Ajoute une quête !"),
    "Nothing pending. Suspicious.": ("कुछ भी बाकी नहीं। संदिग्ध।", "काहीही बाकी नाही. संशयास्पद.", "Nada pendiente. Sospechoso.", "Rien en attente. Suspect."),
    "cleared": ("पूर्ण", "पूर्ण", "completado", "terminées"),
    "quests": ("क्वेस्ट", "क्वेस्ट", "misiones", "quêtes"),
    "add a quest to begin": ("शुरू करने के लिए क्वेस्ट जोड़ो", "सुरुवात करण्यासाठी क्वेस्ट जोडा", "añade una misión para empezar", "ajoute une quête pour commencer"),
    "REROLL": ("दोबारा", "पुन्हा", "OTRA VEZ", "RELANCER"),
    "ACCEPT CHALLENGE (+25 XP)": ("चैलेंज स्वीकारो (+25 XP)", "चॅलेंज स्वीकारा (+25 XP)", "ACEPTAR RETO (+25 XP)", "ACCEPTER LE DÉFI (+25 XP)"),
    "ACCEPTED — NOW GO CLEAR IT": ("स्वीकार किया — अब पूरा करो", "स्वीकारले — आता पूर्ण करा", "ACEPTADO — AHORA CÚMPLELO", "ACCEPTÉ — À TOI DE JOUER"),
    # --- missions ---
    "NEW QUEST": ("नया क्वेस्ट", "नवीन क्वेस्ट", "NUEVA MISIÓN", "NOUVELLE QUÊTE"),
    "Tap here and type your quest…": ("यहाँ टैप करके अपना क्वेस्ट लिखो…", "इथे टॅप करून तुमचा क्वेस्ट लिहा…", "Toca aquí y escribe tu misión…", "Touche ici et écris ta quête…"),
    "Deadline YYYY-MM-DD (optional)": ("डेडलाइन YYYY-MM-DD (वैकल्पिक)", "डेडलाइन YYYY-MM-DD (ऐच्छिक)", "Fecha límite AAAA-MM-DD (opcional)", "Date limite AAAA-MM-JJ (facultatif)"),
    "ADD QUEST": ("क्वेस्ट जोड़ो", "क्वेस्ट जोडा", "AÑADIR MISIÓN", "AJOUTER UNE QUÊTE"),
    "QUEST LOG": ("क्वेस्ट सूची", "क्वेस्ट यादी", "REGISTRO DE MISIONES", "JOURNAL DES QUÊTES"),
    "ALL": ("सभी", "सर्व", "TODAS", "TOUT"),
    "DONE": ("पूर्ण", "पूर्ण", "HECHAS", "FAIT"),
    "LATE": ("देरी", "उशीर", "TARDE", "RETARD"),
    "No deadline = 24 hours from now. Miss it and the roast arrives automatically.": ("बिना डेडलाइन = अभी से 24 घंटे। चूके तो रोस्ट अपने आप आएगा।", "डेडलाइन नाही = आतापासून 24 तास. चुकलात तर रोस्ट आपोआप येईल.", "Sin fecha límite = 24 horas desde ahora. Si fallas, el roast llega solo.", "Pas de date limite = 24 heures à partir de maintenant. Si tu rates, le roast arrive tout seul."),
    "No deadline": ("कोई डेडलाइन नहीं", "डेडलाइन नाही", "Sin fecha límite", "Pas de date limite"),
    "CLEARED": ("पूर्ण", "पूर्ण", "COMPLETADA", "TERMINÉE"),
    "OVERDUE": ("समय सीमा पार", "मुदत संपली", "VENCIDA", "EN RETARD"),
    "BOSS FIGHT": ("बॉस फाइट", "बॉस फाइट", "JEFE FINAL", "COMBAT DE BOSS"),
    "HIGH PRIORITY": ("उच्च प्राथमिकता", "उच्च प्राधान्य", "PRIORIDAD ALTA", "PRIORITÉ HAUTE"),
    "Cleared": ("पूरा किया", "पूर्ण केले", "Completada", "Terminée"),
    "Boss fight": ("बॉस फाइट", "बॉस फाइट", "Jefe final", "Combat de boss"),
    "High": ("उच्च", "उच्च", "Alta", "Haute"),
    "Normal": ("सामान्य", "सामान्य", "Normal", "Normale"),
    "left": ("बाकी", "बाकी", "restante", "restant"),
    "overdue by": ("देरी", "उशीर", "vencida hace", "en retard de"),
    "No quests yet. The empty quest log is judging us both.": ("अभी कोई क्वेस्ट नहीं। खाली सूची हम दोनों को घूर रही है।", "अजून क्वेस्ट नाही. रिकामी यादी आपल्या दोघांकडे बघतेय.", "Aún no hay misiones. El registro vacío nos juzga a los dos.", "Pas encore de quêtes. Le journal vide nous juge tous les deux."),
    "Nothing here. Try another tab.": ("यहाँ कुछ नहीं। दूसरा टैब आज़माओ।", "इथे काही नाही. दुसरा टॅब वापरून पहा.", "Nada aquí. Prueba otra pestaña.", "Rien ici. Essaie un autre onglet."),
    # --- AI helper ---
    "AI SIDEKICK // QUEST HELPER": ("AI साथी // क्वेस्ट सहायक", "AI साथीदार // क्वेस्ट मदतनीस", "AYUDANTE IA // AYUDA DE MISIONES", "COMPAGNON IA // AIDE AUX QUÊTES"),
    "FOCUS": ("फोकस", "फोकस", "ENFOQUE", "FOCUS"),
    "STOP": ("रोको", "थांबवा", "PARAR", "STOP"),
    "BREAK IT DOWN": ("टुकड़ों में बाँटो", "तुकड्यांत विभागा", "DESGLÓSALO", "DÉCOMPOSE-LE"),
    "25-MIN PLAN": ("25-मिनट योजना", "25-मिनिटांची योजना", "PLAN DE 25 MIN", "PLAN 25 MIN"),
    "EXPLAIN IT": ("समझाओ", "समजावून सांगा", "EXPLÍCALO", "EXPLIQUE"),
    "PEP TALK": ("हौसला बढ़ाओ", "प्रोत्साहन द्या", "ÁNIMO", "MOTIVATION"),
    "GOOGLE IT": ("गूगल करो", "गूगल करा", "BUSCA EN GOOGLE", "GOOGLE-LE"),
    "SEND": ("भेजो", "पाठवा", "ENVIAR", "ENVOYER"),
    "Ask anything about your quest…": ("अपने क्वेस्ट के बारे में कुछ भी पूछो…", "तुमच्या क्वेस्टबद्दल काहीही विचारा…", "Pregunta lo que quieras sobre tu misión…", "Demande ce que tu veux sur ta quête…"),
    "YOU //": ("आप //", "तुम्ही //", "TÚ //", "TOI //"),
    "AI // SIDEKICK": ("AI // साथी", "AI // साथीदार", "IA // AYUDANTE", "IA // COMPAGNON"),
    "thinking…": ("सोच रहा है…", "विचार करत आहे…", "pensando…", "réflexion…"),
    "AI ONLINE": ("AI ऑनलाइन", "AI ऑनलाइन", "IA EN LÍNEA", "IA EN LIGNE"),
    "OFFLINE HELPER": ("ऑफ़लाइन सहायक", "ऑफलाइन मदतनीस", "AYUDA SIN CONEXIÓN", "AIDE HORS LIGNE"),
    "Yo! I'm your AI sidekick. Pick a focus quest above (or tap 🤖 on any quest), hit a chip, or ask me anything. I'll help you finish faster.": (
        "अरे! मैं तुम्हारा AI साथी हूँ। ऊपर से एक फोकस क्वेस्ट चुनो (या किसी क्वेस्ट पर 🤖 दबाओ), कोई चिप दबाओ, या कुछ भी पूछो। मैं तुम्हें जल्दी पूरा करने में मदद करूँगा।",
        "अरे! मी तुमचा AI साथीदार. वरून फोकस क्वेस्ट निवडा (किंवा कोणत्याही क्वेस्टवरील 🤖 दाबा), चिप दाबा किंवा काहीही विचारा. मी तुम्हाला लवकर पूर्ण करायला मदत करेन.",
        "¡Eh! Soy tu ayudante IA. Elige una misión de enfoque arriba (o toca 🤖 en cualquier misión), pulsa un chip o pregúntame lo que quieras. Te ayudo a terminar más rápido.",
        "Yo ! Je suis ton compagnon IA. Choisis une quête de focus ci-dessus (ou touche 🤖 sur une quête), appuie sur une puce ou demande-moi n'importe quoi. Je t'aide à finir plus vite."),
    # --- mood ---
    "SYSTEM CHECK: HOW ARE YOU?": ("सिस्टम चेक: आप कैसे हो?", "सिस्टम चेक: तुम्ही कसे आहात?", "REVISIÓN: ¿CÓMO ESTÁS?", "CONTRÔLE : COMMENT ÇA VA ?"),
    "Focused": ("एकाग्र", "एकाग्र", "Concentrado", "Concentré"),
    "Good": ("अच्छा", "छान", "Bien", "Bien"),
    "Okay": ("ठीक", "ठीक", "Normal", "Moyen"),
    "Stressed": ("तनाव में", "तणावात", "Estresado", "Stressé"),
    "Tired": ("थका हुआ", "थकलेला", "Cansado", "Fatigué"),
    "Low": ("उदास", "खिन्न", "Decaído", "Bas"),
    "LOG MOOD": ("मूड दर्ज करो", "मूड नोंदवा", "GUARDAR ÁNIMO", "ENREGISTRER L'HUMEUR"),
    "Your wellbeing matters more than your XP.": ("तुम्हारी भलाई तुम्हारे XP से ज़्यादा ज़रूरी है।", "तुमचं आरोग्य तुमच्या XP पेक्षा महत्त्वाचं आहे.", "Tu bienestar importa más que tu XP.", "Ton bien-être compte plus que ton XP."),
    "RECENT CHECK-INS": ("हाल की एंट्री", "अलीकडील नोंदी", "REGISTROS RECIENTES", "DERNIERS BILANS"),
    "Your mood history will appear here.": ("तुम्हारा मूड इतिहास यहाँ दिखेगा।", "तुमचा मूड इतिहास इथे दिसेल.", "Tu historial de ánimo aparecerá aquí.", "Ton historique d'humeur apparaîtra ici."),
    "No mood logs yet.": ("अभी कोई मूड दर्ज नहीं।", "अजून मूड नोंद नाही.", "Aún no hay registros de ánimo.", "Pas encore d'humeur enregistrée."),
    "No moods logged yet.": ("अभी कोई मूड दर्ज नहीं।", "अजून मूड नोंद नाही.", "Aún no hay ánimos registrados.", "Aucune humeur enregistrée."),
    # --- badges ---
    "ACHIEVEMENTS & BADGES": ("उपलब्धियाँ और बैज", "कामगिरी आणि बॅज", "LOGROS E INSIGNIAS", "SUCCÈS ET BADGES"),
    "unlocked": ("अनलॉक", "अनलॉक", "desbloqueadas", "débloqués"),
    "First Quest": ("पहला क्वेस्ट", "पहिला क्वेस्ट", "Primera misión", "Première quête"),
    "Clear your first quest": ("अपना पहला क्वेस्ट पूरा करो", "तुमचा पहिला क्वेस्ट पूर्ण करा", "Completa tu primera misión", "Termine ta première quête"),
    "Quest Gremlin (5)": ("क्वेस्ट शैतान (5)", "क्वेस्ट खोडकर (5)", "Duende de Misiones (5)", "Gremlin des Quêtes (5)"),
    "Clear 5 quests": ("5 क्वेस्ट पूरे करो", "5 क्वेस्ट पूर्ण करा", "Completa 5 misiones", "Termine 5 quêtes"),
    "Double Digits (10)": ("डबल डिजिट (10)", "डबल डिजिट (10)", "Doble Dígito (10)", "Double Chiffre (10)"),
    "Clear 10 quests": ("10 क्वेस्ट पूरे करो", "10 क्वेस्ट पूर्ण करा", "Completa 10 misiones", "Termine 10 quêtes"),
    "Main Character (25)": ("मुख्य किरदार (25)", "मुख्य पात्र (25)", "Protagonista (25)", "Personnage Principal (25)"),
    "Clear 25 quests": ("25 क्वेस्ट पूरे करो", "25 क्वेस्ट पूर्ण करा", "Completa 25 misiones", "Termine 25 quêtes"),
    "Level Up": ("लेवल अप", "लेव्हल अप", "Subir de Nivel", "Niveau Supérieur"),
    "Reach 100 XP": ("100 XP तक पहुँचो", "100 XP गाठा", "Alcanza 100 XP", "Atteins 100 XP"),
    "XP Machine": ("XP मशीन", "XP मशीन", "Máquina de XP", "Machine à XP"),
    "Reach 500 XP": ("500 XP तक पहुँचो", "500 XP गाठा", "Alcanza 500 XP", "Atteins 500 XP"),
    "3-Day Streak": ("3-दिन स्ट्रीक", "3-दिवस स्ट्रीक", "Racha de 3 días", "Série de 3 jours"),
    "Clear quests 3 days in a row": ("लगातार 3 दिन क्वेस्ट पूरे करो", "सलग 3 दिवस क्वेस्ट पूर्ण करा", "Completa misiones 3 días seguidos", "Termine des quêtes 3 jours d'affilée"),
    "Mood Check-In Pro": ("मूड चेक-इन प्रो", "मूड चेक-इन प्रो", "Experto en Chequeo de Ánimo", "Pro du Bilan d'Humeur"),
    "Log 5 moods": ("5 मूड दर्ज करो", "5 मूड नोंदवा", "Registra 5 ánimos", "Enregistre 5 humeurs"),
    # --- insights ---
    "ARCADE INSIGHTS": ("आर्केड आंकड़े", "आर्केड आकडेवारी", "ESTADÍSTICAS ARCADE", "STATS ARCADE"),
    "TOTAL XP": ("कुल XP", "एकूण XP", "XP TOTAL", "XP TOTAL"),
    "BEST STREAK": ("सर्वश्रेष्ठ स्ट्रीक", "सर्वोत्तम स्ट्रीक", "MEJOR RACHA", "MEILLEURE SÉRIE"),
    "CLEAR RATE": ("पूर्णता दर", "पूर्ण दर", "TASA DE ÉXITO", "TAUX DE RÉUSSITE"),
    "MOOD LOGS": ("मूड एंट्री", "मूड नोंदी", "REGISTROS DE ÁNIMO", "BILANS D'HUMEUR"),
    "LAST 7 DAYS": ("पिछले 7 दिन", "गेले 7 दिवस", "ÚLTIMOS 7 DÍAS", "7 DERNIERS JOURS"),
    "MOOD MIX": ("मूड मिश्रण", "मूड मिश्रण", "MEZCLA DE ÁNIMO", "MIX D'HUMEUR"),
    "STREAK": ("स्ट्रीक", "स्ट्रीक", "RACHA", "SÉRIE"),
    "Complete a quest to start building your stats.": ("आंकड़े बनाने के लिए एक क्वेस्ट पूरा करो।", "आकडेवारी तयार करण्यासाठी एक क्वेस्ट पूर्ण करा.", "Completa una misión para empezar tus estadísticas.", "Termine une quête pour construire tes stats."),
    "day(s) in a row": ("दिन लगातार", "दिवस सलग", "día(s) seguidos", "jour(s) d'affilée"),
    "mood log(s)": ("मूड एंट्री", "मूड नोंदी", "registro(s) de ánimo", "bilan(s) d'humeur"),
    # --- roast zone ---
    "UNHINGED SIDEKICK": ("बेलगाम साथी", "बेफाम साथीदार", "AYUDANTE DESQUICIADO", "COMPAGNON DÉJANTÉ"),
    "GENERATE A QUESTIONABLE EXCUSE": ("एक बेतुका बहाना बनाओ", "एक भन्नाट बहाणा तयार करा", "GENERA UNA EXCUSA DUDOSA", "GÉNÈRE UNE EXCUSE DOUTEUSE"),
    "ROAST ME": ("मुझे रोस्ट करो", "मला रोस्ट करा", "ASÁDAME", "ROAST-MOI"),
    "PROCRASTINATION METER": ("टालमटोल मीटर", "चालढकल मीटर", "MEDIDOR DE PROCRASTINACIÓN", "COMPTEUR DE PROCRASTINATION"),
    "HALL OF SHAME": ("शर्मिंदगी की दीवार", "लाजिरवाणी भिंत", "SALÓN DE LA VERGÜENZA", "MUR DE LA HONTE"),
    "Nobody in the hall of shame. Respect.": ("शर्मिंदगी की दीवार पर कोई नहीं। सम्मान।", "लाजिरवाण्या भिंतीवर कोणी नाही. आदर.", "Nadie en el salón de la vergüenza. Respeto.", "Personne au mur de la honte. Respect."),
    "Zero overdue quests. Suspiciously responsible.": ("एक भी क्वेस्ट लेट नहीं। संदिग्ध रूप से ज़िम्मेदार।", "एकही क्वेस्ट उशिरा नाही. संशयास्पद जबाबदार.", "Cero misiones vencidas. Sospechosamente responsable.", "Zéro quête en retard. Suspectement responsable."),
    "Loading today's questionable life advice...": ("आज की संदिग्ध ज़िंदगी सलाह लोड हो रही है...", "आजचा संशयास्पद आयुष्य सल्ला लोड होत आहे...", "Cargando el dudoso consejo de vida de hoy...", "Chargement du conseil de vie douteux du jour..."),
    # --- settings ---
    "SOUND: ON": ("आवाज़: चालू", "आवाज: चालू", "SONIDO: SÍ", "SON : OUI"),
    "SOUND: OFF": ("आवाज़: बंद", "आवाज: बंद", "SONIDO: NO", "SON : NON"),
    "AI KEY (OPTIONAL OVERRIDE)": ("AI कुंजी (वैकल्पिक)", "AI की (ऐच्छिक)", "CLAVE IA (OPCIONAL)", "CLÉ IA (FACULTATIF)"),
    "SAVE KEY": ("कुंजी सहेजो", "की सेव्ह करा", "GUARDAR CLAVE", "ENREGISTRER LA CLÉ"),
    "CLEAR KEY": ("कुंजी हटाओ", "की काढा", "BORRAR CLAVE", "EFFACER LA CLÉ"),
    "TEST AI CONNECTION": ("AI कनेक्शन जाँचो", "AI कनेक्शन तपासा", "PROBAR CONEXIÓN IA", "TESTER LA CONNEXION IA"),
    "Paste your API key…": ("अपनी API कुंजी पेस्ट करो…", "तुमची API की पेस्ट करा…", "Pega tu clave API…", "Colle ta clé API…"),
    "ABOUT": ("जानकारी", "माहिती", "ACERCA DE", "À PROPOS"),
    "LANGUAGE & REGION": ("भाषा और क्षेत्र", "भाषा आणि प्रदेश", "IDIOMA Y REGIÓN", "LANGUE ET RÉGION"),
    "LANGUAGE": ("भाषा", "भाषा", "IDIOMA", "LANGUE"),
    "COUNTRY": ("देश", "देश", "PAÍS", "PAYS"),
    "Choose language": ("भाषा चुनो", "भाषा निवडा", "Elegir idioma", "Choisir la langue"),
    "Choose country": ("देश चुनो", "देश निवडा", "Elegir país", "Choisir le pays"),
    "No country": ("कोई देश नहीं", "देश नाही", "Sin país", "Aucun pays"),
    "CLOSE": ("बंद करो", "बंद करा", "CERRAR", "FERMER"),
    # --- profile + leaderboard ---
    "PLAYER PROFILE": ("खिलाड़ी प्रोफ़ाइल", "खेळाडू प्रोफाइल", "PERFIL DEL JUGADOR", "PROFIL DU JOUEUR"),
    "EDIT PROFILE": ("प्रोफ़ाइल बदलो", "प्रोफाइल बदला", "EDITAR PERFIL", "MODIFIER LE PROFIL"),
    "Avatar": ("अवतार", "अवतार", "Avatar", "Avatar"),
    "Username (3-16 letters, numbers or _)": ("यूज़रनेम (3-16 अक्षर, अंक या _)", "युजरनेम (3-16 अक्षरे, अंक किंवा _)", "Usuario (3-16 letras, números o _)", "Pseudo (3-16 lettres, chiffres ou _)"),
    "e.g. QuestGremlin42": ("जैसे QuestGremlin42", "उदा. QuestGremlin42", "p. ej. QuestGremlin42", "ex. QuestGremlin42"),
    "SAVE + JOIN BOARD": ("सहेजो + बोर्ड जॉइन करो", "सेव्ह करा + बोर्डमध्ये सामील व्हा", "GUARDAR + UNIRSE", "ENREGISTRER + REJOINDRE"),
    "LEAVE BOARD": ("बोर्ड छोड़ो", "बोर्ड सोडा", "SALIR DEL RANKING", "QUITTER LE CLASSEMENT"),
    "GLOBAL LEADERBOARD": ("ग्लोबल लीडरबोर्ड", "ग्लोबल लीडरबोर्ड", "RANKING GLOBAL", "CLASSEMENT MONDIAL"),
    "REFRESH": ("रिफ्रेश", "रिफ्रेश", "ACTUALIZAR", "ACTUALISER"),
    "MY PROFILE": ("मेरी प्रोफ़ाइल", "माझी प्रोफाइल", "MI PERFIL", "MON PROFIL"),
    "WORLD": ("दुनिया", "जग", "MUNDO", "MONDE"),
    "MY COUNTRY": ("मेरा देश", "माझा देश", "MI PAÍS", "MON PAYS"),
    "(no username yet)": ("(अभी यूज़रनेम नहीं)", "(अजून युजरनेम नाही)", "(sin usuario aún)", "(pas encore de pseudo)"),
    "RANK": ("रैंक", "क्रमांक", "PUESTO", "RANG"),
    "unranked": ("बिना रैंक", "क्रमांक नाही", "sin clasificar", "non classé"),
    "Not on the leaderboard yet. Pick a username!": ("अभी लीडरबोर्ड पर नहीं हो। यूज़रनेम चुनो!", "अजून लीडरबोर्डवर नाही. युजरनेम निवडा!", "Aún no estás en el ranking. ¡Elige un usuario!", "Pas encore au classement. Choisis un pseudo !"),
    "Nobody here yet. Be the first on the board!": ("यहाँ अभी कोई नहीं। बोर्ड पर पहले बनो!", "इथे अजून कोणी नाही. बोर्डवर पहिले व्हा!", "Nadie aún. ¡Sé el primero del ranking!", "Personne pour l'instant. Sois le premier !"),
    "Pick a username in PROFILE to join the board.": ("बोर्ड जॉइन करने के लिए PROFILE में यूज़रनेम चुनो।", "बोर्डमध्ये सामील होण्यासाठी PROFILE मध्ये युजरनेम निवडा.", "Elige un usuario en PERFIL para unirte al ranking.", "Choisis un pseudo dans PROFIL pour rejoindre le classement."),
    "Pick a country first (PROFILE or SETTINGS).": ("पहले देश चुनो (PROFILE या SETTINGS)।", "आधी देश निवडा (PROFILE किंवा SETTINGS).", "Elige primero un país (PERFIL o AJUSTES).", "Choisis d'abord un pays (PROFIL ou RÉGLAGES)."),
    "Loading the board…": ("बोर्ड लोड हो रहा है…", "बोर्ड लोड होत आहे…", "Cargando el ranking…", "Chargement du classement…"),
    "players shown": ("खिलाड़ी दिखाए गए", "खेळाडू दाखवले", "jugadores mostrados", "joueurs affichés"),
    "updated": ("अपडेट", "अपडेट", "actualizado", "mis à jour"),
    "Synced": ("सिंक हुआ", "सिंक झाले", "Sincronizado", "Synchronisé"),
    "Shared with the leaderboard: username, avatar, country, XP, level, quests cleared, best streak.": ("लीडरबोर्ड के साथ साझा: यूज़रनेम, अवतार, देश, XP, लेवल, पूरे क्वेस्ट, सर्वश्रेष्ठ स्ट्रीक।", "लीडरबोर्डसोबत शेअर: युजरनेम, अवतार, देश, XP, लेव्हल, पूर्ण क्वेस्ट, सर्वोत्तम स्ट्रीक.", "Compartido con el ranking: usuario, avatar, país, XP, nivel, misiones completadas, mejor racha.", "Partagé avec le classement : pseudo, avatar, pays, XP, niveau, quêtes terminées, meilleure série."),
    "Your quests, moods and AI chats never leave this PC.": ("तुम्हारे क्वेस्ट, मूड और AI चैट इस PC से बाहर नहीं जाते।", "तुमचे क्वेस्ट, मूड आणि AI चॅट या PC बाहेर जात नाहीत.", "Tus misiones, ánimos y chats de IA nunca salen de este PC.", "Tes quêtes, humeurs et discussions IA ne quittent jamais ce PC."),
    "LEAVE BOARD deletes your row from the server.": ("बोर्ड छोड़ने पर सर्वर से तुम्हारी एंट्री हट जाती है।", "बोर्ड सोडल्यास सर्व्हरवरून तुमची नोंद हटवली जाते.", "SALIR DEL RANKING borra tu fila del servidor.", "QUITTER LE CLASSEMENT supprime ta ligne du serveur."),
}

# ------------------------------------------------------------------
# translate()
# ------------------------------------------------------------------
# extra languages (German, Portuguese, Italian, Russian, Turkish, Indonesian, Dutch,
# Polish) live in i18n_extra.py. If that file is missing the app still works.
EXTRA = {}
try:
    import i18n_extra
    EXTRA = i18n_extra.build(list(T.keys()))
    for _code, _name, _ai in i18n_extra.LANGS:
        if _code in EXTRA:
            LANGUAGES[_code] = dict(name=_name, ai=_ai, idx=None, deva=False, ex=True)
except Exception:
    EXTRA = {}

_PAT = None


def _pattern():
    global _PAT
    if _PAT is None:
        parts = []
        for key in sorted(T, key=len, reverse=True):
            p = re.escape(key)
            if key[0].isalnum():
                p = r"(?<![A-Za-z0-9])" + p
            if key[-1].isalnum():
                p += r"(?![A-Za-z0-9])"
            parts.append(p)
        _PAT = re.compile("|".join(parts))
    return _PAT


def translate(text, code=None):
    code = code or CUR
    info = LANGUAGES.get(code)
    if not text or info is None:
        return text
    if info.get("ex"):
        table = EXTRA.get(code)
        if not table:
            return text
        return _pattern().sub(lambda m: table.get(m.group(0), m.group(0)), str(text))
    if info["idx"] is None:
        return text
    idx = info["idx"]
    return _pattern().sub(lambda m: T[m.group(0)][idx], str(text))


def _rewrap_i18n(widget, value):
    """Replaces main.py's _rewrap: remember the English text, show the translated one."""
    if widget._busy:
        return
    widget._src = value
    wrapped = _MAIN["tech_markup"](translate(value))
    if wrapped != value:
        widget._busy = True
        try:
            widget.text = wrapped
        finally:
            widget._busy = False


# ------------------------------------------------------------------
# widgets (defined after install() injects NeonPanel & friends)
# ------------------------------------------------------------------
PickerRow = None


def _define_classes():
    global PickerRow

    class _PickerRow(ButtonBehavior, NeonPanel):
        """Tappable row: [flag] text  >"""

        def __init__(self, **kw):
            super().__init__(orientation="horizontal", padding=[dp(10), dp(4)], spacing=dp(10),
                             size_hint_y=None, height=dp(48), bg_color=PANEL_ALT,
                             border_color=(0.0, 0.95, 1.0, 0.5), **kw)
            self.flag = Image(size_hint=(None, 1), width=dp(44), fit_mode="contain")
            self.text_lbl = Label(font_name=_MAIN["TECH_FONT"], font_size="13sp", bold=True,
                                  color=WHITE, halign="left", valign="middle")
            self.text_lbl.bind(size=lambda i, _s: setattr(i, "text_size", (i.width, i.height)))
            arrow = Label(text=">", font_name=_MAIN["TECH_FONT"], color=MUTED, size_hint_x=None,
                          width=dp(18), bold=True)
            self.add_widget(self.flag)
            self.add_widget(self.text_lbl)
            self.add_widget(arrow)

    PickerRow = _PickerRow


# ------------------------------------------------------------------
# app methods (attached to the app class by install())
# ------------------------------------------------------------------
class RegionMixin:
    # ----- flags -----
    def flag_path(self, code):
        base = os.path.join(_APP_DIR, "flags")
        path = os.path.join(base, (code or "world").lower() + ".png")
        if os.path.exists(path):
            return path
        return os.path.join(base, "world.png")

    def make_flag(self, code, width=None):
        return Image(source=self.flag_path(code), size_hint=(None, 1),
                     width=width or dp(36), fit_mode="contain")

    def set_flag(self, img, code):
        img.source = self.flag_path(code)

    def country_name(self, code):
        return _COUNTRY_NAMES.get(code, "")

    # ----- AI replies in the chosen language -----
    def ai_language_note(self):
        code = getattr(self, "lang", "en")
        if code == "en" or code not in LANGUAGES:
            return ""
        return f"\nIMPORTANT: Always reply in {LANGUAGES[code]['ai']}."

    # ----- picker rows (settings + profile) -----
    def make_country_row(self):
        row = PickerRow()
        row.bind(on_release=self.open_country_picker)
        if not hasattr(self, "_country_rows"):
            self._country_rows = []
        self._country_rows.append(row)
        self.refresh_region()
        return row

    def make_lang_row(self):
        row = PickerRow()
        row.flag.opacity = 0
        row.flag.width = 0
        row.bind(on_release=self.open_language_picker)
        if not hasattr(self, "_lang_rows"):
            self._lang_rows = []
        self._lang_rows.append(row)
        self.refresh_region()
        return row

    def build_region_section(self, body):
        body.add_widget(section("🌐 LANGUAGE & REGION", CYAN))
        body.add_widget(make_label("LANGUAGE", 11, MUTED, True, size_hint_y=None, height=dp(22)))
        body.add_widget(self.make_lang_row())
        body.add_widget(make_label("COUNTRY", 11, MUTED, True, size_hint_y=None, height=dp(22)))
        body.add_widget(self.make_country_row())

    def refresh_region(self):
        code = getattr(self, "lang", "en")
        country = getattr(self, "country", "")
        for row in getattr(self, "_country_rows", []):
            self.set_flag(row.flag, country)
            row.text_lbl.font_name = lang_font(CUR)
            row.text_lbl.text = self.country_name(country) or translate("No country")
        for row in getattr(self, "_lang_rows", []):
            row.text_lbl.font_name = lang_font(code)
            row.text_lbl.text = LANGUAGES.get(code, LANGUAGES["en"])["name"]

    # ----- country popup -----
    def open_country_picker(self, *_):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))
        sv = ScrollView(do_scroll_x=False, bar_width=dp(8), bar_color=CYAN)
        grid = GridLayout(cols=2, spacing=dp(6), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        for code, name in [("", "")] + COUNTRIES:
            row = PickerRow()
            row.height = dp(44)
            self.set_flag(row.flag, code)
            row.text_lbl.font_name = lang_font(CUR)
            row.text_lbl.text = name or translate("No country")
            row.bind(on_release=lambda _r, c=code: self._pick_country(c, popup))
            grid.add_widget(row)
        sv.add_widget(grid)
        content.add_widget(sv)
        close = NeonButton(text="CLOSE", bg_color=(0.20, 0.15, 0.45, 1))
        close.size_hint_y = None
        close.height = dp(40)
        content.add_widget(close)
        popup = Popup(title=translate("Choose country"), title_font=lang_font(CUR),
                      content=content, size_hint=(0.92, 0.92),
                      separator_color=CYAN, background_color=PANEL)
        close.bind(on_press=popup.dismiss)
        popup.open()

    def _pick_country(self, code, popup):
        popup.dismiss()
        self.country = code
        self.save_data()
        self.refresh_region()
        if hasattr(self, "refresh_profile"):
            self.refresh_profile()
        if hasattr(self, "render_leaderboard"):
            self.render_leaderboard()
        self.set_status((self.country_name(code) or translate("No country")) + " ✔", GREEN)
        self.play_sound("success")

    # ----- language popup -----
    def open_language_picker(self, *_):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))
        sv = ScrollView(do_scroll_x=False, bar_width=dp(8), bar_color=CYAN)
        lst = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        lst.bind(minimum_height=lst.setter("height"))
        for code in available_languages():
            row = PickerRow()
            row.flag.opacity = 0
            row.flag.width = 0
            row.text_lbl.font_name = lang_font(code)
            row.text_lbl.text = LANGUAGES[code]["name"]
            row.text_lbl.font_size = "16sp"
            row.bind(on_release=lambda _r, c=code: self._pick_language(c, popup))
            lst.add_widget(row)
        if not DEVA_FONT:
            lst.add_widget(make_label("Hindi / Marathi need a Devanagari font (Nirmala UI) on Windows.",
                                      10, MUTED, auto_height=True))
        sv.add_widget(lst)
        content.add_widget(sv)
        close = NeonButton(text="CLOSE", bg_color=(0.20, 0.15, 0.45, 1))
        close.size_hint_y = None
        close.height = dp(40)
        content.add_widget(close)
        popup = Popup(title=translate("Choose language"), title_font=lang_font(CUR),
                      content=content, size_hint=(0.8, 0.9),
                      separator_color=CYAN, background_color=PANEL)
        close.bind(on_press=popup.dismiss)
        popup.open()

    def _pick_language(self, code, popup):
        popup.dismiss()
        self.lang = code
        self.save_data()
        self.apply_language()
        self.set_status(LANGUAGES[code]["name"] + " ✔", GREEN)
        self.play_sound("success")

    # ----- apply the language to every widget -----
    def apply_language(self):
        global CUR
        code = getattr(self, "lang", "en")
        if code not in available_languages():
            code = "en"
            self.lang = "en"
        CUR = code
        font = lang_font(code)
        _MAIN["TECH_FONT"] = font          # labels/inputs created from now on use this font
        tech_markup = _MAIN["tech_markup"]

        roots = list(Window.children)
        if hasattr(self, "pages"):
            roots += list(self.pages.screens)
        seen = set()
        for root in roots:
            for w in root.walk(restrict=False):
                if id(w) in seen:
                    continue
                seen.add(id(w))
                if getattr(w, "_no_i18n", False):
                    continue
                if hasattr(w, "_src") and hasattr(w, "_busy"):      # TechLabel / NeonButton
                    w.font_name = font
                    w._busy = True
                    try:
                        w.text = tech_markup(translate(w._src))
                    finally:
                        w._busy = False
                elif isinstance(w, TextInput):
                    if not hasattr(w, "_hint_src"):
                        w._hint_src = w.hint_text
                    w.hint_text = translate(w._hint_src)
                    w.font_name = font

        for opt in getattr(self, "mood_options", []):                 # plain-Label mood tiles
            opt.name_label.font_name = font
            opt.name_label.text = translate(opt.mood)

        self.refresh_region()
        if hasattr(self, "refresh_screen"):
            self.refresh_screen()
        if hasattr(self, "refresh_profile"):
            self.refresh_profile()
        if hasattr(self, "render_leaderboard"):
            self.render_leaderboard()


def install(ns, app_cls):
    """Called from main.py: hooks the translator in and attaches the new methods."""
    global _MAIN, _APP_DIR, _BASE_FONT
    _MAIN = ns
    _BASE_FONT = ns["TECH_FONT"]
    try:
        _APP_DIR = os.path.dirname(os.path.abspath(ns["__file__"]))
    except Exception:
        _APP_DIR = os.getcwd()
    for name in _NEEDED:
        globals()[name] = ns[name]
    _define_classes()
    ns["_rewrap"] = _rewrap_i18n                  # every label/button now goes through translate()
    for name, fn in RegionMixin.__dict__.items():
        if callable(fn) and not name.startswith("__"):
            setattr(app_cls, name, fn)