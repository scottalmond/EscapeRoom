"""
Main

This class is responsible for initializing a thread and running the escape room operations within that thread
Encapsulating all processes within a thread allows for asyncronous debugging operations

To kickoff, run:
Main().start()
"""

import time
import threading

class Main(threading.Thread):
	
	"""
	Extends Thread
	"""
	def run(self):
		self.__init()
		self.__main()
		self.__dispose()
	
	"""
	Create Environment and Book
	"""
	def __init(self,environment_type=1,book_type=1):
		self.my_environment=Environment(environment_type)
		self.my_environment.init()
		self.my_book=Book(self.my_environment,book_type)
		self.my_book.init()
	
	"""
	Loop execution here until ready to exit
	"""
	def __main(self):
		while(not self.__isStopped()):
			print("Main: HERE")
			self.my_book.run()
			time.sleep(3.0)
	
	"""
	Close references to open environmental variables
	Do so in reverse order from init()
	"""
	def __dispose(self):
		self.my_book.dispose()
		self.my_environment.dispose()
	
	"""
	check if environment has been stopped
	"""		
	def __isStopped():
		return self.my_environment.isStopped()
		
