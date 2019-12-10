# Remote Black Energy 3 Attack 
#### Introduction 

This project will be used to demo the "Black Energy 3" attack on the OT-PLC-Railway system. When the attack happens all the PLC output coils will be turn off but the system HMI center will show every thing normal.

Steps to implement the attack: 

1. Connect the attack device (A Raspberry PI which with the attack server program) to the OT-PLC-Railway system by a CAT-5 cable. 

2. Attack situation 1: Attacker can use a remote attack control panel to turn off all the PLC output coils. 
3. Attack situation 2: When a normal user open a MS word document, a document edit eable message box will pop up, if the confirm button was clicked, the attack server will turn off all the PLC output coils. 
4. Attack situation 3: when a normal user click the "PLC detail menu" hyper-link in a MS-Word document the attack start. 

------

#### Program Setup

###### Development Environment: Python 2.7 & python 3.7

###### Additional Lib/Software Need:

1. snap7 + python-snap7 (need to install for S71200 PLC control) 

   ```
   Install instruction: 
   http://simplyautomationized.blogspot.com/2014/12/raspberry-pi-getting-data-from-s7-1200.html
   ```

2. Ettercap-graphical (need to install on Raspberry PI to do the attack)

   ```
   $ sudo apt-get update -y
   $ sudo apt-get install -y ettercap-graphical
   ```

###### Hardware Needed: 

Raspberry PI Mode 3 B+ with Ettercap installed and IP set: 

```
$ ifconfig eth0 192.168.10.244 netmask 255.255.255.0 up
```

###### Program File List:

| Program file          | Execution env     | Description                                                  |
| --------------------- | ----------------- | ------------------------------------------------------------ |
| attckBlackE3.py       | python2.7/python3 | This module will be called from the macro in doc "operation manual.docm"to simulation the black energy 3 attack on the OT-platform. |
| attackHost.py         | python2.7/python3 | This module is used to create a http server on port 8080 to handle the get request. |
| attackServ.py         | python2.7/python3 | This module will create a attack service program to run the Ettercap false data injection attack. |
| controlPanel.py       | python2.7/python3 | This module will create attack control panel to start and stop the man in the middle attack. |
| M2PLC221.py           | python2.7/python3 | This module is used to connect the Schneider M2xx PLC.       |
| S7PLC1200.py          | python3           | This module is used to connect the siemens s7-1200 PLC       |
| m221_3 filter         | C                 | This filter is used to do block all the PLC feedback data to the HMI computer.(192.168.10.21) |
| operation manual.docm | MS word/VBA       | Word document with Macro to active the attack.               |

------

#### Program Design 

The program design is followed below diagram:

![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/attack.png)

Ettercap filter network sniffing algorithm:

![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/mimAttack.png)

------

#### Program Usage

1. ###### Setup attack device

   - Install Ettercap in Raspberry PI and compile the filter to executable file for the Ettercap : 

     ```
     $ etterfilter m221_3.filter -o m221_3.ef
     ```

   - Plug the Raspberry Pi in the OT-RailWay-PLC system and setup the IP address:

     ```
     $ sudo ifconfig eth0 192.168.10.244 netmask 255.255.255.0 up
     ```

   - Copy the file **m221_3.ef** and **attackServ.py** in to the same folder and run the attack server:

     ```
     $ python attackServ.py
     ```

2. ######  Start/stop attack from control pane

   - Make should the client computer is also connected in the OT-PLC-Railway system, run/double click the **controlPanel.py** : 

     ![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/controlPanel.png)

   - Click the "**Connect Serv**" button to test the server connection, the text field will show "**C;1**" to identify the server response server connection successful.

   - Click the "**Active attack**" button to start the attack, the server will response "**A;1**" when it start attack. Click the "**Stop attack**" button and the when sever response "**A;0**" the attack will be stopped.

3. ###### Start attack from the MS-Word document macro

   - Run the attack host on the client computer with the word document.

   - Double click the **operation manual.docm**, when the document is opened, an editing enable message box will be show. Click the "**OK**" button.

     ![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/macro1.png)

     The scan cmd window will pop-up and show the computer scan information.

     ![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/scan1.png)

     An executable file will be created with the same folder of the MS-Word document. (If the file was put in the 'Desktop', the file may not be created as the file creation permission is not high enough ) 

     ![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/exeFile.png)

     Then the attack will be start automatically. 

4. ###### Start the attack from the document's hyper-link

   - Run the attack host on the client computer with the word document.

   - Click the hyper-link and the attack will be start when the bowser pop-up and shows "405 file not found error".

     ![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/link.png)

   

​	







