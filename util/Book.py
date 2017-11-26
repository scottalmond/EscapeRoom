"""
Class used to execute a series of Chapters
Coordinates preparation, execution and disposal of Chapters
"""

TYPE_DEBUG=0
TYPE_MAIN=1
TYPE_AUX=2

class Book:
    def __init__(self,book_type,environment):
        self.my_book_type=book_type
        self.my_environment=environment
    
    """
    Acquire resources needed to run the chapters
    """
    def init(self):
        pass
    
    """
    Step through all chapters in the book once
    """
    def run(self):
        print("Book: HERE")
        
    """
    Release resources that all chapters hold
    """
    def dispose():
        pass
        