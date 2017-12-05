"""
Class used to execute a series of Chapters
Coordinates preparation, execution and disposal of Chapters
"""

TYPE_DEBUG=0 #for development testing
TYPE_MAIN=1 #for running operationally on main monitor
TYPE_AUX=2 #for running operationally on auxilary monitor
TYPE_IO=3 #for testing IO response

class Book:
    """
    Create chapters for the specified book type
    """
    def __init__(self,environment,book_type):
        self.my_environment=environment
        self.chapter_list=[]
        if(book_type==self.TYPE_DEBUG):
            chapter_list.append(Hyperspace(environment))
        elif(book_type==self.TYPE_MAIN):
            pass#TODO
        elif(book_type==self.TYPE_AUX):
            pass#TODO
        elif(book_type==self.TYPE_IO):
            chapter_list.append(IO_Test(environment))
        else:
            raise ValueError("Undefined Book type: "+str(book_type))
    
    """
    Acquire resources needed to run the chapters
    Chapters initialized in FIFO order
    """
    def init(self):
        for chapter in self.chapter_list:
            chapter.init()
    
    """
    Step through all chapters in the book once
    """
    def run(self):
        for chapter in self.chapter_list:
            chapter_frame=0
            while(not chapter.isComplete() and not self.isStopped()):
                chapter.step(chapter_frame)#ie, draw one frame from this chapter
                chapter_frame+=1
        print("Book: HERE")
        
    """
    Release resources that all chapters hold
    Chapters disposed in LIFO order for symmetry with init()
    """
    def dispose():
        for chapter in reversed(self.chapter_list):
            chapter.dispose()
    
    def isStopped():
        return self.my_environment.isStopped()
        