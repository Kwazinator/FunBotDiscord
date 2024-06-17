import discord

GETIMAGE = {
    'Carentan': 'https://static.wikia.nocookie.net/hellletloose/images/a/aa/Carentan.jpg/revision/latest/scale-to-width-down/1000?cb=20201227220018',
    'Omaha Beach': 'https://static.wikia.nocookie.net/hellletloose/images/8/8f/Omaha.jpg/revision/latest/scale-to-width-down/1000?cb=20201227220327',
    'Purple Heart Lane': 'https://static.wikia.nocookie.net/hellletloose/images/3/31/Purple.png/revision/latest/scale-to-width-down/1000?cb=20210626124911',
    'Foy': 'https://static.wikia.nocookie.net/hellletloose/images/3/3b/Hll_Map_Foy_StrongPoints.png/revision/latest/scale-to-width-down/1000?cb=20210926173013',
    'Hill 400': 'https://static.wikia.nocookie.net/hellletloose/images/d/d2/Hill400.png/revision/latest/scale-to-width-down/1000?cb=20210727093229',
    'Sainte-Marie-du-Mont': 'https://static.wikia.nocookie.net/hellletloose/images/6/6c/SMDMV2_TacMap01_SP.png/revision/latest/scale-to-width-down/1000?cb=20210926174337',
    'Hürtgen Forest': 'https://static.wikia.nocookie.net/hellletloose/images/3/31/HurtgenV2_7_26_21.png/revision/latest/scale-to-width-down/1000?cb=20220209213720',
    'Sainte-Mère-Église': 'https://static.wikia.nocookie.net/hellletloose/images/9/94/Eglise.jpg/revision/latest/scale-to-width-down/1000?cb=20201227220035',
    'Stalingrad': 'https://static.wikia.nocookie.net/hellletloose/images/7/76/Stalingrad_TacMap03.png/revision/latest/scale-to-width-down/1000?cb=20210626125249',
    'Kursk': 'https://static.wikia.nocookie.net/hellletloose/images/9/98/Kursk-tactical-map.png/revision/latest/scale-to-width-down/1000?cb=20210727091018',
    'Utah Beach': 'https://static.wikia.nocookie.net/hellletloose/images/f/f9/Utah.jpg/revision/latest/scale-to-width-down/1000?cb=20201227220357',
}


class HLL_View(discord.ui.View):
    answer1 = None
    @discord.ui.select(
        placeholder="Which map would you like to see",
        options=[
            discord.SelectOption(label='Carentan', value='Carentan'),
            discord.SelectOption(label='Omaha Beach', value='Omaha Beach'),
            discord.SelectOption(label='Purple Heart Lane', value='Purple Heart Lane'),
            discord.SelectOption(label='Foy', value='Foy'),
            discord.SelectOption(label='Hill 400', value='Hill 400'),
            discord.SelectOption(label='Sainte-Marie-du-Mont', value='Sainte-Marie-du-Mont'),
            discord.SelectOption(label='Hürtgen Forest', value='Hürtgen Forest'),
            discord.SelectOption(label='Sainte-Mère-Église', value='Sainte-Mère-Église'),
            discord.SelectOption(label='Stalingrad', value='Stalingrad'),
            discord.SelectOption(label='Kursk', value='Kursk'),
            discord.SelectOption(label='Utah Beach', value='Utah Beach'),
        ]
    )
    async def select_map(self, interaction:discord.Interaction, select_item: discord.ui.Select):
        self.answer1 = GETIMAGE[select_item.values[0]]
        self.children[0].disabled = True
        #can place a follow up quiestion here if needed
        await interaction.message.edit(view=self) # updates the view to reflect your response
        await interaction.response.defer()
        self.stop()

