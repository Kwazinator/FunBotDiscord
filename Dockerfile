 FROM python:3
 FROM gorialis/discord.py

 RUN mkdir -p /usr/src/bot
 WORKDIR /usr/src/bot
 COPY . .
 RUN pip install -r requirements.txt

 CMD [ "python3", "FunBotDiscord.py" ]

