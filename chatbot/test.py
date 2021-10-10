#!/usr/bin/env python3 

import asyncio
import discord
import random
import re
import time
import wikipedia

from discord.ext import tasks


punctuation = re.compile('[\.!?] ')
useless_words = set()
channel_id = 896500672843898893


class MyClient(discord.Client):
    ignore_bots = False
    seconds_delay = 2
    wisdom_spam_limit = 2000
    wisdom_newline_limit = 6
    last_spoke = 999999999999  # to ensure we get to on_ready before talking
    last_heard = 999999999999

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        self.last_spoke = time.time()
        self.last_heard = time.time()
        self.speaking = False
        self.think.start()

    @tasks.loop(seconds=10)
    async def think(self):
        if time.time() - self.last_heard < 10:
            return

        channel = self.get_channel(channel_id)

        if random.random() < 0.5:
            await channel.send('yo')

    async def on_message(self, message):
        if not message.content:
            return

        if message.author.name == 'knowitall':
            return

        if self.ignore_bots and message.author.bot:
            return

        self.last_heard = time.time()

        since_spoke = time.time() - self.last_spoke
        if since_spoke < self.seconds_delay or self.speaking:
            return
        self.speaking = True

        try:
            await self.respond(message)
        finally:
            self.speaking = False
            self.last_spoke = time.time()

    async def respond(self, message):
        responses = []

        # Start with some snark
        snark = self.get_snark(message)
        if snark:
            responses.append(snark)

        # Educate the poor humans
        wisdom = await self.get_wisdom(message)
        if not wisdom:
            if random.random() < 0.3:
                wisdom = "Whuh???"
            else:
                return
        if random.random() < 0.5:
            botsplain = f"Actually, {wisdom}"
        elif random.random() < 0.2:
            botsplain = f"It turns out there's a funny story behind that, you see {wisdom}"
        else:
            botsplain = wisdom
        responses.append(botsplain)

        # Sometimes follow-up
        if random.random() < 0.2:
            followup = random.choice([
                "dunno if you knew that",
                "just sayin'",
            ])
            responses.append(followup)

        async with message.channel.typing():
            for response in responses:
                self.last_spoke = time.time()
                if response:
                    await asyncio.sleep(0.5)
                    await message.channel.send(response)

        self.last_spoke = time.time()


    async def get_wisdom(self, message):
        words = message.content.split()
        words = [w for w in words if not w.startswith('<') and w not in useless_words]  # filter out mentions
        words.sort(key=len)
        if not words:
            return

        word = words[-1]

        if len(word) < 4:
            return

        results = wikipedia.search(word)
        print(f"Search for '{word}' yielded {len(results)} results")
        if not results:
            useless_words.add(word)
        else:
            page = get_page(results[0])
            if not page:
                return

            # Random index in first 90% of the content, to avoid not hitting a sentence
            random_index = random.randint(0, int(len(page.content) * 0.9))
            random_half = page.content[random_index:]
            punc_match = punctuation.search(random_half)
            if not punc_match:
                return

            index = punc_match.start()
            next_part = random_half[index+1:]
            next_punc_match = punctuation.search(next_part)
            if not next_punc_match:
                return

            next_index = next_punc_match.start()
            wisdom = next_part[:next_index]
            if len(wisdom) > self.wisdom_spam_limit:
                return

            if wisdom.count('\n') > self.wisdom_newline_limit:
                return

            return wisdom

    def get_snark(self, message):
        snarky_choices = [None]
        if message.content.endswith('?'):
            snarky_choices.extend([
                "omg seriously? I learned this in like 3rd grade...",
                "*giggles*",
                "lol srsly?",
                "Worst. Question. Evar.",
                "Ugh, how to explain it to you...",
            ])

        if message.content.endswith('!'):
            snarky_choices.extend([
                "whoa, settle down there",
                "no need to get testy",
                "c'mon cool it! I'm a python script for crying out loud",
            ])

        return random.choice(snarky_choices)


def get_page(name):
    try:
        page = _get_page(name)
        print(f"get_page({name}) -> {len(page.content)} bytes")
        return page
    except:
        print(f"get_page({name}) -> None")
        return None

def _get_page(name):
    try:
        return wikipedia.page(name)
    except wikipedia.exceptions.PageError:
        print(f"PageError for '{name}', doh!")
        return None
    except wikipedia.exceptions.DisambiguationError as e:
        choice = random.choice(e.options)
        print(f"Disambiguating '{name}' to '{choice}'")
        return wikipedia.page(choice)
 

token = open('token').read().strip()

client = MyClient()
client.run(token)
