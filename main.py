import discord
import asyncio
import os
import re
import random
import datetime
from utils import write_to_file, get_from_file_id_lines, split_separator_nick, load_config
from lottery import Lottery
from eye_game import EyeGame

ALLOWED_ROLES = ["Awanturnik", "Bohater", "Wędrowiec", "Test-1"]
HUBERT_GREETINGS = [
    "Ahoy!", "Ahoj, {}!", "Yo-ho-ho!", "Avast, ye landlubber!",
    "Niech mnie kule biją!", "Niech to dunder świśnie!",
    "Arr, witam na pokładzie!"
]
LEGIT_GUILDS = ['AWANTURNICY: Widmo nad Versmold', 'Test-Server']
LEGIT_CHANNELS = ['👋 | witaj-pośród-awanturników', 'kanał-drugi-⚓']
WRONG_ANSWER = [
    "To jakieś morze bzdur!", "Chyba Cię meduza ugryzła w mózg!",
    "Popełniłeś błąd, jak marynarz na lądzie!",
    "To nie ta opowieść, przyjacielu!",
    "Jakbyś nawigował, to już dawno byśmy osiedli na rafie!",
    "Żeglarzu, chyba masz kaca po rumie!", "Gadanie jak z dziobu papugi!",
    "Który rekin Ci to naopowiadał?", "Widzę, że kompas Ci się popsuł!",
    "To gorsze niż morska choroba!", "Zatopione! Nietrafione!",
    "Na dno! Spróbuj jeszcze raz!",
    "Przez takie myślenie wylądujemy na mieliźnie, rusz głową!",
    "To tak, jakbyś szukał skarbu bez mapy!",
    "Czy ty w ogóle słyszysz, co mówisz?",
    "To nie ten okręt, kolego! Ho, ho, ho!",
    "Jesteś tak daleko, jak Wielki Ocean od Imperium!",
    "Twoja odpowiedź jest jak wiatr w żagle... tyle że na przeciwny kursu!",
    "Ani kropla prawdy w tym, co mówisz!",
    "Czy ty nawigujesz odpowiedzi na ślepo?",
    "Jesteś bardziej zagubiony niż skarb na bezludnej wyspie!",
    "Twoje słowa to czysta piracka fantazja!",
    "Chyba ci się kompas zepsuł, marynarzu!",
    "Jakbyś strzelał z armaty... i chybił!",
    "To odpowiedź jak z mokrej procy!",
    "Przyjacielu, lepiej już milcz jak syreny w burzy!",
    "Zgubiłeś się jak statek w mgle!", "To tak trafne, jak mapa bez 'X'!",
    "Rozmawiasz jak pijany sternik!",
    "Twoje słowa toną szybciej niż statek w sztormie!"
]

config = load_config()

active_questions = [False for _ in range(10)]
active_piq_quest = False
lottery_process = Lottery()
eye_process = EyeGame()

token = os.environ['DIS_TOKEN']

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


def validate_is_status_of_action_ok(action):
    author_id = action.get("message_author").id
    situation_index = action.get("situation_index")

    lines = get_from_file_id_lines('pig_quest.txt', author_id)

    if situation_index == "1":
        if len(lines) > 0:
            return False
        else:
            return True

    if situation_index == "2":
        if len(lines) == 1:
            pattern = r"roll result: ([\d.]+)"
            match = re.search(pattern, lines[0])

            if match:
                roll_result = int(match.group(1))

                if roll_result < 10:
                    return True

            return False


async def ask_question(sleep_time,
                       target_channel,
                       question_content,
                       question_index,
                       author,
                       img=None):
    await asyncio.sleep(sleep_time)
    if img:
        await target_channel.send(f'**{author}**: \n{question_content}.',
                                  file=discord.File(f'./{img}'))
    else:
        await target_channel.send(f'**{author}**: \n{question_content}.')
    active_questions[question_index] = True


async def send_questions(target_channel):
    if config.get("questions", {}).get("process"):
        await target_channel.send(
            "**Kapitan Hubert**: \nHo ho! W związku z naszym wyjątkowym dniem ogłaszam konkurs wiedzy! Dla wszystkich członków oddziału Dauerhafta! Do wygrania wiele marnych miedziaków 💰! Ogłszam, że w losowych momentach w ciągu dnia zostaną podane pytania dotyczące wiedzy na temat walki Frantza 💪 i jego towarzyszy . Osoba, która jako pierwsza dobrze odpowie na zadane pytanie, otrzyma ode mnie 10 marnych miedziaków, za każdą dobrą odpowiedź.:mee6Coins:. Niby niewiele, ale miedziak do miedziaczka aż zbierzesz ziemniaczka 🥔 ho, ho ho! Miedziaczki zostaną rozdysponowane pod koniec dnia przez Majtka Solveiga."
        )

    if config.get("questions", {}).get("question1", {}).get("process"):
        await ask_question(
            sleep_time=config.get("questions", {}).get("question1", {}).get("delay_time", 5),
            target_channel=target_channel,
            question_content=
            'Zacznijmy od czegoś prostego! Jak nazywała się Beczułka zlokalizowana w Holthusen:question: Kto pierwszy ten lepszy! Ho, ho, ho🍺\n\n-----\n||*By udzielić odpowiedzi napisz: "!Frantz-Hubert-1 XXX" (gdzie XXX to odpowiedź) np. !Frantz-Hubert-1 Pół Miarki Więcej. Wielkość liter nie ma znaczenia*||',
            question_index=0,
            author="Kapitan Hubert")

    if config.get("questions", {}).get("question2", {}).get("process"):
        await ask_question(
            sleep_time=config.get("questions", {}).get("question2", {}).get("delay_time", 10),
            target_channel=target_channel,
            question_content=
            'Kto pierwszy ten lepszy! Czyja to piękna, szpetna morda:question: *Kapitan Hubert rozwija pergamin* \n\n-----\n||*By udzielić odpowiedzi napisz: "!Frantz-Hubert-2 XXX" (gdzie XXX to odpowiedź) np. !Frantz-Hubert-2 Pół Miarki Więcej. Wielkość liter nie ma znaczenia*||',
            question_index=1,
            author="Kapitan Hubert",
            img="Frederich.png")

    if config.get("questions", {}).get("question3", {}).get("process"):
        await ask_question(
            sleep_time=config.get("questions", {}).get("question3", {}).get("delay_time", 15),
            target_channel=target_channel,
            question_content=
            'Kto wyrwał ze stawu ramię Tommy\'emu w Noc Tajemnic:question:\n\n-----\n||*By udzielić odpowiedzi napisz: "!Frantz-Hubert-3 XXX" (gdzie XXX to odpowiedź) np. !Frantz-Hubert-3 Pół Miarki Więcej. Wielkość liter nie ma znaczenia*||',
            question_index=2,
            author="Kapitan Hubert")

    if config.get("questions", {}).get("question4", {}).get("process"):
        await ask_question(
            sleep_time=config.get("questions", {}).get("question4", {}).get("delay_time", 20),
            target_channel=target_channel,
            question_content=
            'Jak miała na imię córka Roberta, byłego pracodawcy Frantza:question: Proszę o podanie imienia i nazwiska.\n\n-----\n||*By udzielić odpowiedzi napisz: "!Frantz-Hubert-4 XXX" (gdzie XXX to odpowiedź) np. !Frantz-Hubert-4 Frederich Grun. Wielkość liter nie ma znaczenia*||',
            question_index=3,
            author="Kapitan Hubert")

    if config.get("questions", {}).get("question5", {}).get("process"):
        await ask_question(
            sleep_time=config.get("questions", {}).get("question5", {}).get("delay_time", 25),
            target_channel=target_channel,
            question_content=
            'Podaj mi kamracie imiona kolejno prawdziwego ojca, przybranego ojca, brata, przybranej siostry naszego bosmana Kastnera. 💪\n\n-----\n||*By udzielić odpowiedzi napisz: "!Frantz-Hubert-5 XXX" (gdzie XXX to odpowiedź, imiona odziel przecinkami) np. !Frantz-Hubert-5 Frederich, Tommy, Frantz, Haakon. Wielkość liter nie ma znaczenia, ale kolejność ma znaczenie! UWAGA: zwróć uwagę na spacje po przecinku inaczej odpowiedź nie zostanie rozpoznana*||',
            question_index=4,
            author="Kapitan Hubert")

    if config.get("questions", {}).get("question6", {}).get("process"):
        await ask_question(
            sleep_time=config.get("questions", {}).get("question6", {}).get("delay_time", 25),
            target_channel=target_channel,
            question_content=
            'A jak miał na imię woźnica i kolega Ralfa towarzyszący w podróży między innymi z Zahnstadu do Eilchart:question: 💪\n\n-----\n||*By udzielić odpowiedzi napisz: "!Frantz-Hubert-6 XXX" (gdzie XXX to odpowiedź) np. !Frantz-Hubert-6 Frederich. Wielkość liter nie ma znaczenia*||',
            question_index=5,
            author="Kapitan Hubert")

    if config.get("pig", {}).get("process"):
        await pig_action_initialization(target_channel, config.get("pig", {}).get("duration", 300))

    # 2:07 XXXVIII
    if config.get("questions", {}).get("question7", {}).get("process"):
        await ask_question(
            sleep_time=config.get("questions", {}).get("question7", {}).get("delay_time", 30),
            target_channel=target_channel,
            question_content=
            'Jak nazywała się strażnik, która  Haakona w Eilchart do ludzi, którzy potem uwięzili Haakona:question: Ha tfu, szubrawcy!\n\n-----\n||*By udzielić odpowiedzi napisz: "!Frantz-Hubert-7 XXX" (gdzie XXX to odpowiedź) np. !Frantz-Hubert-7 Frederich. Wielkość liter nie ma znaczenia*||',
            question_index=6,
            author="Kapitan Hubert")

    if config.get("questions", {}).get("question8", {}).get("process"):
        await ask_question(
            sleep_time=config.get("questions", {}).get("question8", {}).get("delay_time", 35),
            target_channel=target_channel,
            question_content=
            'Kto był niby bohaterem w Eilhart, a kto prwadziwym bohaterem:question: *kapitan Hubert puszcza oczko do Aubrey* ;)\n\n-----\n||*By udzielić odpowiedzi napisz: "!Frantz-Hubert-8 XXX" (gdzie XXX to odpowiedź, imiona odziel przecinkami) np. !Frantz-Hubert-8 Frederich, Frantz. Wielkość liter nie ma znaczenia. UWAGA: zwróć uwagę na spacje po przecinku inaczej odpowiedź nie zostanie rozpoznana*||',
            question_index=7,
            author="Kapitan Hubert")

    if config.get("questions", {}).get("question9", {}).get("process"):
        await ask_question(
            sleep_time=config.get("questions", {}).get("question9", {}).get("delay_time", 40),
            target_channel=target_channel,
            question_content=
            'No, ostatnie pytanie należy do mnie, jak zawsze ostatnie słowo jest moje. Jakie było imię głównego zwierzchnika sił pospolitego ruszenia Imperium podczas bitwy o Holthusen:question:\n\n-----\n||*By udzielić odpowiedzi napisz: "!Frantz-Aubrey-9 XXX" (gdzie XXX to odpowiedź) np. !Frantz-Aubrey-9 Frederich. Wielkość liter nie ma znaczenia*||',
            question_index=8,
            author="Aubrey")


async def pig_action_initialization(target_channel, time_event=300):
    global active_piq_quest
    active_piq_quest = True

    await target_channel.send(
        '**:crossed_swords: Głos z Eteru :crossed_swords:**\nŚwiętowanie trwa w najlepsze, piwo leje się garściami, ludzie się śmieją rozmawiają, nagke chaos, gdy niespodziewany gość - potężny warchlak - wtargnął na pokład! Z impetem przewrócił osobę stojącą przy rampie, wydając głośne "KWI! KWI! KWI!", co wywołało salwy śmiechu wśród załogantów. Świniak, niczym burza, przemknął przez łajbę, wprowadzając zamieszanie. W ślad za nim, na pokład wparował rozedrgany wieśniak z długim kijem, wykrzykując w stronę załogi:\n\n**Wieśniak:**\nLudzie, ludzie! Świniak mi uciekł, psia mać! Pomóżcie złapać, pomóżcie!\n\n**Głos z Eteru:**\nW rozpaczliwym pędzie za świnią, mężczyzna wpada prosto w grupę rozśmieszonych marynarzy. Zwierzę, zwinne jak wiatr, przemyka między nimi, przewracając po drodze skrzynie z kuflami piwa. Wieśniak, potykając się, wpada na marynarzy i lądując z dwójką z nich na ziemi.\n\n**Wieśniak:**\nPrzepraszam, panocki, przepraszam! Nie chciałem, przeklęty warchlak! Jak go dorwę, psia mać!\n\n**Głos z Eteru: **\nMężczyzna szybko podniósł się, otrzepując ubranie, pomagając innym wrócić na nogi i przeprszając ich. Rozgląda się za świnią, która, skierowana przez marynarzy, biegiem wpada na rampę i znika z pokładu. Wieśniak rusza za nią pędem. Mija krótka chwila, gdy przewróceni wcześniej marynarze wykrzykują ze zdumieniem: "Kurwa, moja sakiewka! Łapać złodzieja!", wskazując palcem na niknącego w tłumie na lądzie mężczyznę.\n\n||Wydarzenie opatrzone jest - :crossed_swords: co oznacza, że jest on przeznaczony dla osób posiadających grywalne postaci w Świecie Awanturników. Jeżeli chcesz dołączyć do gonitwy za złodziejem wpisz !pościg-1 podając wartość zwinności Twojego bohatera np. !pościg-1 3 (gdy Twoja postać ma wartość zręczności 3).||'
    )

    await asyncio.sleep(time_event)
    active_piq_quest = False


# huber - szefem odzialu dauerhafta
async def answers_question_check(question_context):
    author = question_context.get('author')
    shorten_version = "hubert" if author == "Kapitan Hubert" else author.lower()
    question_index = question_context.get('index_question', 0)
    user_command_answer = question_context.get('msg_content', '')
    question_title = f'!frantz-{shorten_version}-{question_index + 1}'
    message_object = question_context.get('message')
    correct_answer = question_context.get('correct_answer')
    incorrect_answer = question_context.get('incorrect_answer')
    hubert_positive_reply = question_context.get('positive_reply', '👍')

    if active_questions[question_index] and user_command_answer.startswith(
            question_title) and len(user_command_answer) > 17:
        answer = user_command_answer.split(f'{question_title} ', 1)[1]

        if answer == correct_answer:
            await message_object.reply(f'**{author}**:\n{hubert_positive_reply}')

            active_questions[question_index] = False

            write_to_file(
                'hubert_answers.txt',
                f'{str(datetime.datetime.now())}, question index: {question_index}, author_name: {message_object.author.name}, author_id: {message_object.author.id}, answer: {answer}'
            )
        else:
            await message_object.reply(f'**{author}**:\n{incorrect_answer}')


async def send_weloce_section(channel):
    await channel.send(
        "Statek Frantz przecina tafle Reiku, sunąc niebieską wstęgą ⚓. Frantz dociera do jakiejś pomniejszej wioski, zarzuca cumy i rozpoczyna się ś w i ę t o w a n i e 🎉🎊🎉🎊🎉!!!*\n\n**Kapitan Hubert**:\nDziś wyjątkowy dzień Kamraci 🎉, ho ho! Mamy dziesiątą rocznicę rozpoczęcia naszych poszukiwań wroga Imperium Ludzkości i wszystkich ras Kaz-Kazli 🔍! Co jednak ważniejsze mamy w związku z tym także rocznię poświęcenia i końca krucjaty naszego bohatera, inspiratora, autorytetu - Frantza 👏. Świętujmy oddziale Dauerhafta! Zdrowie Frantza 🍻!\n\n||Dodatkowe zasady: wszystkie eventy opatrzone :crossed_swords: XXX :crossed_swords: to wydarzenia tylko dla osób biorących czynny udział w sesjach Solwisia, czyli mających swoje karty postaci.||",
        file=discord.File("./board.png")
    )


async def validate_question_section(message_data):
    msg_content = message_data.get('message_content')
    message = message_data.get('message_obj')

    await answers_question_check({
        "index_question": 0,
        "msg_content": msg_content,
        "correct_answer": "uśmiechnięta",
        "incorrect_answer": random.choice(WRONG_ANSWER),
        "positive_reply":
            "To nie bylo zbyt trudne. Dobra, pamiętaj potem zgłosić się po miedziaczki :mee6Coins:",
        "message": message,
        "author": "Kapitan Hubert"
    })

    await answers_question_check({
        "index_question": 1,
        "msg_content": msg_content,
        "correct_answer": "frederich",
        "incorrect_answer": random.choice(WRONG_ANSWER),
        "positive_reply":
            "To było ostatnie łatwe pytanie! Dobra, zgłoś się potem po swoje miedziaczki :mee6Coins:",
        "message": message,
        "author": "Kapitan Hubert"
    })

    await answers_question_check({
        "index_question": 2,
        "msg_content": msg_content,
        "correct_answer": "oddon",
        "incorrect_answer": random.choice(WRONG_ANSWER),
        "positive_reply":
            "Zdrowie Oddona! 🍻 Proszę, zgłosić sie potem o odbiór miedziaczków :mee6Coins:",
        "message": message,
        "author": "Kapitan Hubert"
    })

    await answers_question_check({
        "index_question": 3,
        "msg_content": msg_content,
        "correct_answer": "carla wittgenstein",
        "incorrect_answer": random.choice(WRONG_ANSWER),
        "positive_reply":
            "Nieźle, nieźle! Podobno niejaka Elsinka jest do niej niezwykle podobna 👀! Proszę, zgłosić się potem o odbiór miedziaczków :mee6Coins:",
        "message": message,
        "author": "Kapitan Hubert"
    })

    await answers_question_check({
        "index_question": 4,
        "msg_content": msg_content,
        "correct_answer": "richmut, thorstein, peter, angelika",
        "incorrect_answer": random.choice(WRONG_ANSWER),
        "positive_reply":
            "Uuuu czyżby cichy fan rodziny Kastnerów 🤫? Proszę, zgłosić sie potem o odbiór miedziaczków :mee6Coins:",
        "message": message,
        "author": "Kapitan Hubert"
    })

    await answers_question_check({
        "index_question": 5,
        "msg_content": msg_content,
        "correct_answer": "hartwin",
        "incorrect_answer": random.choice(WRONG_ANSWER),
        "positive_reply":
            "Nigdy go nie poznałem, a szkoda! Zgłoś się potem po odbiór miedziaczków :mee6Coins:",
        "message": message,
        "author": "Kapitan Hubert"
    })

    await answers_question_check({
        "index_question": 6,
        "msg_content": msg_content,
        "correct_answer": "ute",
        "incorrect_answer": random.choice(WRONG_ANSWER),
        "positive_reply":
            "Szubrawiec, ot co! Zgłoś się potem po odbiór miedziaczków :mee6Coins:",
        "message": message,
        "author": "Kapitan Hubert"
    })

    await answers_question_check({
        "index_question": 7,
        "msg_content": msg_content,
        "correct_answer": "ingo, aubrey",
        "incorrect_answer": random.choice(WRONG_ANSWER),
        "positive_reply":
            "Tak między nami, do dziś nie rozumiem jak ta baba trzęsła tamtym miastem! Zgłoś się potem po odbiór miedziaczków :mee6Coins:",
        "message": message,
        "author": "Kapitan Hubert"
    })

    await answers_question_check({
        "index_question": 8,
        "msg_content": msg_content,
        "correct_answer": "leopold",
        "incorrect_answer":
            "Nie byłeś nawet blisko, idź sprawdź czy masz coś w głowie, a potem wróć, o ile coś znajdziesz...",
        "positive_reply":
            "Podobno pochodził z Carroburga. Nie zapomnij odebrać miedziaczków :mee6Coins:",
        "message": message,
        "author": "Aubrey"
    })


async def participate_pig_quest(message_data):
    if not active_piq_quest:
        return

    msg_content = message_data.get('message_content')
    message = message_data.get('message_obj')
    ability_value = int(msg_content[-1])
    situation_index = msg_content[-3]

    can_pass = validate_is_status_of_action_ok({
        "message_author": message.author,
        "situation_index": situation_index
    })

    if not can_pass:
        return

    roll_result = random.randint(1, 10) + ability_value

    if situation_index == "1":
        write_to_file(
            'pig_quest.txt',
            f'[{message.author.id}]: {str(datetime.datetime.now())}, author: {message.author.name}, situation: {situation_index}, roll result: {roll_result}'
        )
        if roll_result > 9:
            await message.reply(
                f"**:crossed_swords: Głos z Eteru :crossed_swords**:\n**Sukces! ✅🎲** Wynik rzutu na pościg za złodziejem {roll_result}.\n\n||**Głos z Eteru**:\nZ determinacją dołączasz do pościgu. Opuszczasz statek, a Twoje kroki nabierają tempa, gdy zbiegasz z rampy wzdłuż linii brzegowo-portowej 🏃. Twoje oczy szybko wypatrują skrzyżowania, a tam - gęsty tłum, który pochłania gonioną postać. Ruszasz w tamtą stronę i z lekkim przyspieszeniem, wbijasz się w tłum poruszając się zręcznie wśród ludzi, przemykając przez szczeliny między ciałami, ledwo dotykając kogokolwiek.\nW trakcie biegu, wykonujesz szybki manewr uniku, omijając wymachującego ręką przechodnia. Po krótkim wślizgu, wyłaniasz się z tłumu i dostrzegasz poszukiwanego, łapiącego zadyszany oddech, z rękami opartymi na kolanach. Napinasz łydki i z intensywnym odbiciem od ziemi, pędzisz w jego kierunku 🏃. Zanim zdąży się zorientować, już jesteś przy nim, a razem z Tobą kilku pościgowych członków grupy Mercatores. Chwytacie nieznajomego za ubranie i odzyskujecie skradzione pieniądze :mee6Coins:.\n\nZa szybką rekacje, niezwykłą zwinność i czujność, dopisz sobie 1 PD dla Twojej postaci.||"
            )
        else:
            await message.reply(
                f"**:crossed_swords: Głos z Eteru :crossed_swords**:\n**Porażka! ❎🎲** Wynik rzutu na pościg za złodziejem {roll_result}.\n\n||**Głos z Eteru**:\nZ determinacją dołączasz do pościgu. Opuszczasz statek, a Twoje kroki nabierają tempa, gdy zbiegasz z rampy wzdłuż linii brzegowo-portowej 🏃. Twoje oczy szybko wypatrują skrzyżowania, a tam - gęsty tłum, który pochłania gonioną postać. Ruszasz w tamtą stronę i z lekkim przyspieszeniem odczuwając już zmęczenie i brak tchu, wpadasz w tłum. Próbujesz poruszać się zręcznie wśród ludzi, przemykając w szczelinach między ciałami, tak by na nikogo nie wpaść.\n Niestety Twój refleks nie jest w stanie sprotstać temu wyzwaniu z nienacka otrzymujesz cios ręką w twarz ✋ zataczając się delikatnie wpadasz na kolejnych przechodniów.\nNie ma lekko, rzut się nie powiódł, grzeźniesz w tłumie siłując się z napierającymi na Ciebie ludźmi wykonaj teraz komendę !pościg-2 podając po spacji wartość Twojej siły np. !pościg-2 1 (jeżeli Twoja siła wynosi 1).||"
            )
    elif situation_index == "2":
        if roll_result > 9:
            write_to_file(
                'pig_quest.txt',
                f'[{message.author.id}]: {str(datetime.datetime.now())}, author: {message.author.name}, roll result: {roll_result}, situation: {situation_index} saved coins.'
            )

            await message.reply(
                f"**:crossed_swords: Głos z Eteru :crossed_swords:**\n**Sukces! ✅🎲** Wynik rzutu na pościg za złodziejem {roll_result}.\n\n||**Głos z Eteru**:\nStajesz przed wyzwaniem przepychanki z tłumem. Ludzie naciskają na Ciebie ze wszystkich stron, ale nie jesteś nowicjuszem w takich sytuacjach. Napinasz swoje mięśnie 💪, tworząc barierę między sobą a otaczającym Cię chaosem. Z determinacją i dynamicznymi ruchami torujesz sobie drogę przez tłum.\nPo chwili, wychodzisz z rozgardiaszu, lecz zdajesz sobie sprawę, że straciłeś orientację – uciekinier zniknął z pola widzenia 👀. Powracasz na statek bez łupu, lecz również bez szwanku. Może ktoś inny miał więcej szczęścia i udało mu się go złapać 🤞.||"
            )
        else:
            lost_coins = random.randint(25, 35)

            write_to_file(
                'pig_quest.txt',
                f'[{message.author.id}]: {str(datetime.datetime.now())}, author: {message.author.name}, roll result: {roll_result}, lost coins: {lost_coins}, situation: {situation_index}. #TO REMOVE FROM PLAYER'
            )

            await message.reply(
                f"**:crossed_swords: Głos z Eteru :crossed_swords:**\n**Porażka! ❎🎲** Wynik rzutu na pościg za złodziejem {roll_result}.\n\n||**Głos z Eteru**:\nStoisz przed wyzwaniem przetarcia się przez tłum. Ludzie naciskają na Ciebie ze wszystkich stron, gdy już wydaje Ci się, że powoli zaczynasz odzyskiwać kontrolę nad sytuacją. Wtedy nagle, znikąd, wpada na Ciebie całkowicie nieznajomy mężczyzna 😱. Moment zawahania, frustracja narasta. Ruszasz niepewnym krokiem, ale już kolejna osoba zmierza prosto na Ciebie, blokując drogę, a następnie ktoś inny, ociera się o Ciebie i delikatnie popycha impetem swojego chodu tak że tracisz równowagę i prawie lądujesz na ziemi.\nPo dłuższej chwili, wreszcie wydostajesz się z tłumu, a raczej to tłum Cię wypluwa, czujesz się zdezorientowany. Ale to nie koniec problemów – zdajesz sobie sprawę, że Twoja przestrzeń osobista została naruszona! Szybko sprawdzasz swój ekwipunek i odkrywasz, że Twój mieszek został rozcięty, a kilka miedziaków zaginęło. Odwracasz się i patrząc w tłum, już czujesz, że poszukiwanie tych drobnych miedziaczków w tłumie byłoby absurdalnym zadaniem 💸.\n\nTracisz {lost_coins} miedziaków (maksymalnie do zera). Zostaną Ci one odpisane przez MG.||"
            )


@client.event
async def on_ready():
    print(f'Loged in as {client.user}')

    for guild in client.guilds:
        if guild.name in LEGIT_GUILDS:
            # print("GUILD", guild)
            print("GUILD", guild.text_channels)
            target_channel = None
            for channel in guild.text_channels:
                if channel.name == 'ogólny':
                    target_channel = channel

                if channel.name in LEGIT_CHANNELS and channel.permissions_for(
                        guild.me).send_messages:
                    # print("CHANNEL", channel.name)
                    # print("CHANNEL", channel.id)
                    if config.get("welcome"):
                        await send_weloce_section(channel)

            if target_channel:
                # await pig_action_initialization(target_channel)
                if config.get("questions", {}).get("process"):
                    await send_questions(target_channel)

                if config.get("lottery"):
                    await lottery_process.initialize_lottery(target_channel)

                if config.get("eye"):
                    await eye_process.initialize_eye_game(target_channel)

            break


@client.event
async def on_message(message):
    print(message.author)
    role_names = [role.name for role in message.author.roles]
    approved_user = False
    for name in role_names:
        if name in ALLOWED_ROLES:
            approved_user = True
            break

    if message.author == client.user:
        return
    if not approved_user:
        await message.reply("**Aubrey:**\nGdzie się Pan pchasz? Masz Pan Glejt? 📜")

    msg_content = message.content.lower().strip()
    message_data = {"message_content": msg_content, "message_obj": message}

    if msg_content in ['ahoj', 'ahoy', 'ahoj!', 'ahoy!']:
        choosen_greeting = random.choice(HUBERT_GREETINGS)
        if choosen_greeting.find("{}") != -1:
            choosen_greeting = choosen_greeting.replace("{}",
                                                        split_separator_nick(message.author.display_name).capitalize())
        await message.reply(choosen_greeting)

    if msg_content == '!ralf':
        await message.reply("*Z eterycznej pustki dobiega:*\nDUPC! BENC! JEBC! 🐐")

    if msg_content == "!talan":
        await message.reply("**Talan**:\nŻadne, pieczywko, kurwa! 🥖")

    if msg_content == "!aubrey":
        await message.reply("**Aubrey**:\nNie masz co robić? Znaleźć Ci robotę? ⚒️"
                            )

    if msg_content == "!kastner":
        await message.reply("**Kastner**:\nCo się gapisz? Spadaj! 🔥")

    if msg_content == "!hubert":
        await message.reply("**Kapitan Hubert**\nZdrowie poległych! Ho, ho, ho! 🍻")

    questions_pattern = r"^!frantz-[a-z]+-\d{1} .+"
    if re.match(questions_pattern, msg_content):
        await validate_question_section(message_data)

    pig_quest_pattern = r"^!pościg-[1,2]\s\d{1}$"
    if re.match(pig_quest_pattern, msg_content):
        await participate_pig_quest(message_data)

    lottery_pattern = r"^!frantz-loteria-[1,2]\s?.*"
    if re.match(lottery_pattern, msg_content):
        await lottery_process.process_lotery_join(message_data)

    eye_pattern = r"^!frantz-oko-(hubert|kastner).+"
    if re.match(eye_pattern, msg_content):
        await eye_process.process_gameplay(message_data)


client.run(token)
