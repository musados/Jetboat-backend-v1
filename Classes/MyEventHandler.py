from Classes.EventHandler import EventHandler

class MyEventHandler(EventHandler):
    def __init__(self, message):
        self.message = message
	
    def __str__(self):
        return "Message from other class: " + repr(self.message)