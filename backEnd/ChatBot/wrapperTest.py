#import Items
from bot_wrapper import BotWrapper

#test 1
#test the initialization of the bot
#we will init the instance and check the instance vars are all empty
bot = BotWrapper()
assert bot.inputs == []
assert bot.outputs == []
assert bot.intentState == -1
assert bot.predictionKnowns == {
    "name": None,
    "G": None,
    "A": None,
    "GP": None,
    "PIM": None,
    "position_D" : None,
    "position_LW" : None
}
print("test 1 passed")
#test 2
#test the determination of the intent state
#we will send a message to the bot and check the intent state
print(bot.initialize(["give me stats for Crosby in 2017", "string"]))
assert bot.intentState == 0
bot = BotWrapper()
#now lets test the prediction call
print(bot.initialize(["can you predict the round that bob dylan will be drafted in", "string"]))
print(bot.intentState)
#assert bot.intentState == 1
print(bot.initialize(["bob dylan", "name"]))
print(bot.initialize(["45", "GP"]))
print(bot.initialize(["555555", "G"]))
print(bot.initialize(["58", "A"]))
print(bot.initialize(["10", "PIM"]))
print(bot.initialize(["0", "position_D"]))
print(bot.initialize(["1", "position_LW"]))



