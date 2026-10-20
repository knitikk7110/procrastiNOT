# -*- coding: utf-8 -*-
"""
i18n_extra.py - 8 more languages for procrastiNOT.exe (German, Portuguese,
Italian, Russian, Turkish, Indonesian, Dutch, Polish).

Keep this file next to i18n.py. Each language is a list of lines "N|text",
where N is the position of the English phrase in the table T inside i18n.py
(0 = "PLAYER MENU" ... 172 = "LEAVE BOARD deletes your row from the server.").
A language whose list is incomplete is simply skipped, so it can never crash
the app.
"""

LANGS = [
    ("de", "Deutsch", "German"),
    ("pt", "Português", "Portuguese"),
    ("it", "Italiano", "Italian"),
    ("ru", "Русский", "Russian"),
    ("tr", "Türkçe", "Turkish"),
    ("id", "Bahasa Indonesia", "Indonesian"),
    ("nl", "Nederlands", "Dutch"),
    ("pl", "Polski", "Polish"),
]

_RAW = {}

_RAW["de"] = """
0|SPIELERMENÜ
1|START
2|MISSIONEN
3|KI-HELFER
4|STIMMUNGSLABOR
5|ABZEICHEN
6|STATISTIK
7|ROAST-ZONE
8|EINSTELLUNGEN
9|PROFIL
10|RANGLISTE
11|DEIN LEBEN. DEINE QUEST. DEINE REGELN.
12|LEVEL
13|LVL
14|GESAMT
15|Tage Serie
16|Aufschieber-Neuling
17|Schlummer-Bezwinger
18|Quest-Kobold
19|Fokus-Ritter
20|Deadline-Drachentöter
21|Produktivitätslegende
22|Hey Legende
23|Guten Morgen, Legende. Wähl eine Quest.
24|Guten Tag, Legende. Noch Zeit, dich zu fokussieren.
25|Guten Abend, Legende. Noch eine Quest?
26|SPIELERSTATUS
27|ALS NÄCHSTES
28|QUEST-ERFOLGSQUOTE
29|HEUTIGE CHAOS-QUEST
30|SYSTEMPROTOKOLL
31|SIDEKICK-TIPP
32|ERLEDIGT
33|AKTIV
34|LETZTE STIMMUNG
35|KEINE DATEN
36|Nichts offen. Verdächtig. Füge eine Quest hinzu!
37|Nichts offen. Verdächtig.
38|erledigt
39|Quests
40|füge eine Quest hinzu, um zu starten
41|NEU WÜRFELN
42|HERAUSFORDERUNG ANNEHMEN (+25 XP)
43|ANGENOMMEN — JETZT ERLEDIGEN
44|NEUE QUEST
45|Tippe hier und schreibe deine Quest…
46|Deadline JJJJ-MM-TT (optional)
47|QUEST HINZUFÜGEN
48|QUEST-LOGBUCH
49|ALLE
50|FERTIG
51|SPÄT
52|Keine Deadline = 24 Stunden ab jetzt. Verpasst du sie, kommt der Roast automatisch.
53|Keine Deadline
54|ERLEDIGT
55|ÜBERFÄLLIG
56|BOSSKAMPF
57|HOHE PRIORITÄT
58|Erledigt
59|Bosskampf
60|Hoch
61|Normal
62|übrig
63|überfällig seit
64|Noch keine Quests. Das leere Logbuch verurteilt uns beide.
65|Hier ist nichts. Probier einen anderen Tab.
66|KI-SIDEKICK // QUEST-HELFER
67|FOKUS
68|STOPP
69|AUFTEILEN
70|25-MIN-PLAN
71|ERKLÄR'S MIR
72|MOTIVATION
73|GOOGLE ES
74|SENDEN
75|Frag alles zu deiner Quest…
76|DU //
77|KI // SIDEKICK
78|denkt nach…
79|KI ONLINE
80|OFFLINE-HELFER
81|Yo! Ich bin dein KI-Sidekick. Wähle oben eine Fokus-Quest (oder tippe bei einer Quest auf 🤖), drück einen Chip oder frag mich irgendwas. Ich helfe dir, schneller fertig zu werden.
82|SYSTEMCHECK: WIE GEHT'S DIR?
83|Fokussiert
84|Gut
85|Okay
86|Gestresst
87|Müde
88|Niedergeschlagen
89|STIMMUNG SPEICHERN
90|Dein Wohlbefinden ist wichtiger als deine XP.
91|LETZTE CHECK-INS
92|Dein Stimmungsverlauf erscheint hier.
93|Noch keine Stimmungseinträge.
94|Noch keine Stimmungen erfasst.
95|ERFOLGE & ABZEICHEN
96|freigeschaltet
97|Erste Quest
98|Erledige deine erste Quest
99|Quest-Kobold (5)
100|Erledige 5 Quests
101|Zweistellig (10)
102|Erledige 10 Quests
103|Hauptfigur (25)
104|Erledige 25 Quests
105|Level-Up
106|Erreiche 100 XP
107|XP-Maschine
108|Erreiche 500 XP
109|3-Tage-Serie
110|Erledige Quests 3 Tage in Folge
111|Stimmungs-Check-in-Profi
112|Erfasse 5 Stimmungen
113|ARCADE-STATISTIK
114|GESAMT-XP
115|BESTE SERIE
116|ERFOLGSQUOTE
117|STIMMUNGSEINTRÄGE
118|LETZTE 7 TAGE
119|STIMMUNGSMIX
120|SERIE
121|Erledige eine Quest, um deine Statistik aufzubauen.
122|Tag(e) in Folge
123|Stimmungseintrag/-einträge
124|DURCHGEKNALLTER SIDEKICK
125|EINE FRAGWÜRDIGE AUSREDE ERZEUGEN
126|ROAST MICH
127|PROKRASTINATIONS-METER
128|WALL OF SHAME
129|Niemand in der Wall of Shame. Respekt.
130|Null überfällige Quests. Verdächtig verantwortungsbewusst.
131|Lade heutigen fragwürdigen Lebensrat...
132|TON: AN
133|TON: AUS
134|KI-SCHLÜSSEL (OPTIONALE ÜBERSCHREIBUNG)
135|SCHLÜSSEL SPEICHERN
136|SCHLÜSSEL LÖSCHEN
137|KI-VERBINDUNG TESTEN
138|API-Schlüssel einfügen…
139|INFO
140|SPRACHE & REGION
141|SPRACHE
142|LAND
143|Sprache wählen
144|Land wählen
145|Kein Land
146|SCHLIESSEN
147|SPIELERPROFIL
148|PROFIL BEARBEITEN
149|Avatar
150|Benutzername (3–16 Buchstaben, Zahlen oder _)
151|z. B. QuestGremlin42
152|SPEICHERN + BEITRETEN
153|RANGLISTE VERLASSEN
154|GLOBALE RANGLISTE
155|AKTUALISIEREN
156|MEIN PROFIL
157|WELT
158|MEIN LAND
159|(noch kein Benutzername)
160|RANG
161|ohne Rang
162|Noch nicht in der Rangliste. Wähle einen Benutzernamen!
163|Noch niemand hier. Sei der Erste in der Rangliste!
164|Wähle im PROFIL einen Benutzernamen, um beizutreten.
165|Wähle zuerst ein Land (PROFIL oder EINSTELLUNGEN).
166|Rangliste wird geladen…
167|Spieler angezeigt
168|aktualisiert
169|Synchronisiert
170|Mit der Rangliste geteilt: Benutzername, Avatar, Land, XP, Level, erledigte Quests, beste Serie.
171|Deine Quests, Stimmungen und KI-Chats verlassen nie diesen PC.
172|RANGLISTE VERLASSEN löscht deine Zeile vom Server.
"""

_RAW["pt"] = """
0|MENU DO JOGADOR
1|INÍCIO
2|MISSÕES
3|AJUDA IA
4|LAB DE HUMOR
5|EMBLEMAS
6|ESTATÍSTICAS
7|ZONA ROAST
8|CONFIGURAÇÕES
9|PERFIL
10|RANKING
11|SUA VIDA. SUA MISSÃO. SUAS REGRAS.
12|NÍVEL
13|NÍV
14|TOTAL
15|dias de sequência
16|Procrastinador Novato
17|Matador de Soneca
18|Gremlin das Missões
19|Cavaleiro do Foco
20|Mata-Dragão de Prazos
21|Lenda da Produtividade
22|E aí, lenda
23|Bom dia, lenda. Escolha uma missão.
24|Boa tarde, lenda. Ainda dá tempo de focar.
25|Boa noite, lenda. Mais uma missão?
26|STATUS DO JOGADOR
27|A SEGUIR
28|TAXA DE MISSÕES
29|MISSÃO CAÓTICA DE HOJE
30|REGISTRO DO SISTEMA
31|DICA DO PARCEIRO
32|CONCLUÍDAS
33|ATIVAS
34|ÚLTIMO HUMOR
35|SEM DADOS
36|Nada pendente. Suspeito. Adicione uma missão!
37|Nada pendente. Suspeito.
38|concluídas
39|missões
40|adicione uma missão para começar
41|SORTEAR
42|ACEITAR DESAFIO (+25 XP)
43|ACEITO — AGORA CUMPRA
44|NOVA MISSÃO
45|Toque aqui e digite sua missão…
46|Prazo AAAA-MM-DD (opcional)
47|ADICIONAR MISSÃO
48|DIÁRIO DE MISSÕES
49|TODAS
50|FEITAS
51|ATRASADAS
52|Sem prazo = 24 horas a partir de agora. Se perder, o roast chega sozinho.
53|Sem prazo
54|CONCLUÍDA
55|ATRASADA
56|CHEFE FINAL
57|PRIORIDADE ALTA
58|Concluída
59|Chefe final
60|Alta
61|Normal
62|restante
63|atrasada há
64|Nenhuma missão ainda. O diário vazio está nos julgando.
65|Nada aqui. Tente outra aba.
66|PARCEIRO IA // AJUDA DE MISSÕES
67|FOCO
68|PARAR
69|DIVIDA EM PASSOS
70|PLANO DE 25 MIN
71|EXPLIQUE
72|MOTIVAÇÃO
73|PESQUISE NO GOOGLE
74|ENVIAR
75|Pergunte qualquer coisa sobre sua missão…
76|VOCÊ //
77|IA // PARCEIRO
78|pensando…
79|IA ONLINE
80|AJUDA OFFLINE
81|E aí! Sou seu parceiro de IA. Escolha uma missão de foco acima (ou toque em 🤖 em qualquer missão), clique num chip ou me pergunte qualquer coisa. Eu ajudo você a terminar mais rápido.
82|VERIFICAÇÃO: COMO VOCÊ ESTÁ?
83|Focado
84|Bem
85|Mais ou menos
86|Estressado
87|Cansado
88|Para baixo
89|SALVAR HUMOR
90|Seu bem-estar importa mais que seu XP.
91|CHECK-INS RECENTES
92|Seu histórico de humor aparecerá aqui.
93|Nenhum registro de humor ainda.
94|Nenhum humor registrado ainda.
95|CONQUISTAS E EMBLEMAS
96|desbloqueados
97|Primeira missão
98|Conclua sua primeira missão
99|Gremlin das Missões (5)
100|Conclua 5 missões
101|Dois Dígitos (10)
102|Conclua 10 missões
103|Personagem Principal (25)
104|Conclua 25 missões
105|Subir de Nível
106|Alcance 100 XP
107|Máquina de XP
108|Alcance 500 XP
109|Sequência de 3 dias
110|Conclua missões 3 dias seguidos
111|Mestre do Check-in de Humor
112|Registre 5 humores
113|ESTATÍSTICAS ARCADE
114|XP TOTAL
115|MELHOR SEQUÊNCIA
116|TAXA DE CONCLUSÃO
117|REGISTROS DE HUMOR
118|ÚLTIMOS 7 DIAS
119|MISTURA DE HUMOR
120|SEQUÊNCIA
121|Conclua uma missão para começar suas estatísticas.
122|dia(s) seguidos
123|registro(s) de humor
124|PARCEIRO DESCONTROLADO
125|GERAR UMA DESCULPA DUVIDOSA
126|ME ZOA
127|MEDIDOR DE PROCRASTINAÇÃO
128|MURAL DA VERGONHA
129|Ninguém no mural da vergonha. Respeito.
130|Zero missões atrasadas. Suspeitamente responsável.
131|Carregando o conselho de vida duvidoso de hoje...
132|SOM: LIGADO
133|SOM: DESLIGADO
134|CHAVE IA (SUBSTITUIÇÃO OPCIONAL)
135|SALVAR CHAVE
136|APAGAR CHAVE
137|TESTAR CONEXÃO IA
138|Cole sua chave de API…
139|SOBRE
140|IDIOMA E REGIÃO
141|IDIOMA
142|PAÍS
143|Escolher idioma
144|Escolher país
145|Sem país
146|FECHAR
147|PERFIL DO JOGADOR
148|EDITAR PERFIL
149|Avatar
150|Usuário (3-16 letras, números ou _)
151|ex.: QuestGremlin42
152|SALVAR + ENTRAR NO RANKING
153|SAIR DO RANKING
154|RANKING GLOBAL
155|ATUALIZAR
156|MEU PERFIL
157|MUNDO
158|MEU PAÍS
159|(ainda sem usuário)
160|POSIÇÃO
161|sem posição
162|Você ainda não está no ranking. Escolha um usuário!
163|Ninguém aqui ainda. Seja o primeiro do ranking!
164|Escolha um usuário em PERFIL para entrar no ranking.
165|Escolha um país primeiro (PERFIL ou CONFIGURAÇÕES).
166|Carregando o ranking…
167|jogadores exibidos
168|atualizado
169|Sincronizado
170|Compartilhado com o ranking: usuário, avatar, país, XP, nível, missões concluídas, melhor sequência.
171|Suas missões, humores e chats de IA nunca saem deste PC.
172|SAIR DO RANKING apaga sua linha do servidor.
"""

_RAW["it"] = """
0|MENU GIOCATORE
1|HOME
2|MISSIONI
3|AIUTO IA
4|LAB UMORE
5|BADGE
6|STATISTICHE
7|ZONA ROAST
8|IMPOSTAZIONI
9|PROFILO
10|CLASSIFICA
11|LA TUA VITA. LA TUA MISSIONE. LE TUE REGOLE.
12|LIVELLO
13|LIV
14|TOTALE
15|giorni di serie
16|Procrastinatore Principiante
17|Cacciatore di Snooze
18|Gremlin delle Missioni
19|Cavaliere del Focus
20|Ammazzadraghi delle Scadenze
21|Leggenda della Produttività
22|Ehi, leggenda
23|Buongiorno, leggenda. Scegli una missione.
24|Buon pomeriggio, leggenda. C'è ancora tempo per concentrarti.
25|Buonasera, leggenda. Un'altra missione?
26|STATO DEL GIOCATORE
27|PROSSIMA
28|TASSO DI MISSIONI
29|MISSIONE CAOS DI OGGI
30|LOG DI SISTEMA
31|CONSIGLIO DEL COMPAGNO
32|COMPLETATE
33|ATTIVE
34|ULTIMO UMORE
35|NESSUN DATO
36|Niente in sospeso. Sospetto. Aggiungi una missione!
37|Niente in sospeso. Sospetto.
38|completate
39|missioni
40|aggiungi una missione per iniziare
41|RILANCIA
42|ACCETTA LA SFIDA (+25 XP)
43|ACCETTATA — ORA COMPLETALA
44|NUOVA MISSIONE
45|Tocca qui e scrivi la tua missione…
46|Scadenza AAAA-MM-GG (facoltativa)
47|AGGIUNGI MISSIONE
48|REGISTRO MISSIONI
49|TUTTE
50|FATTE
51|IN RITARDO
52|Nessuna scadenza = 24 ore da ora. Se la perdi, il roast arriva da solo.
53|Nessuna scadenza
54|COMPLETATA
55|SCADUTA
56|BOSS FINALE
57|PRIORITÀ ALTA
58|Completata
59|Boss finale
60|Alta
61|Normale
62|rimaste
63|scaduta da
64|Ancora nessuna missione. Il registro vuoto ci giudica entrambi.
65|Niente qui. Prova un'altra scheda.
66|COMPAGNO IA // AIUTO MISSIONI
67|FOCUS
68|STOP
69|DIVIDILA IN PASSI
70|PIANO DA 25 MIN
71|SPIEGAMELO
72|CARICA
73|CERCA SU GOOGLE
74|INVIA
75|Chiedi qualsiasi cosa sulla tua missione…
76|TU //
77|IA // COMPAGNO
78|sto pensando…
79|IA ONLINE
80|AIUTO OFFLINE
81|Ehi! Sono il tuo compagno IA. Scegli una missione di focus qui sopra (o tocca 🤖 su una missione), premi un chip o chiedimi qualsiasi cosa. Ti aiuto a finire prima.
82|CONTROLLO: COME STAI?
83|Concentrato
84|Bene
85|Così così
86|Stressato
87|Stanco
88|Giù
89|SALVA UMORE
90|Il tuo benessere conta più dei tuoi XP.
91|CHECK-IN RECENTI
92|La cronologia del tuo umore apparirà qui.
93|Ancora nessun umore registrato.
94|Nessun umore registrato finora.
95|TRAGUARDI E BADGE
96|sbloccati
97|Prima missione
98|Completa la tua prima missione
99|Gremlin delle Missioni (5)
100|Completa 5 missioni
101|Doppia Cifra (10)
102|Completa 10 missioni
103|Protagonista (25)
104|Completa 25 missioni
105|Sali di Livello
106|Raggiungi 100 XP
107|Macchina da XP
108|Raggiungi 500 XP
109|Serie di 3 giorni
110|Completa missioni per 3 giorni di fila
111|Esperto di Check-in dell'Umore
112|Registra 5 umori
113|STATISTICHE ARCADE
114|XP TOTALI
115|MIGLIORE SERIE
116|TASSO DI SUCCESSO
117|REGISTRI UMORE
118|ULTIMI 7 GIORNI
119|MIX DI UMORI
120|SERIE
121|Completa una missione per iniziare le tue statistiche.
122|giorno/i di fila
123|registro/i dell'umore
124|COMPAGNO SCATENATO
125|GENERA UNA SCUSA DISCUTIBILE
126|PRENDIMI IN GIRO
127|MISURATORE DI PROCRASTINAZIONE
128|MURO DELLA VERGOGNA
129|Nessuno nel muro della vergogna. Rispetto.
130|Zero missioni scadute. Sospettosamente responsabile.
131|Carico il discutibile consiglio di vita di oggi...
132|SUONO: ON
133|SUONO: OFF
134|CHIAVE IA (SOSTITUZIONE FACOLTATIVA)
135|SALVA CHIAVE
136|CANCELLA CHIAVE
137|PROVA CONNESSIONE IA
138|Incolla la tua chiave API…
139|INFO
140|LINGUA E REGIONE
141|LINGUA
142|PAESE
143|Scegli la lingua
144|Scegli il paese
145|Nessun paese
146|CHIUDI
147|PROFILO GIOCATORE
148|MODIFICA PROFILO
149|Avatar
150|Nome utente (3-16 lettere, numeri o _)
151|es. QuestGremlin42
152|SALVA + ENTRA IN CLASSIFICA
153|ESCI DALLA CLASSIFICA
154|CLASSIFICA GLOBALE
155|AGGIORNA
156|IL MIO PROFILO
157|MONDO
158|IL MIO PAESE
159|(ancora nessun nome utente)
160|POSIZIONE
161|senza posizione
162|Non sei ancora in classifica. Scegli un nome utente!
163|Ancora nessuno qui. Sii il primo in classifica!
164|Scegli un nome utente in PROFILO per entrare in classifica.
165|Scegli prima un paese (PROFILO o IMPOSTAZIONI).
166|Caricamento classifica…
167|giocatori mostrati
168|aggiornato
169|Sincronizzato
170|Condiviso con la classifica: nome utente, avatar, paese, XP, livello, missioni completate, miglior serie.
171|Le tue missioni, i tuoi umori e le chat IA non lasciano mai questo PC.
172|ESCI DALLA CLASSIFICA elimina la tua riga dal server.
"""

_RAW["ru"] = """
0|МЕНЮ ИГРОКА
1|ГЛАВНАЯ
2|МИССИИ
3|ИИ-ПОМОЩНИК
4|ЛАБ НАСТРОЕНИЯ
5|ЗНАЧКИ
6|СТАТИСТИКА
7|ЗОНА ПРОЖАРКИ
8|НАСТРОЙКИ
9|ПРОФИЛЬ
10|РЕЙТИНГ
11|ТВОЯ ЖИЗНЬ. ТВОЙ КВЕСТ. ТВОИ ПРАВИЛА.
12|УРОВЕНЬ
13|УР.
14|ИТОГО
15|дн. подряд
16|Новичок-прокрастинатор
17|Убийца будильника
18|Квест-гремлин
19|Рыцарь фокуса
20|Победитель дедлайнов
21|Легенда продуктивности
22|Привет, легенда
23|Доброе утро, легенда. Выбери один квест.
24|Добрый день, легенда. Ещё есть время собраться.
25|Добрый вечер, легенда. Ещё один квест?
26|СТАТУС ИГРОКА
27|ДАЛЕЕ
28|ПРОЦЕНТ ЗАВЕРШЕНИЯ
29|КВЕСТ ХАОСА НА СЕГОДНЯ
30|СИСТЕМНЫЙ ЖУРНАЛ
31|СОВЕТ НАПАРНИКА
32|ВЫПОЛНЕНО
33|АКТИВНО
34|ПОСЛЕДНЕЕ НАСТРОЕНИЕ
35|НЕТ ДАННЫХ
36|Ничего не ждёт. Подозрительно. Добавь квест!
37|Ничего не ждёт. Подозрительно.
38|выполнено
39|квестов
40|добавь квест, чтобы начать
41|ЕЩЁ РАЗ
42|ПРИНЯТЬ ВЫЗОВ (+25 XP)
43|ПРИНЯТО — ТЕПЕРЬ ВЫПОЛНЯЙ
44|НОВЫЙ КВЕСТ
45|Нажми здесь и введи свой квест…
46|Дедлайн ГГГГ-ММ-ДД (необязательно)
47|ДОБАВИТЬ КВЕСТ
48|ЖУРНАЛ КВЕСТОВ
49|ВСЕ
50|ГОТОВО
51|ПОЗДНО
52|Без дедлайна = 24 часа с этого момента. Пропустишь — прожарка придёт сама.
53|Без дедлайна
54|ВЫПОЛНЕНО
55|ПРОСРОЧЕНО
56|БОСС
57|ВЫСОКИЙ ПРИОРИТЕТ
58|Выполнено
59|Босс
60|Высокий
61|Обычный
62|осталось
63|просрочено на
64|Квестов пока нет. Пустой журнал осуждает нас обоих.
65|Тут ничего нет. Попробуй другую вкладку.
66|ИИ-НАПАРНИК // ПОМОЩНИК ПО КВЕСТАМ
67|ФОКУС
68|СТОП
69|РАЗБЕЙ НА ШАГИ
70|ПЛАН НА 25 МИН
71|ОБЪЯСНИ
72|ЗАРЯД БОДРОСТИ
73|НАЙТИ В GOOGLE
74|ОТПРАВИТЬ
75|Спроси что угодно о своём квесте…
76|ТЫ //
77|ИИ // НАПАРНИК
78|думаю…
79|ИИ ОНЛАЙН
80|ОФЛАЙН-ПОМОЩНИК
81|Йоу! Я твой ИИ-напарник. Выбери квест для фокуса выше (или нажми 🤖 на любом квесте), нажми чип или спроси меня о чём угодно. Помогу закончить быстрее.
82|ПРОВЕРКА: КАК ТЫ?
83|Сосредоточен
84|Хорошо
85|Нормально
86|В стрессе
87|Устал
88|Подавлен
89|ЗАПИСАТЬ НАСТРОЕНИЕ
90|Твоё самочувствие важнее твоих XP.
91|ПОСЛЕДНИЕ ОТМЕТКИ
92|История настроения появится здесь.
93|Записей настроения пока нет.
94|Настроений пока не записано.
95|ДОСТИЖЕНИЯ И ЗНАЧКИ
96|открыто
97|Первый квест
98|Выполни свой первый квест
99|Квест-гремлин (5)
100|Выполни 5 квестов
101|Двузначное число (10)
102|Выполни 10 квестов
103|Главный герой (25)
104|Выполни 25 квестов
105|Новый уровень
106|Набери 100 XP
107|Машина XP
108|Набери 500 XP
109|Серия 3 дня
110|Выполняй квесты 3 дня подряд
111|Профи отметок настроения
112|Запиши 5 настроений
113|АРКАДНАЯ СТАТИСТИКА
114|ВСЕГО XP
115|ЛУЧШАЯ СЕРИЯ
116|ПРОЦЕНТ ВЫПОЛНЕНИЯ
117|ЗАПИСИ НАСТРОЕНИЯ
118|ПОСЛЕДНИЕ 7 ДНЕЙ
119|МИКС НАСТРОЕНИЙ
120|СЕРИЯ
121|Выполни квест, чтобы начать копить статистику.
122|дн. подряд
123|запись(ей) настроения
124|БЕЗУМНЫЙ НАПАРНИК
125|СГЕНЕРИРОВАТЬ СОМНИТЕЛЬНУЮ ОТМАЗКУ
126|ПРОЖАРЬ МЕНЯ
127|ШКАЛА ПРОКРАСТИНАЦИИ
128|ДОСКА ПОЗОРА
129|На доске позора никого. Уважение.
130|Ноль просроченных квестов. Подозрительно ответственно.
131|Загружаю сегодняшний сомнительный жизненный совет...
132|ЗВУК: ВКЛ
133|ЗВУК: ВЫКЛ
134|КЛЮЧ ИИ (НЕОБЯЗАТЕЛЬНО)
135|СОХРАНИТЬ КЛЮЧ
136|УДАЛИТЬ КЛЮЧ
137|ПРОВЕРИТЬ СВЯЗЬ С ИИ
138|Вставь свой API-ключ…
139|О ПРОГРАММЕ
140|ЯЗЫК И РЕГИОН
141|ЯЗЫК
142|СТРАНА
143|Выбери язык
144|Выбери страну
145|Нет страны
146|ЗАКРЫТЬ
147|ПРОФИЛЬ ИГРОКА
148|РЕДАКТИРОВАТЬ ПРОФИЛЬ
149|Аватар
150|Имя (3–16 букв, цифр или _)
151|напр. QuestGremlin42
152|СОХРАНИТЬ + В РЕЙТИНГ
153|ПОКИНУТЬ РЕЙТИНГ
154|ГЛОБАЛЬНЫЙ РЕЙТИНГ
155|ОБНОВИТЬ
156|МОЙ ПРОФИЛЬ
157|МИР
158|МОЯ СТРАНА
159|(имени пока нет)
160|МЕСТО
161|вне рейтинга
162|Тебя ещё нет в рейтинге. Выбери имя!
163|Здесь пока никого. Стань первым в рейтинге!
164|Выбери имя в ПРОФИЛЬ, чтобы попасть в рейтинг.
165|Сначала выбери страну (ПРОФИЛЬ или НАСТРОЙКИ).
166|Загрузка рейтинга…
167|игроков показано
168|обновлено
169|Синхронизировано
170|Видно в рейтинге: имя, аватар, страна, XP, уровень, выполненные квесты, лучшая серия.
171|Твои квесты, настроения и ИИ-чаты никогда не покидают этот ПК.
172|ПОКИНУТЬ РЕЙТИНГ удаляет твою строку с сервера.
"""

_RAW["tr"] = """
0|OYUNCU MENÜSÜ
1|ANA SAYFA
2|GÖREVLER
3|YZ YARDIMCISI
4|RUH HALİ LABI
5|ROZETLER
6|İSTATİSTİKLER
7|ROAST BÖLGESİ
8|AYARLAR
9|PROFİL
10|SIRALAMA
11|HAYATIN. GÖREVİN. KURALLARIN.
12|SEVİYE
13|SVY
14|TOPLAM
15|günlük seri
16|Erteleme Çaylağı
17|Erteleme Avcısı
18|Görev Cini
19|Odak Şövalyesi
20|Teslim Tarihi Ejderha Avcısı
21|Verimlilik Efsanesi
22|Selam efsane
23|Günaydın, efsane. Bir görev seç.
24|Tünaydın, efsane. Odaklanmak için hâlâ vakit var.
25|İyi akşamlar, efsane. Bir görev daha?
26|OYUNCU DURUMU
27|SIRADAKİ
28|GÖREV TAMAMLAMA ORANI
29|BUGÜNÜN KAOS GÖREVİ
30|SİSTEM GÜNLÜĞÜ
31|YARDIMCI İPUCU
32|TAMAMLANAN
33|AKTİF
34|SON RUH HALİ
35|VERİ YOK
36|Bekleyen yok. Şüpheli. Bir görev ekle!
37|Bekleyen yok. Şüpheli.
38|tamamlandı
39|görev
40|başlamak için bir görev ekle
41|YENİDEN ÇEK
42|MEYDAN OKUMAYI KABUL ET (+25 XP)
43|KABUL EDİLDİ — ŞİMDİ BİTİR
44|YENİ GÖREV
45|Buraya dokun ve görevini yaz…
46|Son tarih YYYY-AA-GG (isteğe bağlı)
47|GÖREV EKLE
48|GÖREV GÜNLÜĞÜ
49|HEPSİ
50|BİTTİ
51|GEÇ
52|Son tarih yok = şu andan itibaren 24 saat. Kaçırırsan roast otomatik gelir.
53|Son tarih yok
54|TAMAMLANDI
55|GECİKMİŞ
56|PATRON SAVAŞI
57|YÜKSEK ÖNCELİK
58|Tamamlandı
59|Patron savaşı
60|Yüksek
61|Normal
62|kaldı
63|gecikme:
64|Henüz görev yok. Boş görev günlüğü ikimizi de yargılıyor.
65|Burada bir şey yok. Başka sekmeyi dene.
66|YZ YARDIMCISI // GÖREV YARDIMCISI
67|ODAK
68|DURDUR
69|PARÇALA
70|25 DK PLAN
71|AÇIKLA
72|MORAL KONUŞMASI
73|GOOGLE'DA ARA
74|GÖNDER
75|Görevin hakkında her şeyi sor…
76|SEN //
77|YZ // YARDIMCI
78|düşünüyor…
79|YZ ÇEVRİMİÇİ
80|ÇEVRİMDIŞI YARDIMCI
81|Selam! Ben senin YZ yardımcınım. Yukarıdan bir odak görevi seç (veya herhangi bir görevde 🤖'ye dokun), bir çipe bas ya da bana her şeyi sor. Daha hızlı bitirmene yardım ederim.
82|SİSTEM KONTROLÜ: NASILSIN?
83|Odaklanmış
84|İyi
85|İdare eder
86|Stresli
87|Yorgun
88|Moralsiz
89|RUH HALİNİ KAYDET
90|Sağlığın XP'nden daha önemli.
91|SON KONTROLLER
92|Ruh hali geçmişin burada görünecek.
93|Henüz ruh hali kaydı yok.
94|Henüz ruh hali kaydedilmedi.
95|BAŞARIMLAR VE ROZETLER
96|açıldı
97|İlk Görev
98|İlk görevini tamamla
99|Görev Cini (5)
100|5 görev tamamla
101|Çift Haneli (10)
102|10 görev tamamla
103|Ana Karakter (25)
104|25 görev tamamla
105|Seviye Atla
106|100 XP'ye ulaş
107|XP Makinesi
108|500 XP'ye ulaş
109|3 Günlük Seri
110|Üst üste 3 gün görev tamamla
111|Ruh Hali Kontrol Ustası
112|5 ruh hali kaydet
113|ARCADE İSTATİSTİKLERİ
114|TOPLAM XP
115|EN İYİ SERİ
116|TAMAMLAMA ORANI
117|RUH HALİ KAYITLARI
118|SON 7 GÜN
119|RUH HALİ KARIŞIMI
120|SERİ
121|İstatistiklerini oluşturmaya başlamak için bir görev tamamla.
122|gün üst üste
123|ruh hali kaydı
124|DELİ YARDIMCI
125|ŞÜPHELİ BİR MAZERET ÜRET
126|BENİ ALAYA AL
127|ERTELEME ÖLÇERİ
128|UTANÇ DUVARI
129|Utanç duvarında kimse yok. Saygı.
130|Sıfır gecikmiş görev. Şüpheli derecede sorumlu.
131|Bugünün şüpheli hayat tavsiyesi yükleniyor...
132|SES: AÇIK
133|SES: KAPALI
134|YZ ANAHTARI (İSTEĞE BAĞLI)
135|ANAHTARI KAYDET
136|ANAHTARI SİL
137|YZ BAĞLANTISINI TEST ET
138|API anahtarını yapıştır…
139|HAKKINDA
140|DİL VE BÖLGE
141|DİL
142|ÜLKE
143|Dil seç
144|Ülke seç
145|Ülke yok
146|KAPAT
147|OYUNCU PROFİLİ
148|PROFİLİ DÜZENLE
149|Avatar
150|Kullanıcı adı (3-16 harf, rakam veya _)
151|örn. QuestGremlin42
152|KAYDET + SIRALAMAYA KATIL
153|SIRALAMADAN AYRIL
154|GENEL SIRALAMA
155|YENİLE
156|PROFİLİM
157|DÜNYA
158|ÜLKEM
159|(henüz kullanıcı adı yok)
160|SIRA
161|sırasız
162|Henüz sıralamada değilsin. Bir kullanıcı adı seç!
163|Burada henüz kimse yok. Sıralamada ilk sen ol!
164|Sıralamaya katılmak için PROFİL'de bir kullanıcı adı seç.
165|Önce bir ülke seç (PROFİL veya AYARLAR).
166|Sıralama yükleniyor…
167|oyuncu gösteriliyor
168|güncellendi
169|Senkronize edildi
170|Sıralamayla paylaşılan: kullanıcı adı, avatar, ülke, XP, seviye, tamamlanan görevler, en iyi seri.
171|Görevlerin, ruh hallerin ve YZ sohbetlerin bu bilgisayardan asla çıkmaz.
172|SIRALAMADAN AYRIL, satırını sunucudan siler.
"""

_RAW["id"] = """
0|MENU PEMAIN
1|BERANDA
2|MISI
3|BANTUAN AI
4|LAB SUASANA HATI
5|LENCANA
6|STATISTIK
7|ZONA ROAST
8|PENGATURAN
9|PROFIL
10|PERINGKAT
11|HIDUPMU. MISIMU. ATURANMU.
12|LEVEL
13|LV
14|TOTAL
15|hari beruntun
16|Pemula Penunda
17|Pembasmi Snooze
18|Gremlin Misi
19|Ksatria Fokus
20|Pembunuh Naga Tenggat
21|Legenda Produktivitas
22|Halo, legenda
23|Selamat pagi, legenda. Pilih satu misi.
24|Selamat siang, legenda. Masih ada waktu untuk fokus.
25|Selamat malam, legenda. Satu misi lagi?
26|STATUS PEMAIN
27|BERIKUTNYA
28|TINGKAT PENYELESAIAN MISI
29|MISI KEKACAUAN HARI INI
30|LOG SISTEM
31|TIPS PENDAMPING
32|SELESAI
33|AKTIF
34|SUASANA HATI TERAKHIR
35|TIDAK ADA DATA
36|Tidak ada yang tertunda. Mencurigakan. Tambahkan misi!
37|Tidak ada yang tertunda. Mencurigakan.
38|selesai
39|misi
40|tambahkan misi untuk memulai
41|ACAK ULANG
42|TERIMA TANTANGAN (+25 XP)
43|DITERIMA — SEKARANG SELESAIKAN
44|MISI BARU
45|Ketuk di sini dan ketik misimu…
46|Tenggat TTTT-BB-HH (opsional)
47|TAMBAH MISI
48|CATATAN MISI
49|SEMUA
50|TUNTAS
51|TERLAMBAT
52|Tanpa tenggat = 24 jam dari sekarang. Kalau terlewat, roast datang otomatis.
53|Tanpa tenggat
54|SELESAI
55|LEWAT TENGGAT
56|PERTARUNGAN BOS
57|PRIORITAS TINGGI
58|Selesai
59|Pertarungan bos
60|Tinggi
61|Normal
62|tersisa
63|terlambat
64|Belum ada misi. Catatan misi yang kosong menghakimi kita berdua.
65|Tidak ada apa-apa di sini. Coba tab lain.
66|PENDAMPING AI // BANTUAN MISI
67|FOKUS
68|BERHENTI
69|PECAH JADI LANGKAH
70|RENCANA 25 MENIT
71|JELASKAN
72|SEMANGAT
73|CARI DI GOOGLE
74|KIRIM
75|Tanya apa saja tentang misimu…
76|KAMU //
77|AI // PENDAMPING
78|berpikir…
79|AI ONLINE
80|BANTUAN OFFLINE
81|Yo! Aku pendamping AI-mu. Pilih misi fokus di atas (atau ketuk 🤖 pada misi mana pun), tekan chip, atau tanya apa saja. Aku bantu kamu selesai lebih cepat.
82|CEK SISTEM: BAGAIMANA KABARMU?
83|Fokus
84|Baik
85|Biasa saja
86|Stres
87|Lelah
88|Murung
89|CATAT SUASANA HATI
90|Kesejahteraanmu lebih penting daripada XP-mu.
91|CEK-IN TERBARU
92|Riwayat suasana hatimu akan muncul di sini.
93|Belum ada catatan suasana hati.
94|Belum ada suasana hati yang dicatat.
95|PENCAPAIAN & LENCANA
96|terbuka
97|Misi Pertama
98|Selesaikan misi pertamamu
99|Gremlin Misi (5)
100|Selesaikan 5 misi
101|Dua Digit (10)
102|Selesaikan 10 misi
103|Tokoh Utama (25)
104|Selesaikan 25 misi
105|Naik Level
106|Capai 100 XP
107|Mesin XP
108|Capai 500 XP
109|Beruntun 3 Hari
110|Selesaikan misi 3 hari berturut-turut
111|Pakar Cek-in Suasana Hati
112|Catat 5 suasana hati
113|STATISTIK ARCADE
114|TOTAL XP
115|RANGKAIAN TERBAIK
116|TINGKAT PENYELESAIAN
117|CATATAN SUASANA HATI
118|7 HARI TERAKHIR
119|CAMPURAN SUASANA HATI
120|RANGKAIAN
121|Selesaikan satu misi untuk mulai membangun statistikmu.
122|hari berturut-turut
123|catatan suasana hati
124|PENDAMPING GILA
125|BUAT ALASAN YANG MENCURIGAKAN
126|ROAST AKU
127|METER PROKRASTINASI
128|DINDING KEMALUAN
129|Tidak ada siapa pun di dinding kemaluan. Hormat.
130|Nol misi terlambat. Mencurigakan bertanggung jawab.
131|Memuat saran hidup meragukan hari ini...
132|SUARA: NYALA
133|SUARA: MATI
134|KUNCI AI (PENGGANTI OPSIONAL)
135|SIMPAN KUNCI
136|HAPUS KUNCI
137|UJI KONEKSI AI
138|Tempel kunci API-mu…
139|TENTANG
140|BAHASA & WILAYAH
141|BAHASA
142|NEGARA
143|Pilih bahasa
144|Pilih negara
145|Tanpa negara
146|TUTUP
147|PROFIL PEMAIN
148|EDIT PROFIL
149|Avatar
150|Nama pengguna (3-16 huruf, angka, atau _)
151|mis. QuestGremlin42
152|SIMPAN + GABUNG PERINGKAT
153|KELUAR PERINGKAT
154|PERINGKAT GLOBAL
155|SEGARKAN
156|PROFILKU
157|DUNIA
158|NEGARAKU
159|(belum ada nama pengguna)
160|URUTAN
161|tanpa peringkat
162|Kamu belum ada di peringkat. Pilih nama pengguna!
163|Belum ada siapa-siapa. Jadilah yang pertama di peringkat!
164|Pilih nama pengguna di PROFIL untuk bergabung ke peringkat.
165|Pilih negara dulu (PROFIL atau PENGATURAN).
166|Memuat peringkat…
167|pemain ditampilkan
168|diperbarui
169|Tersinkron
170|Dibagikan ke peringkat: nama pengguna, avatar, negara, XP, level, misi selesai, rangkaian terbaik.
171|Misi, suasana hati, dan obrolan AI-mu tidak pernah meninggalkan PC ini.
172|KELUAR PERINGKAT menghapus barismu dari server.
"""

_RAW["nl"] = """
0|SPELERSMENU
1|HOME
2|MISSIES
3|AI-HULP
4|STEMMINGSLAB
5|BADGES
6|INZICHTEN
7|ROAST-ZONE
8|INSTELLINGEN
9|PROFIEL
10|RANGLIJST
11|JOUW LEVEN. JOUW QUEST. JOUW REGELS.
12|LEVEL
13|LVL
14|TOTAAL
15|dagen reeks
16|Uitstel-Beginner
17|Snooze-Slayer
18|Quest-Gremlin
19|Focus-Ridder
20|Deadline-Drakendoder
21|Productiviteitslegende
22|Hé legende
23|Goedemorgen, legende. Kies één quest.
24|Goedemiddag, legende. Er is nog tijd om je te focussen.
25|Goedenavond, legende. Nog één quest?
26|SPELERSSTATUS
27|VOLGENDE
28|QUEST-SUCCESPERCENTAGE
29|CHAOS-QUEST VAN VANDAAG
30|SYSTEEMLOG
31|SIDEKICK-TIP
32|VOLTOOID
33|ACTIEF
34|LAATSTE STEMMING
35|GEEN GEGEVENS
36|Niets open. Verdacht. Voeg een quest toe!
37|Niets open. Verdacht.
38|voltooid
39|quests
40|voeg een quest toe om te beginnen
41|OPNIEUW
42|UITDAGING AANNEMEN (+25 XP)
43|GEACCEPTEERD — GA HET NU DOEN
44|NIEUWE QUEST
45|Tik hier en typ je quest…
46|Deadline JJJJ-MM-DD (optioneel)
47|QUEST TOEVOEGEN
48|QUESTLOGBOEK
49|ALLES
50|KLAAR
51|TE LAAT
52|Geen deadline = 24 uur vanaf nu. Mis je hem, dan komt de roast vanzelf.
53|Geen deadline
54|VOLTOOID
55|VERLOPEN
56|BAASGEVECHT
57|HOGE PRIORITEIT
58|Voltooid
59|Baasgevecht
60|Hoog
61|Normaal
62|over
63|te laat met
64|Nog geen quests. Het lege logboek veroordeelt ons allebei.
65|Hier is niets. Probeer een ander tabblad.
66|AI-SIDEKICK // QUESTHULP
67|FOCUS
68|STOP
69|SPLITS OP
70|25-MIN-PLAN
71|LEG UIT
72|PEPTALK
73|GOOGLE HET
74|VERSTUUR
75|Vraag alles over je quest…
76|JIJ //
77|AI // SIDEKICK
78|denkt na…
79|AI ONLINE
80|OFFLINE-HULP
81|Yo! Ik ben je AI-sidekick. Kies hierboven een focusquest (of tik op 🤖 bij een quest), druk op een chip of vraag me alles. Ik help je sneller klaar te zijn.
82|SYSTEEMCHECK: HOE GAAT HET?
83|Gefocust
84|Goed
85|Oké
86|Gestrest
87|Moe
88|Somber
89|STEMMING OPSLAAN
90|Je welzijn is belangrijker dan je XP.
91|RECENTE CHECK-INS
92|Je stemmingsgeschiedenis verschijnt hier.
93|Nog geen stemmingslogs.
94|Nog geen stemmingen vastgelegd.
95|PRESTATIES & BADGES
96|ontgrendeld
97|Eerste quest
98|Voltooi je eerste quest
99|Quest-Gremlin (5)
100|Voltooi 5 quests
101|Dubbele Cijfers (10)
102|Voltooi 10 quests
103|Hoofdpersonage (25)
104|Voltooi 25 quests
105|Level omhoog
106|Bereik 100 XP
107|XP-machine
108|Bereik 500 XP
109|Reeks van 3 dagen
110|Voltooi quests 3 dagen achter elkaar
111|Stemmings-Check-in-Pro
112|Leg 5 stemmingen vast
113|ARCADE-INZICHTEN
114|TOTAAL XP
115|BESTE REEKS
116|SUCCESPERCENTAGE
117|STEMMINGSLOGS
118|LAATSTE 7 DAGEN
119|STEMMINGSMIX
120|REEKS
121|Voltooi een quest om je statistieken op te bouwen.
122|dag(en) op rij
123|stemmingslog(s)
124|DOORGEDRAAIDE SIDEKICK
125|GENEREER EEN TWIJFELACHTIGE EXCUUS
126|ROAST MIJ
127|UITSTELMETER
128|MUUR VAN SCHAAMTE
129|Niemand op de muur van schaamte. Respect.
130|Nul verlopen quests. Verdacht verantwoordelijk.
131|Het twijfelachtige levensadvies van vandaag laden...
132|GELUID: AAN
133|GELUID: UIT
134|AI-SLEUTEL (OPTIONELE OVERSCHRIJVING)
135|SLEUTEL OPSLAAN
136|SLEUTEL WISSEN
137|AI-VERBINDING TESTEN
138|Plak je API-sleutel…
139|OVER
140|TAAL & REGIO
141|TAAL
142|LAND
143|Kies taal
144|Kies land
145|Geen land
146|SLUITEN
147|SPELERSPROFIEL
148|PROFIEL BEWERKEN
149|Avatar
150|Gebruikersnaam (3-16 letters, cijfers of _)
151|bijv. QuestGremlin42
152|OPSLAAN + MEEDOEN
153|RANGLIJST VERLATEN
154|WERELDRANGLIJST
155|VERVERSEN
156|MIJN PROFIEL
157|WERELD
158|MIJN LAND
159|(nog geen gebruikersnaam)
160|PLAATS
161|zonder plaats
162|Je staat nog niet in de ranglijst. Kies een gebruikersnaam!
163|Nog niemand hier. Wees de eerste op de ranglijst!
164|Kies een gebruikersnaam in PROFIEL om mee te doen.
165|Kies eerst een land (PROFIEL of INSTELLINGEN).
166|Ranglijst laden…
167|spelers getoond
168|bijgewerkt
169|Gesynchroniseerd
170|Gedeeld met de ranglijst: gebruikersnaam, avatar, land, XP, level, voltooide quests, beste reeks.
171|Je quests, stemmingen en AI-chats verlaten deze pc nooit.
172|RANGLIJST VERLATEN verwijdert jouw rij van de server.
"""

_RAW["pl"] = """
0|MENU GRACZA
1|START
2|MISJE
3|POMOC AI
4|LAB NASTROJU
5|ODZNAKI
6|STATYSTYKI
7|STREFA ROAST
8|USTAWIENIA
9|PROFIL
10|RANKING
11|TWOJE ŻYCIE. TWOJA MISJA. TWOJE ZASADY.
12|POZIOM
13|POZ
14|RAZEM
15|dni serii
16|Początkujący Prokrastynator
17|Pogromca Drzemki
18|Gremlin Misji
19|Rycerz Skupienia
20|Pogromca Smoków Terminów
21|Legenda Produktywności
22|Hej, legendo
23|Dzień dobry, legendo. Wybierz jedną misję.
24|Dzień dobry, legendo. Jeszcze jest czas, by się skupić.
25|Dobry wieczór, legendo. Jeszcze jedna misja?
26|STATUS GRACZA
27|NASTĘPNE
28|WSKAŹNIK UKOŃCZENIA MISJI
29|DZISIEJSZA MISJA CHAOSU
30|DZIENNIK SYSTEMU
31|PORADA POMOCNIKA
32|UKOŃCZONE
33|AKTYWNE
34|OSTATNI NASTRÓJ
35|BRAK DANYCH
36|Nic nie czeka. Podejrzane. Dodaj misję!
37|Nic nie czeka. Podejrzane.
38|ukończono
39|misji
40|dodaj misję, aby zacząć
41|LOSUJ PONOWNIE
42|PRZYJMIJ WYZWANIE (+25 XP)
43|PRZYJĘTE — DO ROBOTY
44|NOWA MISJA
45|Dotknij tutaj i wpisz swoją misję…
46|Termin RRRR-MM-DD (opcjonalnie)
47|DODAJ MISJĘ
48|DZIENNIK MISJI
49|WSZYSTKIE
50|GOTOWE
51|SPÓŹNIONE
52|Brak terminu = 24 godziny od teraz. Jak przegapisz, roast przyjdzie sam.
53|Brak terminu
54|UKOŃCZONA
55|PRZETERMINOWANA
56|WALKA Z BOSSEM
57|WYSOKI PRIORYTET
58|Ukończona
59|Walka z bossem
60|Wysoki
61|Normalny
62|zostało
63|po terminie o
64|Brak misji. Pusty dziennik osądza nas oboje.
65|Nic tu nie ma. Spróbuj innej karty.
66|POMOCNIK AI // POMOC W MISJACH
67|SKUPIENIE
68|STOP
69|ROZBIJ NA KROKI
70|PLAN NA 25 MIN
71|WYJAŚNIJ
72|MOTYWACJA
73|SZUKAJ W GOOGLE
74|WYŚLIJ
75|Zapytaj o cokolwiek w sprawie misji…
76|TY //
77|AI // POMOCNIK
78|myślę…
79|AI ONLINE
80|POMOC OFFLINE
81|Hej! Jestem Twoim pomocnikiem AI. Wybierz misję skupienia powyżej (lub dotknij 🤖 przy dowolnej misji), kliknij chip albo zapytaj mnie o cokolwiek. Pomogę Ci skończyć szybciej.
82|TEST SYSTEMU: JAK SIĘ CZUJESZ?
83|Skupiony
84|Dobrze
85|W porządku
86|Zestresowany
87|Zmęczony
88|Przygnębiony
89|ZAPISZ NASTRÓJ
90|Twoje samopoczucie jest ważniejsze niż XP.
91|OSTATNIE ZAMELDOWANIA
92|Historia Twojego nastroju pojawi się tutaj.
93|Brak wpisów nastroju.
94|Nie zapisano jeszcze nastrojów.
95|OSIĄGNIĘCIA I ODZNAKI
96|odblokowano
97|Pierwsza misja
98|Ukończ swoją pierwszą misję
99|Gremlin Misji (5)
100|Ukończ 5 misji
101|Dwucyfrowy (10)
102|Ukończ 10 misji
103|Główny Bohater (25)
104|Ukończ 25 misji
105|Awans na poziom
106|Osiągnij 100 XP
107|Maszyna XP
108|Osiągnij 500 XP
109|Seria 3 dni
110|Ukończ misje 3 dni z rzędu
111|Mistrz Zameldowań Nastroju
112|Zapisz 5 nastrojów
113|STATYSTYKI ARCADE
114|ŁĄCZNIE XP
115|NAJLEPSZA SERIA
116|WSKAŹNIK UKOŃCZENIA
117|WPISY NASTROJU
118|OSTATNIE 7 DNI
119|MIKS NASTROJÓW
120|SERIA
121|Ukończ misję, aby zacząć budować statystyki.
122|dni z rzędu
123|wpis(ów) nastroju
124|SZALONY POMOCNIK
125|WYGENERUJ WĄTPLIWĄ WYMÓWKĘ
126|WYŚMIEJ MNIE
127|MIERNIK PROKRASTYNACJI
128|ŚCIANA WSTYDU
129|Nikogo na ścianie wstydu. Szacunek.
130|Zero przeterminowanych misji. Podejrzanie odpowiedzialnie.
131|Ładuję dzisiejszą wątpliwą radę życiową...
132|DŹWIĘK: WŁ.
133|DŹWIĘK: WYŁ.
134|KLUCZ AI (OPCJONALNE NADPISANIE)
135|ZAPISZ KLUCZ
136|USUŃ KLUCZ
137|PRZETESTUJ POŁĄCZENIE AI
138|Wklej swój klucz API…
139|INFO
140|JĘZYK I REGION
141|JĘZYK
142|KRAJ
143|Wybierz język
144|Wybierz kraj
145|Brak kraju
146|ZAMKNIJ
147|PROFIL GRACZA
148|EDYTUJ PROFIL
149|Awatar
150|Nazwa użytkownika (3-16 liter, cyfr lub _)
151|np. QuestGremlin42
152|ZAPISZ + DOŁĄCZ DO RANKINGU
153|OPUŚĆ RANKING
154|RANKING GLOBALNY
155|ODŚWIEŻ
156|MÓJ PROFIL
157|ŚWIAT
158|MÓJ KRAJ
159|(brak nazwy użytkownika)
160|MIEJSCE
161|bez miejsca
162|Nie ma Cię jeszcze w rankingu. Wybierz nazwę użytkownika!
163|Nikogo tu jeszcze nie ma. Bądź pierwszy w rankingu!
164|Wybierz nazwę użytkownika w PROFIL, aby dołączyć do rankingu.
165|Najpierw wybierz kraj (PROFIL lub USTAWIENIA).
166|Wczytywanie rankingu…
167|pokazanych graczy
168|zaktualizowano
169|Zsynchronizowano
170|Udostępniane w rankingu: nazwa użytkownika, awatar, kraj, XP, poziom, ukończone misje, najlepsza seria.
171|Twoje misje, nastroje i czaty AI nigdy nie opuszczają tego komputera.
172|OPUŚĆ RANKING usuwa Twój wiersz z serwera.
"""


def build(keys):
    """Return {code: {english_phrase: translation}} for every complete language."""
    out = {}
    for code, raw in _RAW.items():
        rows = {}
        for line in raw.strip().splitlines():
            n, _sep, txt = line.partition("|")
            try:
                rows[int(n)] = txt.strip()
            except ValueError:
                continue
        if sorted(rows) == list(range(len(keys))):
            out[code] = {k: rows[i] for i, k in enumerate(keys)}
    return out