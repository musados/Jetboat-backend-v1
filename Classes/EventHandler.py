class EventHandler(object):
    callbacks = None
	
    def on(self, EHname, callback):
        if self.callbacks is None:
            self.callbacks = {}
	
        if EHname not in self.callbacks:
            self.callbacks[EHname] = [callback]
        else:
            self.callbacks[EHname].append(callback)
	
    def trigger(self, EHname, data=None):
        if self.callbacks is not None and EHname in self.callbacks:
            for callback in self.callbacks[EHname]:
                callback(self, data)
