"""
Class to provide a standard interface to all periphreals such as IO pins, strain gauges, light sensors, UART, etc
"""

MAIN_MONITOR=1
AUX_MONITOR=2

class Environment:
    MAX_TIME_SECONDS=60*60 #number of seconds allowed to solve the room before room auto-times out
    
    def __init__(self,environment_type):
        self.enviornment_type=environment_type
        if(self.environment_type==self.MAIN_MONITOR):
            pass#TODO
        elif(self.environment_type==self.AUX_MONITOR):
            pass#TODO
        else:
            raise ValueError("Undefined environment_type: "+str(self.environment_type))
        
    def init(self):
        if(self.environment_type==self.MAIN_MONITOR):
            pass#TODO
        elif(self.environment_type==self.AUX_MONITOR):
            pass#TODO
    
    def dispose(self):
        if(self.environment_type==self.MAIN_MONITOR):
            pass#TODO
        elif(self.environment_type==self.AUX_MONITOR):
            pass#TODO
        pass
    
    """
    Start timer to count down
    """
    def startTimer():
        pass#TODO
    
    """
    Stop the room timer
    """
    def stopTimer():
        pass#TODO
    
    """
    Returns the status of the timer
    """
    def getRemainingTimeSeconds():
        pass#TODO
    
    def getElapsedTimeSeconds():
        pass#TODO
    
    """
    Evaluate whether lights are ON or OFF
    """
    def isLightsOn():
        pass#TODO
    
    """
    Get raw measurement of current light level
    """
    def getLightLevel():
        pass#TODO
    
    """
    If the lights are turned OFF shorly after starting the game, then exit cuurent and subsequent chapters, effectively triggering a soft reboot
    """
    def isGameRunning():
        pass#TODO