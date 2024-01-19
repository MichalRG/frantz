import discord
import random
from utils import try_parse_int, split_separator_nick, write_to_file, get_content
import uuid
from datetime import datetime


class EyeGame:
    HUBERT_FAIL_RESPONSES = [
        "Cholera, znowu pech!", "Morze miało dziś inny plan.",
        "Kapitani mają gorsze dni.", "Kostki dzisiaj zdradliwe jak morze.",
        "Prawdziwa burza nie szczęścia!", "Ktoś musiał przekląć te kości!",
        "Fale szczęścia opuściły mnie.", "Dziś fala nie na moją stronę.",
        "Morskie demony mi nie sprzyjają.", "Szczęście dziś u innych portów.",
        "Tym razem los mi nie sprzyjał.", "Takie morskie sztormy życia.",
        "Dziś bez łupu, panowie i panie!", "Kapryśna jak fala przy pełni.",
        "Morski los ma dziś humory.", "Czas chyba wyruszyć na inne wody.",
        "Jak w sztormie, tracę kurs.", "Czyjeś przekleństwo na tych kościach.",
        "Fala szczęścia odpłynęła.", "Zgubiony kurs w grze losu."
    ]
    KASTNER_FAIL_RESPONSES = [
        "Eh...", "Argh...", "Nosz kurwa!", "Kurwa!",
        "Czy ty przypadkiem nie podmieniłeś kości!?",
        "No co jest! Widziałem 9-tkę!", "Tak blisko..."
    ]
    HUBERT_SUCCESS_RESPONSES = [
        "Pełne żagle szczęścia!", "Morze sprzyja dziś starym wilkom!",
        "Złapaliśmy pomyślny wiatr!", "Jak prawdziwy kapitan na fali!",
        "Złoto morskich bogów dla mnie!", "Na pokładzie szczęścia dziś!",
        "Jak trafny strzał z armaty!", "Fala fortuny na mojej stronie!",
        "Trafiony, zatopiony, wygrany!", "Na morzu szczęścia jestem kapitanem!",
        "Lodowa góra szczęścia dla wilka!", "Wilk morski wie, kiedy atakować!",
        "Kurs na zwycięstwo ustawiony!", "Jak śmiałe abordażowanie sukcesu!",
        "Łup pełen szczęścia!", "Złoto Manna w moich rękach!",
        "Kapitański rzut na pokładzie!", "Jak wspaniały łup na morzu!",
        "Przygoda się udała, panowie!", "Wiatr fortuny w moich żaglach!"
    ]
    KASTNER_SUCCESS_RESPONSES = [
        "Trzeba było fikać? Ha!", "Ha! Cienias!", "Łatwizna!",
        "Ha, nie tylko Sigmar po mojej stronie",
        "To są umiejętności, a nie szczęście!"
    ]

    active_game = False
    hubert_enemy_id = None
    kastner_enemy_id = None
    id_hubert_game = "1"
    id_kastner_game = "2"
    is_hubert_busy = False
    is_kastner_busy = False
    draw_hubert_strategy = 1
    draw_kastner_strategy = 2
    hubert_dice = 1
    kastner_dice = 1
    player_hubert_dice = 1
    player_kastner_dice = 1
    whose_turn_hubert = "Hubert"
    whose_turn_kastner = "Kastner"

    async def initialize_eye_game(self, channel):
        self.active_game = True

        await channel.send(
            '** Kapitan Hubert **\nLudziska, zapraszam do wspólnej gry w Oko 👁️! Ho, ho, ho! Gra odbywać się będzie na dolnym pokładzie, zagrać można będzie ze mną i z Kastnerem, w ramach praktyki i zrozumienia zasad. A apropo reguł spisał je Majtek Solveig. Odczytam je teraz dla nieczytliwych, a Ci co potrafią czytać 📖 to będą one wywieszone na tablicy. 📜\n*Kapitan Hubert wyciąga zwitek papieru i zaczyna czytać, gdy kończy, przybija go do tablicy*\n\n||By wziąć udział w grze Oko, napisz !frantz-oko-hubert XXX, lub !frantz-oko-kastner YYY, gdzie XXX i YYY to liczba miedziaków, które stawiasz. Druga strona dokłada taką samą pulę, a zwycięzca bierze wszystko np. !frantz-oko-hubert 5 <- oznacza to że wyzywasz Kapitana Huberta na 5 miedziaków, zwycięzca otrzymuje 10. Rzuty dokonywane są po stronie serwera poprzez wylosowanie odpowiednich wartości.||'
        )
        await channel.send(file=discord.File('./OkoRule.png'))

    async def process_gameplay(self, message_data):
        if not self.active_game:
            return

        msg_content = message_data.get('message_content')
        message = message_data.get('message_obj')

        if msg_content.startswith('!frantz-oko-hubert '):
            if not self.is_hubert_busy:
                did_we_play = self.__check_player_status(str(message.author.id),
                                                         'hubert')
                if did_we_play:
                    await message.reply(
                        "**Kapitan Hubert**\nPanie my już graliśmy, wystarczy tego przewalania miedziaków. Innym razem, chodźmy się napić 🍻"
                    )
                    return
                await self.__process_start_hubert_gameplay(message, msg_content)
            else:
                await message.reply(
                    "**Kapitan Hubert**\nTeraz nie mogę, już gram! 🤔 Zaproponuj później!"
                )
        elif msg_content.startswith('!frantz-oko-kastner '):
            if not self.is_kastner_busy:
                did_we_play = self.__check_player_status(str(message.author.id),
                                                         'kastner')
                if did_we_play:
                    await message.reply(
                        "**Kastner**\nHmmn, nie graliśmy już razem? Nie mam więcej dla Ciebie czasu idź męcz Huberta... 🖐️"
                    )
                    return
                await self.__process_kastner_gameplay(message, msg_content)
            else:
                await message.reply(
                    "**Kastner**\nGrrr! Nie widzisz, że gram? Spieprzaj! 🤬")
        elif msg_content == '!frantz-oko-hubert-rzucam' and self.is_hubert_busy and self.hubert_enemy_id == message.author.id:
            await self.__player_roll(message, 'Hubert')
        elif msg_content == '!frantz-oko-hubert-dobieram' and self.is_hubert_busy and self.hubert_enemy_id == message.author.id:
            await self.__player_draw(message, 'Hubert')
        elif msg_content == '!frantz-oko-kastner-rzucam' and self.is_kastner_busy and self.kastner_enemy_id == message.author.id:
            await self.__player_roll(message, 'Kastner')
        elif msg_content == '!frantz-oko-kastner-dobieram' and self.is_kastner_busy and self.kastner_enemy_id == message.author.id:
            await self.__player_draw(message, 'Kastner')

    async def __process_kastner_gameplay(self, message, user_command_answer):
        bid = user_command_answer.split(f'!frantz-oko-kastner ', 1)[1].strip()

        bid_number, is_number = try_parse_int(bid)

        if not is_number or bid_number <= 15:
            await message.reply(
                "**Kastner**\nW kule ze mną lecisz dawaj więcej miedziaków! 🪙")
            return
        elif bid_number > 40:
            await message.reply(
                "**Kastner**\nNie rozpędzasz się kolego? Chcesz Inkwizytora ograć, ze wszystkich miedziaków? Zastanów się..."
            )
            return
        if self.is_kastner_busy:
            await message.reply(
                "**Kastner:**\nChwila moment, kurwa!\n\n||Spróbuj za chwilę.||")
            return
        self.is_kastner_busy = True
        self.id_kastner_game = uuid.uuid4()
        self.kastner_enemy_id = message.author.id

        kastner_initiative_roll = 0
        player_initiative_roll = 0

        while kastner_initiative_roll == player_initiative_roll:
            kastner_initiative_roll, player_initiative_roll = [
                random.randint(1, 10), random.randint(1, 10)
            ]
        write_to_file(
            'oko/gamelog.txt',
            f'[{self.id_kastner_game}] {datetime.now()} Kastner vs {message.author.name} ({message.author.id}), Bid: {bid_number}, Initiative roll: <kastner:{kastner_initiative_roll}>,<player: {player_initiative_roll}>\n'
        )

        if player_initiative_roll < kastner_initiative_roll:
            self.whose_turn_kastner = "Player"
        else:
            self.whose_turn_kastner = "Kastner"

        await message.reply(
            f"**Głos z Eteru:**\nKości turlają się po beczce i mamy wyniki rzutów na inicjatywę:\nKastner:{kastner_initiative_roll}\n{split_separator_nick(message.author.display_name).capitalize()}:{player_initiative_roll}\n\n**Kastner**:\nHmnn... {'Zaczynasz kolego... Rzucaj 🗡️, albo dobieraj 🎲' if self.whose_turn_kastner == 'Player' else 'Patrz i ucz się! :palm_up_hand:'}\n\n||Aby dobrać wpisz !frantz-oko-X-dobieram. Aby rzucać dostępną pulą kostek wpisz !frantz-oko-X-rzucam, gdzie X to hubert, albo kastner zależy od tego z kim grasz.||"
        )

        self.__define_strategy('Kastner')

        if self.whose_turn_kastner == "Kastner":
            await self.__display_I_draw(message, {
                "identifier_player": "Kastner",
                "player_name": "Kastner"
            })

    async def __process_start_hubert_gameplay(self, message,
                                              user_command_answer):
        bid = user_command_answer.split(f'!frantz-oko-hubert ', 1)[1].strip()

        bid_number, is_number = try_parse_int(bid)

        if not is_number or bid_number <= 0:
            await message.reply(
                "**Kapitan Hubert**\nPanie no sypnij pan trochę miedziaków! 🪙")
            return
        elif bid_number > 10:
            await message.reply(
                "**Kapitan Hubert**\nNiech mnie kule biją! Ja gram tylko dla zabawy, zaproponuj mniejszą kwotę 😱 Taką poniżej 10 miedziaków."
            )
            return
        if self.is_hubert_busy:
            await message.reply(
                "**Kapitan Hubert:**\nCzekaj, czekaj, moment.\n\n||Spróbuj za chwilę.||"
            )
            return
        self.is_hubert_busy = True
        self.id_hubert_game = uuid.uuid4()
        self.hubert_enemy_id = message.author.id

        hubert_initiative_roll = 0
        player_initiative_roll = 0

        while hubert_initiative_roll == player_initiative_roll:
            hubert_initiative_roll, player_initiative_roll = [
                random.randint(1, 10), random.randint(1, 10)
            ]

        write_to_file(
            f'oko/gamelog.txt',
            f'[{self.id_hubert_game}] {datetime.now()} Kastner vs {message.author.name} ({message.author.id}), Bid: {bid_number}, Initiative roll: <hubert:{hubert_initiative_roll}>,<player: {player_initiative_roll}>\n'
        )

        if player_initiative_roll < hubert_initiative_roll:
            self.whose_turn_hubert = "Player"
        else:
            self.whose_turn_hubert = "Hubert"

        await message.reply(
            f"**Głos z Eteru:**\nKości turlają się po beczce i mamy wyniki rzutów na inicjatywę:\nKapitan Hubert:{hubert_initiative_roll}\n{split_separator_nick(message.author.display_name).capitalize()}:{player_initiative_roll}\n\n**Kapitan Hubert**:\nHa! {'Zaczynasz. Rzucaj 🗡️, albo dobieraj 🎲' if self.whose_turn_hubert == 'Player' else 'Ojojoj! Zaczynam ja! 🍻'}\n\n||Aby dobrać wpisz !frantz-oko-X-dobieram. Aby rzucać dostępną pulą kostek wpisz !frantz-oko-X-rzucam, gdzie X to albo hubert, albo kastner zależy od tego z kim grasz.||"
        )

        self.__define_strategy('Hubert')

        if self.whose_turn_hubert == "Hubert":
            if self.draw_hubert_strategy == 1:
                await self.__display_I_play(
                    message, {
                        "identifier_player": "Hubert",
                        "player_name": "Kapitan Hubert",
                        "amount_of_rolls": 1,
                        "lose_message": random.choice(self.HUBERT_FAIL_RESPONSES)
                    })
            else:
                await self.__display_I_draw(message, {
                    "identifier_player": "Hubert",
                    "player_name": "Kapitan Hubert"
                })

    async def __perform_enemy_action(self, message, player_name):
        if player_name == "Hubert":
            if self.draw_hubert_strategy == self.hubert_dice:
                await self.__display_I_play(
                    message, {
                        "identifier_player": "Hubert",
                        "player_name": "Kapitan Hubert",
                        "amount_of_rolls": self.hubert_dice,
                        "lose_message": random.choice(self.HUBERT_FAIL_RESPONSES)
                    })
            else:
                await self.__display_I_draw(message, {
                    "identifier_player": "Hubert",
                    "player_name": "Kapitan Hubert"
                })
        elif player_name == "Kastner":
            if self.draw_kastner_strategy == self.kastner_dice:
                await self.__display_I_play(
                    message, {
                        "identifier_player": "Kastner",
                        "player_name": "Kastner",
                        "amount_of_rolls": self.kastner_dice,
                        "lose_message": random.choice(self.KASTNER_FAIL_RESPONSES)
                    })
            else:
                await self.__display_I_draw(message, {
                    "identifier_player": "Kastner",
                    "player_name": "Kastner"
                })

    async def __display_I_draw(self, message, player_object):
        identifier = player_object.get('identifier_player')
        player_name = player_object.get('player_name')

        await message.reply(
            f"**{player_name}:**\nDobieram! 🎲\n\n||Aby dobrać wpisz !frantz-oko-X-dobieram. Aby rzucać dostępną pulą kostek wpisz !frantz-oko-X-rzucam, gdzie X to albo hubert, albo kastner zależy od tego z kim grasz.||"
        )
        if identifier == "Hubert":
            self.hubert_dice += 1
            self.whose_turn_hubert = "Player"
            write_to_file(
                f'oko/gamelog.txt',
                f'[{self.id_hubert_game}] {datetime.now()}: Hubert is drawing and he has {self.hubert_dice} dices\n'
            )
        elif identifier == "Kastner":
            self.kastner_dice += 1
            self.whose_turn_kastner = "Player"
            write_to_file(
                f'oko/gamelog.txt',
                f'[{self.id_kastner_game}] {datetime.now()}: Kastner is drawing and he has {self.kastner_dice} dices\n'
            )

    async def __player_draw(self, message, barrel):
        if barrel == "Hubert":
            self.player_hubert_dice += 1
            self.whose_turn_hubert = "Hubert"
            write_to_file(
                f'oko/gamelog.txt',
                f'[{self.id_hubert_game}] {datetime.now()}, {message.author.name} is drawing and has {self.player_hubert_dice} dices\n'
            )
        if barrel == "Kastner":
            self.player_kastner_dice += 1
            self.whose_turn_kastner = "Kastner"
            write_to_file(
                f'oko/gamelog.txt',
                f'[{self.id_kastner_game}] {datetime.now()}, {message.author.name} is drawing and has {self.player_kastner_dice} dices\n'
            )
        await message.reply(
            f"**Głos z Eteru:**\n{split_separator_nick(message.author.display_name).capitalize()} dobiera kość 🎲. Tura przeciwnika."
        )
        await self.__perform_enemy_action(message, barrel)

    async def __display_I_play(self, message, player_object):
        identifier = player_object.get('identifier_player')
        player_name = player_object.get('player_name')
        amount_of_rolls = player_object.get('amount_of_rolls')
        lose_message = player_object.get('lose_message')
        result_rolls = []

        for roll in range(amount_of_rolls):
            result_rolls.append(random.randint(1, 10))

        await message.reply(
            f"**Głos z Eteru:**\n{player_name} sięga po kości 🎲 i rzuca. {'Kość mknie' if amount_of_rolls == 1 else 'Kości mkną'} po wieku beczki i...\nWynik: {', '.join(map(str, result_rolls))}"
        )

        if 9 in result_rolls:
            if identifier == "Hubert":
                write_to_file(
                    f'oko/gamelog.txt',
                    f'[{self.id_hubert_game}] {datetime.now()}, Hubert is winning with the roll result: {result_rolls}\n'
                )
                write_to_file('oko/hubertGamblers.txt', str(message.author.id))
                await self.__announce_winner(message, 'Hubert')
                self.__reset_stats("Hubert")
            elif identifier == "Kastner":
                write_to_file(
                    f'oko/gamelog.txt',
                    f'[{self.id_kastner_game}] {datetime.now()}, Kastner is winning with the roll result: {result_rolls}\n'
                )
                write_to_file('oko/kastnerGamblers.txt', str(message.author.id))
                await self.__announce_winner(message, 'Kastner')
                self.__reset_stats("Kastner")
            return
        else:
            await message.reply(
                f"**{player_name}:**\n{lose_message} Twoja kolej :confounded:\n\n||Aby dobrać wpisz !frantz-oko-X-dobieram. Aby rzucać dostępną pulą kostek wpisz !frantz-oko-X-rzucam, gdzie X to albo hubert, albo kastner zależy od tego z kim grasz.||"
            )
            if identifier == "Hubert":
                write_to_file(
                    f'oko/gamelog.txt',
                    f'[{self.id_hubert_game}] {datetime.now()}, Hubert rolls with result: {result_rolls}\n'
                )
                self.whose_turn_hubert = "Player"
            elif identifier == "Kastner":
                write_to_file(
                    f'oko/gamelog.txt',
                    f'[{self.id_kastner_game}] {datetime.now()}, Kastner rolls with result: {result_rolls}\n'
                )
                self.whose_turn_kastner = "Player"

    async def __player_roll(self, message, barrel):
        result_rolls = []
        if barrel == "Hubert":
            for roll in range(self.player_hubert_dice):
                result_rolls.append(random.randint(1, 10))

            await message.reply(
                f"**Głos z Eteru:**\n{split_separator_nick(message.author.display_name).capitalize()} sięga po kości 🎲 i rzuca. {'Kość mknie' if len(result_rolls) == 1 else 'Kości mkną'} po wieku beczki i...\nWynik: {', '.join(map(str, result_rolls))}"
            )

            if 9 in result_rolls:
                write_to_file(
                    f'oko/gamelog.txt',
                    f'[{self.id_hubert_game}] {datetime.now()}, {message.author.name} is winning against Hubert with the roll result: {result_rolls}\n'
                )
                write_to_file('oko/hubertGamblers.txt', str(message.author.id))
                await self.__announce_winner(message, 'Player')
                self.__reset_stats("Hubert")
                return
            else:
                write_to_file(
                    f'oko/gamelog.txt',
                    f'[{self.id_hubert_game}] {datetime.now()}, {message.author.name} rolls with result: {result_rolls}\n'
                )
                await message.reply('**Kapitan Hubert**:\nMoja kolej 🎲')
                self.whose_turn_hubert = "Hubert"
                await self.__perform_enemy_action(message, barrel)
        if barrel == "Kastner":
            for roll in range(self.player_kastner_dice):
                result_rolls.append(random.randint(1, 10))

            await message.reply(
                f"**Głos z Eteru:**\n{split_separator_nick(message.author.display_name).capitalize()} sięga po kości 🎲 i rzuca. {'Kość mknie' if len(result_rolls) == 1 else 'Kości mkną'} po wieku beczki i...\nWynik: {', '.join(map(str, result_rolls))}"
            )

            if 9 in result_rolls:
                write_to_file(
                    f'oko/gamelog.txt',
                    f'[{self.id_kastner_game}] {datetime.now()}, {message.author.name} is winning against Kastner with the roll result: {result_rolls}\n'
                )
                write_to_file('oko/kastnerGamblers.txt', str(message.author.id))
                await self.__announce_winner(message, 'Player')
                self.__reset_stats("Kastner")
                return
            else:
                write_to_file(
                    f'oko/gamelog.txt',
                    f'[{self.id_kastner_game}] {datetime.now()}, {message.author.name} rolls with result: {result_rolls}\n'
                )
                await message.reply('**Kastner**:\nPfff 🎲')
                self.whose_turn_kastner = "Kastner"
                await self.__perform_enemy_action(message, barrel)

    def __reset_stats(self, base_stats_indicator):
        if base_stats_indicator == "Hubert":
            self.is_hubert_busy = False
            self.draw_hubert_strategy = 1
            self.hubert_dice = 1
            self.player_hubert_dice = 1
            self.whose_turn_hubert = "Hubert"
        elif base_stats_indicator == "Kastner":
            self.is_kastner_busy = False
            self.draw_kastner_strategy = 2
            self.kastner_dice = 1
            self.player_kastner_dice = 1
            self.whose_turn_kastner = "Kastner"

    async def __announce_winner(self, message, name):
        if name == "Hubert":
            await message.reply(
                f"**Kapitan Hubert:**\n{random.choice(self.HUBERT_SUCCESS_RESPONSES)}\n*Przeciwnik zgarnia miedziaki z beczki* \n||Miedziaki zostaną Ci odpisane pod koniec dnia||."
            )
        elif name == "Kastner":
            await message.reply(
                f"**Kastner:**\n{random.choice(self.KASTNER_SUCCESS_RESPONSES)}\n*Przeciwnik zgarnia miedziaki z beczki* \n||Miedziaki zostaną Ci odpisane pod koniec dnia||."
            )
        elif name == "Player":
            await message.reply(
                f"**Głos z Eteru:**\n{split_separator_nick(message.author.display_name).capitalize()} odnośnisz zwycięstwo! 🏆 Twój przeciwnik rzuca Ci miedziaki na beczkę i odchodzi."
            )

    def __check_player_status(self, id, file_name_base):
        content = get_content(f"oko/{file_name_base}Gamblers.txt")
        if id in content:
            return True

    def __define_strategy(self, name):
        if name == "Hubert":
            self.draw_hubert_strategy = random.randint(1, 2)
            self.hubert_dice = 1
            self.player_hubert_dice = 1
        elif name == "Kastner":
            self.draw_kastner_strategy = random.randint(2, 4)
            self.kasner_dice = 1
            self.player_kastner_dice = 1
