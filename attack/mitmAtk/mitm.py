import socket
import subprocess
import signal
import os
import sys
import time


# attack id for mitm is 01
# ----------------------
# request type
# 01 - stop the attack
# 02 - start the attack
# 03 - get state
# ------------------------
# request id is the number of the request
# ---------------------------

# response
#  01 - got stop command
#  02 - got start command
#  03 - Idle
#  04 - Working
#  05 - Active
#  06  - Stopping


UDP_PORT = 54321
UDP_IP_ADDRESS = "172.18.212.85"
SYSLOG_SERVER = "172.18.212.85"
IP_LISTENER = "172.18.212.234"

# mitm_command = r'/home/pi/mitm/attack.sh >> logs'
mitm_command_1 = r'/home/pi/mitm/attack_1.sh'
mitm_command_2 = r'/home/pi/mitm/attack_2.sh'
mitm_path = r'/home/pi/mitm/'



class attack:
	def __init__(self):
		self.listener()
		self.syslog_lst = []
		if 'logs' in os.listdir(mitm_path):
			os.rename(mitm_path + 'logs', mitm_path + 'logs_' + str(time.time()).split('.')[0])
		with open(mitm_path + 'logs', 'wb')	as f:
		 	f.write('Train Station Attack ')


	def listener(self):
		# open the socket between the server and client

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((IP_LISTENER, UDP_PORT))
		
		self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
		self.writeSyslog('open listen port on ' + IP_LISTENER + ':' + str(UDP_PORT))
		
	
	def writeSyslog(self, msg):
		with open(mitm_path + 'logs', 'ab') as f:
			f.write('\n' + time.strftime("%Y-%m-%d %H:%M:%S: ") + msg + '\n')


	def sendSyslog(self):
		with open(mitm_path + 'logs', 'rb') as f:
			self.syslog_lst = f.readlines()


		sock_syslog = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		for log in self.syslog_lst:
			sock_syslog.sendto(str(log), (SYSLOG_SERVER, 514))
		sock_syslog.close()

	def getDataREquest(self):
		# extract the data from arrived packet
		data, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
		self.writeSyslog('Got requests from ' + str(addr) + ' data: ' + data.encode('hex'))
		# self.writeSyslog('request data is: ' + data.encode('hex'))
		return data, addr

	def createRespone(self, requestsID, attackID, responseType):
		msg = requestsID + attackID + responseType
		return msg

	def sendResponse(self, msg):
		# send the wanted response 
		# self.sock.sendto(msg.decode('hex'), (UDP_IP_ADDRESS, UDP_PORT))
		self.writeSyslog('Send ' + msg + ' respone to ' + UDP_IP_ADDRESS)
		self.sock2.sendto(msg.decode('hex'), (UDP_IP_ADDRESS, UDP_PORT))

	def analizeRequest(self, data):
		request = data.encode('hex')
		# print request, len(request), type(request)
		requestsID = request[0:2] # just an ID to be synchronized request-response
		attackID = request[2:4] # to know wich attack should answer the request
		requestType = request[4:6] # what the request is
		return requestsID, attackID, requestType

	def getState(self, pstring): # need to be added
		# verify what the state of the attack is
		self.writeSyslog('Got get attack state request: ' + pstring)
		ps_counter = os.popen("ps ax | grep " + pstring + " | grep -v grep")
		for line in ps_counter:
			fields = line.split()
			# print fields
			# print pstring
			if pstring in fields:
				return '05'	# active
		return '03' # idle


	def startAttack(self): # need to be added
		# start the attack
		self.writeSyslog('got start MITM attack request')
		f = open(mitm_path + 'turnOff', 'ab')
		# p = subprocess.Popen(mitm_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		p2 = subprocess.Popen(mitm_command_2, shell=True, stdout=subprocess.PIPE, stderr=f)
		time.sleep(4)
		self.sendState('03', '01')
		p1 = subprocess.Popen(mitm_command_1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		time.sleep(4)
		self.stopAttack("s7_2.ef")
		return p1


	def stopAttack(self, pstring): # need to be added
		# stop the attack
		self.writeSyslog('Got stop attack request: ' + pstring)
		counter = 0
		for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):
			fields = line.split()
			# print fields
			pid = fields[0]
			os.kill(int(pid), signal.SIGKILL)
			counter += 1
			self.writeSyslog('stopped attack')

		return counter

	def sendState(self, requestsID, attackID):
		state = self.getState('ettercap')
		res_msg = self.createRespone(requestsID, attackID, state)
		self.sendResponse(res_msg)



if __name__ == '__main__':

	attackID = '01'
	requestsID = '02'
	requestType = '02'
	state = '03'

	attacker = attack()

	try:
		
		while True:
			
			print
			data = attacker.getDataREquest()
			requestsID, attackID, requestType = attacker.analizeRequest(data[0])
			if attackID == '01' and requestType == '01': # stop
				attacker.stopAttack('ettercap')

			if attackID == '01' and requestType == '02': # start
				attacker.startAttack()

			if attackID == '01' and requestType == '03': # get state
				attacker.sendState(requestsID, attackID)
				# state = attacker.getState('ettercap')
				# res_msg = attacker.createRespone(requestsID, attackID, state)
				# attacker.sendResponse(res_msg)
			
			if attackID == '01' and requestType == '04': # send syslog messages
			 	attacker.sendSyslog()
			

	except Exception, e:
		print e
		attacker.sock.close()
		attacker.sock2.close()
		sys.exit()
