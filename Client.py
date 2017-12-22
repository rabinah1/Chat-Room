import socket, sys, select
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from builtins import int, str
import time

class Chat_room(QWidget): # Class for the user interface of the program.
	def __init__(self):
		super().__init__()
		self.serverip = sys.argv[1]
		if (":" in self.serverip): # If the IP-address contains ":", we create an IPv6-socket.
			self.clientsocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			self.port = 9005
		else: # If the IP-address does not contain ":", we create an IPv4-socket.
			self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.port = 9009
		self.clientsocket.settimeout(2) # Set the timeout to be 2 seconds.
		self.nick = input("Please enter your nickname: ") # Ask the user to enter nickname.
		self.clientsocket.connect((self.serverip, self.port)) # Connect to server.
		self.nick = self.nick.encode()
		self.WRITEABLE = []
		self.ERROR = []
		self.initUI() # We call the function initUI(), that initializes the user interface.
	
	def initUI(self): # We use this method to initalize the UI.
		# On the lines 29-40 we create textboxes etc. In addition, we define settings such that there are two text fields side-by-side in the UI and below is a field
		# to which the user writes a message to be send to the server.
		vbox = QVBoxLayout(self)
		hbox = QHBoxLayout()
		self.edit = QTextEdit() # The leftmost window of the UI.
		self.edit_2 = QTextEdit() # The rightmost window of the UI.
		self.edit.setReadOnly(True)
		self.edit_2.setReadOnly(True)
		self.text_box = QLineEdit(self) # The field to which the user writes messages.
		vbox.addLayout(hbox)
		hbox.addWidget(self.edit)
		hbox.addWidget(self.edit_2)
		vbox.addWidget(self.text_box)
		self.setGeometry(150, 150, 700, 700)
		
		self.show() # Show the UI on the screen.
		self.clientsocket.sendall(self.nick) # Send the nickname of the user to the server.
		self.nick = self.nick.decode("ascii")
		
	def keyPressEvent(self, e): # This method recognises when the user presses enter to send a message.
		if e.key() == Qt.Key_Return: # If the user presses enter.
			self.Print(self.text_box.text()) # Call method self.Print()
			
	def Print(self, message): # This method sends the message written by the user to the server.
		self.text_box.clear()  # Clear the textbox to which the user writes messages.
		self.message = message
		self.message = "<" + self.nick + "> " + self.message # Add the nickname of the user in front of the message in the form "<nickname>".
		try: # Try to send the message to server.
			self.clientsocket.sendall(self.message.encode())
		except BrokenPipeError: # If there was an error sending the message, we let the user know.
			self.edit.append("Not connected to server.")
	
	def ClearAll(self): # This method clears the righmost part of the window (which contains information about the users that are online).
		self.edit_2.setReadOnly(False)
		self.edit_2.clear()
		self.edit_2.setReadOnly(True)
	
	def Append(self, data, const): # This method prints the messages received from ther server to the UI.
		# The variable const defines whether the received data is printed to the leftmost or rightmost part of the UI.
		if const == 0:
			self.edit.append(data) # Print to the left part.
		elif const == 1:
			self.edit_2.append(data) # Print to the right part.
	
	def Server_failure(self): # We call this method if the connection to the server is lost.
		self.edit.append("Lost connection to server, trying to reconnect...") # Let the user know about this situation.
		Thread_2.start() # We start a thread that tries to reconnect every two seconds.
		
	def Reconnect(self): # This method tries to reconnect to the server if the connection was lost.
		self.i = 0
		self.clientsocket.close() # Close the socket.
		if (":" in self.serverip):
			self.clientsocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM) # Create a new IPv6 socket.
		else:
			self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a new IPv4 socket.
		self.clientsocket.settimeout(2)
		try: # Try to make connection with the server. If a connection was established, we set the variable i to 1 to inform about this.
			chat.clientsocket.connect((chat.serverip, chat.port))
			self.i = 1
		except ConnectionRefusedError:
			pass
		except ConnectionAbortedError:
			pass
		if self.i == 1: # If we managed to get re-establish the connection.
			self.edit.append("Connection to the server established!") # Let the user know about the reconnection.
			self.nick = self.nick.encode()
			self.clientsocket.sendall(self.nick) # The client sends the nickname again to the server, because it is the first data that the server expects to receive.
			self.nick = self.nick.decode("ascii")
			Thread_1.start() # Initiate a thread that reads the messages coming from the server.
			Thread_2.terminate() # Terminate the thread that tries to reconnect to the server.
			
	def closeEvent(self, event): # This method recognises, when the user quits the program.
		data = "USEREXIT()" + self.nick
		data = data.encode()
		self.clientsocket.sendall(data) # Send a code "USEREXIT()" and the nickname of the user to the server, so that the server can remove the corresponding client.
		event.accept()
		
app = QApplication(sys.argv)
chat = Chat_room()

class ReadSocket(QThread): # Thread that receives the messages coming from the server.
	# pyqtSignal() is a function that can be used to send commands to the methods of the "main program".
	sig = pyqtSignal()
	sig_2 = pyqtSignal(str, int)
	sig_3 = pyqtSignal()
	def __init__(self):
		QThread.__init__(self)
		# Connect the created signals to the methods of the main program that will be commanded by these signals.
		self.sig.connect(chat.ClearAll)
		self.sig_2.connect(chat.Append)
		self.sig_3.connect(chat.Server_failure)
	def run(self): # This method receives and handles the messages that are received from the server.
		while True:
			self.READABLE = [sys.stdin, chat.clientsocket]
			self.ready_to_read, self.ready_to_write, self.in_error = select.select(self.READABLE, chat.WRITEABLE, chat.ERROR)
			for sock in self.ready_to_read:
				if sock == chat.clientsocket: # If there is an incoming message from the server.
					data = sock.recv(4096) # Store the received message to variable "data".
					data = data.decode("ascii")
					if data == "A": # If the content of the message was letter "A".
						self.sig.emit() # We call function ClearAll that clears the rightmost window of the UI. This is done because letter "A" tells the next we will receive
                                                # updated information about online-users.
						self.const = 1
					elif data == "B": # If the content of the message was letter "B".
						self.const = 0
					elif data == "": # The server starts to send very much empty, if the server crasher or is shut down. In this case we call method Server_failure.
						self.sig_3.emit()
						self.terminate() # Now also this thread is terminated becuase we do not want to receive more empty messages from the server.
					else: # If we receive a normal message from the server.
						if self.const == 0:
							self.sig_2.emit(data, self.const)
						elif self.const == 1:
							self.sig_2.emit(data, self.const)

class ServerError(QThread): # A thread that is initiated if the connection to server is lost and we want to try to reconnect to the server.
	sig = pyqtSignal()
	def __init__(self):
		QThread.__init__(self)
		self.const = 0
		self.sig.connect(chat.Reconnect)
	def run(self):
		while True: # We call method Reconnect every two seconds. This method tries to re-establish a connection to the server.
			self.sig.emit()
			time.sleep(2)


Thread_1 = ReadSocket()
Thread_2 = ServerError()
Thread_1.start()
app.exec()
