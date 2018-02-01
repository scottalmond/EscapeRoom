import socket
#determined by calling: sudo ifconfig
#and referring to the wlan0 entry
#https://learn.adafruit.com/adafruits-raspberry-pi-lesson-3-network-setup/finding-your-pis-ip-address
HOST=

def main()




if __name__ == "__main__":
	args=sys.argv
	is_master=False
	if("MASTER" in args):
		is_master=True
		args.remove("MASTER")
	
