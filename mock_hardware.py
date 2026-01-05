class MockOutputDevice:
    def __init__(self, pin):
        self.pin = pin
        self.state = False
        self.value = 0

    def on(self):
        self.state = True
        self.value = 1

    def off(self):
        self.state = False
        self.value = 0

    def toggle(self):
        if self.state: self.off()
        else: self.on()

class MockPWMOutputDevice(MockOutputDevice):
    def __init__(self, pin):
        super().__init__(pin)
        self._value = 0.0

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = max(0.0, min(1.0, float(val)))
        self.state = self._value > 0

class MockCPUTemperature:
    @property
    def temperature(self):
        # Return a fake temperature that varies slightly
        import random
        return 45.0 + random.uniform(-2, 5)
