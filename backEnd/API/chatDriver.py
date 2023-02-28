from ChatBot import ChatBot

class ChatDriver:

    def __init__(self):
        self.chatbot = ChatBot()

    def getResponse(self, message):
        return self.chatbot.getResponse(message)