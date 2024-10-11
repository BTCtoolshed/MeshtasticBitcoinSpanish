import subprocess
from pubsub import pub
import serial
import time
import datetime

#Lora
import meshtastic
import meshtastic.serial_interface

MANUALBTCTR = ""
MANUALBTCTRANS = ""
GUARDAR="i"

#----------------------------------------------------------- RADIO MESHTASTIC -------------------------------------------
def onReceive(packet, interface): # called when a packet arrives
	global STRRCB
	global AUTOR
	global RECIPIENTE
	global CANAL
	global MANUALBTCTRANS
	global MANUALBTCTR
	global datainput2
	global GUARDAR
	CANAL= i
	#print(packet)
	try:
		STRRCB = str(packet['decoded']['portnum'])
		if STRRCB == "TEXT_MESSAGE_APP":
			STRRCB = str(packet['decoded']['text'])
			AUTOR = str(packet['from'])
			RECIPIENTE = str(packet['to'])
			if 'channel' in packet:
					CANAL = str(packet['channel'])
			if RECIPIENTE == "xxxxx" and CANAL != "0":                  #-------------------------CAMBIA XXXXX AL NUMERO DEL "NODE", SON TODOS NUMEROS, NINGUN LETRA
				interface.sendText("recibido",destinationId=int(AUTOR))

				if "*" not in STRRCB and STRRCB != "I" and STRRCB != "R" and STRRCB != "E" and STRRCB != "borra":
					interface.sendText("Red de Bitcoin\n[I]nstrucciones\n[R]evisa Mempool\n[E]mpieza Transmision",destinationId=int(AUTOR))
				
				if STRRCB == "I":
					interface.sendText("1) Ubiquese cerca del radio, envia unos mensajes largos.\n2) Revisa Mempool para la taza para calcular el costo de la transaccion.",destinationId=int(AUTOR))
					time.sleep(1)
					interface.sendText('''3) Utilice una billetera Bitcoin, tal como BlueWallet o Bitcoin Core, para crear un "raw transaction".''',destinationId=int(AUTOR))
					time.sleep(1)
					interface.sendText("4) Dividir la transaccion en su orden & en grupos de un maximo de 100-200 caracteres cada uno.",destinationId=int(AUTOR))
					time.sleep(1)
					interface.sendText('''5) Envia los groups en orden, con un * al final de cada grupo. Espera una confirmacion con una cuenta del total de caracteres para cada grupo, o string. Envia la palabra "borra" para reiniciar el proceso.''',destinationId=int(AUTOR))
					time.sleep(1)
					interface.sendText("6) Para el ultimo grupo, agriega ** al final del ultimo grupo de caracteres. Complira la transaccion. Cuando se envia al red de BTC, recibira una confirmacion.",destinationId=int(AUTOR))
					time.sleep(1)
				
				if STRRCB == "M":
					MEMPOOL = subprocess.getoutput("curl -sSL \"https://mempool.space/api/v1/fees/recommended\"")
					MEMjson = json.loads(MEMPOOL)
					MEMCHECK = str(MEMjson['halfHourFee'])+" Sats/vByte"
					interface.sendText(MEMCHECK,destinationId=int(AUTOR))
				
				if STRRCB == "S":
					GUARDAR = AUTOR
					interface.sendText("Inicie su transacccion, agriegando al final de cada grupo un *, ** al final del ultimo grupo.",destinationId=int(AUTOR))
				
				if "**" in STRRCB and GUARDAR == AUTOR:
					interface.sendText("Cumplido!",destinationId=int(AUTOR))
					STRRCB = STRRCB.replace("*","")
					MANUALBTCTRANS += STRRCB
					MANUALBTCTR = MANUALBTCTRANS
					if len(MANUALBTCTR) > 0:
						try:
							interface.sendText("Cuenta:"+str(len(MANUALBTCTR)),destinationId=int(AUTOR))
						except Exception:
							time.sleep(0.1)
							
				if "*" in STRRCB and GUARDAR == AUTOR:
					interface.sendText("continue...",destinationId=int(AUTOR))
					STRRCB = STRRCB.replace("*","")
					MANUALBTCTRANS += STRRCB
					if len(MANUALBTCTRANS) > 0:
						try:
							interface.sendText("Cuenta:"+str(len(MANUALBTCTRANS)),destinationId=int(AUTOR))
						except Exception:
							time.sleep(0.1)
							
					
				if STRRCB == "borra":
					GUARDAR = i
					BTCBROAD = ""
					BTCSEND = ""
					MANUALBTCTR = ""
					MANUALBTCTRANS = ""
					interface.sendText("Reinicie!",destinationId=int(AUTOR))
				
	except Exception:
		time.sleep(0.1)

def onConnection(interface, topic=pub.AUTO_TOPIC): # called when we (re)connect to the radio
	#defaults to broadcast, specify a destination ID if you wish
	#interface.sendText("Inicializacion de BTC!",channelIndex=0)                                       #----------- PUEDES CAMBIAR EL CANAL, CAMBIANDO EL channelIndex
	time.sleep(0.1)



#############################
#TRY LORA RADIO CONNECTION
try:
	pub.subscribe(onReceive, "meshtastic.receive.text")
	pub.subscribe(onConnection, "meshtastic.connection.established")
	interface = meshtastic.serial_interface.SerialInterface(devPath='/dev/ttyUSB0')                    #------------ By default will try to find a meshtastic device, otherwise provide a device path like /dev/ttyUSB0

except Exception as e:
	print(e)

	
################################################# ESPERA LA INFORMACION DEL RADIO #####################################            
while True:
	if len(MANUALBTCTR) > 20:
		BTCSEND = "/usr/local/bin/bitcoin-cli sendrawtransaction "+MANUALBTCTR
		interface.sendText("Intentando Enviar La Transaccion de Bitcoin...",destinationId=int(GUARDAR))
		try:
			BTCBROAD = subprocess.getoutput(BTCSEND)
			if len(BTCBROAD) > 0:
				SENDTHIS = BTCBROAD.strip()
				if len(SENDTHIS) > 200:
					interfact.sendText(SENDTHIS[0:199],destinationId=int(GUARDAR))
				else:
					interface.sendText(SENDTHIS,destinationId=int(GUARDAR))
				BTCBROAD = ""
				BTCSEND = ""
				MANUALBTCTR = ""
				MANUALBTCTRANS = ""
		except Exception:
			BTCBROAD = ""
			BTCSEND = ""
			MANUALBTCTR = ""
			MANUALBTCTRANS = ""
	time.sleep(0.25)
		


