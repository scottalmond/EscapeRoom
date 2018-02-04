#open the server first.  Server and client can be run on the same computer
#HOST is the ip address of the server

#python3 test16_socket.py SERVER
#python3 test16_socket.py CLIENT

#determined by calling: sudo ifconfig
#and referring to the wlan0 entry
#https://learn.adafruit.com/adafruits-raspberry-pi-lesson-3-network-setup/finding-your-pis-ip-address

#get IP address of other devices in network
#nmap -sP 192.168.1.0/24
#get IP address of other RPI's (requires root)
#sudo nmap -sP 192.168.1.0/24 | awk '/^Nmap/{ip=$NF}/B8:27:EB/{print ip}'


from time import sleep
import socket
import sys

HOST = '192.168.1.116'
PORT = 7070

def main(is_server):
	print('START')
	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	print('socket created')
	try:
		if(is_server):
			s.bind((HOST,PORT))
		else:
			s.connect((HOST,PORT))
	except ConnectionRefusedError as msg:
		print('Connection refused: ' + str(msg))
		sys.exit()
	except socket.error as msg:
		print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
		sys.exit()
		 
	print('Socket bind complete')
	
	if(is_server):
		#Start listening on socket
		s.listen(10)
		print('Socket now listening')
	 
		#now keep talking with the client
		for rep in range(1):
			#wait to accept a connection - blocking call
			conn, addr = s.accept()
			print('Connected with ' + addr[0] + ':' + str(addr[1]))
			
			while(True):
				data=conn.recv(1024).decode()
				if(not data):
					break
				print("from client: "+str(data))
				data=str(data).upper()
				print('sending: '+data)
				conn.send(data.encode())
			conn.close()
	else: #client
		message=""
		while(not message=='q'):
			message=input(' INPUT: ')
			s.send(message.encode())
			data=s.recv(1024).decode()
			print('Recevied from server: '+str(data))
	
	print('Closing...')
	s.close()
	print('DONE')

if __name__ == "__main__":
	args=sys.argv
	is_server=False #else is_client
	if("SERVER" in args):
		is_server=True
		args.remove("SERVER")
	main(is_server)
