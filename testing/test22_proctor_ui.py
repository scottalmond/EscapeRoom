import tkinter as tk
import time
import threading

#def nextChapter():
	#print("Next Chapter")
	
#def resetRoom():
	#print("Reset")
	
#def onClosing():
	#print("Closing...")
	#top.destroy()

#BUTTON_HEIGHT_PX=27

#top=Tk()
#top.title("Proctor")

#nextChapterButton=Button(top,text="Next Chapter",command=nextChapter)
#resetButton=Button(top,text="Reset",command=resetRoom)
#status=StringVar()

#nextChapterButton.place(x=0,y=0*BUTTON_HEIGHT_PX)
#resetButton.place(x=0,y=1*BUTTON_HEIGHT_PX)

#top.geometry("400x300")
#top.protocol("WM_DELETE_WINDOW",onClosing)
#top.mainloop()

#https://stackoverflow.com/questions/459083/how-do-you-run-your-own-code-alongside-tkinters-event-loop
#threading

class GUI(threading.Thread):
	BUTTON_HEIGHT_PX=27
	
	def __init__(self):
		threading.Thread.__init__(self)

	def nextChapter():
		print("Next Chapter")
	
	def resetRoom():
		print("Reset")

	def closing(self):
		print("Closing...")
		self.root.quit() #vs destroy()

	def run(self):
		self.root = tk.Tk()
		self.root.title("Proctor")
		self.root.protocol("WM_DELETE_WINDOW", self.closing)
		
		nextChapterButton=tk.Button(self.root,text="Next Chapter",command=self.nextChapter)
		resetButton=tk.Button(self.root,text="Reset",command=self.resetRoom)
		status=tk.StringVar()
		
		nextChapterButton.pack()
		resetButton.pack()

		label = tk.Label(self.root, textvariable=status)
		label.pack()
		
		status.set("new text")
		
		self.root.geometry("400x300")
		self.root.mainloop()

GUI().start()
