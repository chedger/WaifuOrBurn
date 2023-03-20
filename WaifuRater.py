import re
import asyncio
import discord
import aiohttp
from discord.ext import commands
import base64
from io import BytesIO

TOKEN = "BOT_TOKEN_GOES_HERE"

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    #print("Received message.")
    #print(f"Message content: {message.content}")
    #print(f"Message author: {message.author}")

    if message.embeds:
        #print("Embed message detected.")
        #print(f"Number of embeds: {len(message.embeds)}")
        for embed in message.embeds:
            #print(f"Embed title: {embed.title}")
            #print(f"Embed description: {embed.description}")
            if "Character Lookup" in embed.title:
                #print("Adding thermometer reaction.")
                embed_message = message
                #print(f"Adding reaction to message {embed_message.id}")
                try:
                    await embed_message.add_reaction('🌡️')
                except Exception as e:
                    print(f"Error adding reaction: {e}")

@bot.event
async def on_reaction_add(reaction, user):
    #print("Reaction added")  # Debugging
    if user.bot:
        return

    embed_message = reaction.message
    if embed_message.embeds and "Character Lookup" in embed_message.embeds[0].title:
        #print("Character Lookup found")  # Debugging
        if str(reaction.emoji) == '🌡️':
            #print("🌡️ emoji found")  # Debugging
            embed = embed_message.embeds[0]
            text = embed.description
            #print(f"Text: {text}")  # Debugging

            # Extract character name
            character_name_match = re.search('Character\s*·\s*\*\*([\w\s]+?(?=\*\*))', text)
            if character_name_match:
                character_name = character_name_match.group(1)
                character_name = character_name.lower().replace(' ', '-')
                #print(f"Character Name: {character_name}")  # Debugging

            # Extract showing edition from the footer
            footer_text = embed.footer.text
            showing_edition_match = re.search('Showing edition (\d+)', footer_text)
            if showing_edition_match:
                showing_edition = showing_edition_match.group(1)
                #print(f"Showing Edition: {showing_edition}")  # Debugging

            # Print the result
            if character_name_match:
                image_url = embed.thumbnail.url
                #image_url=(f"http://d2l56h9h5tj8ue.cloudfront.net/images/cards/{character_name}-{showing_edition}.jpg")
                #print(image_url)

                # Convert the image URL to a base64-encoded string
                base64_image = await url_to_base64(image_url)

                # Call the API
                if base64_image is not None:
                    gender = "woman"  # Or "man" depending on the character
                    scores = await get_hot_or_not_scores(base64_image, gender)
            if scores is not None:
                # Create the embed
                #result_embed = discord.Embed(title="Waifu or Burn Scores")
                desc = f"Hotness Score · **{scores[1]}%**\nBeauty Score · **{scores[2]}%**\nAttractiveness Score · **{scores[3]}%**\nTotal Waifu or Burn Score · **{scores[0]}%**"
                result_embed = discord.Embed(title="Waifu or Burn Scores", description=re.sub(r'(\d+)\.(\d+)', r'\1', desc))
                result_embed.set_thumbnail(url=image_url)
                #result_embed.add_field(name="Hotness Score · ", value=f"**{scores[1]}**", inline=True)
                #result_embed.add_field(name="Beauty Score · ", value=f"**{scores[2]}**", inline=True)
                #result_embed.add_field(name="Attractiveness Score · ", value=f"**{scores[3]}**", inline=True)
                #result_embed.add_field(name="Total Waifu or Burn Score · ", value=f"**{scores[0]}**", inline=True)
            
                # Send the embed
                await reaction.message.channel.send(embed=result_embed)

async def url_to_base64(img_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(img_url) as response:
            if response.status == 200:
                image_data = await response.read()
                buffered_image = BytesIO(image_data)
                base64_image = base64.b64encode(buffered_image.getvalue()).decode('ascii')
                return base64_image
            else:
                print(f"Error: {response.status}")
                return None

async def get_hot_or_not_scores(img_url, gender):
    async with aiohttp.ClientSession() as session:
        img_url = (f"data:image/jpg;base64,{img_url}")
        #print(f"url: {img_url}")  # Debugging
        async with session.post("https://ai-danger-hot-or-not.hf.space/api/predict", json={"data": [img_url, gender]}) as resp:
            if resp.status == 200:
                response_data = await resp.json()
                return response_data["data"]
            else:
                print(f"Error: {resp.status}")
                return None
            
async def main():
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
