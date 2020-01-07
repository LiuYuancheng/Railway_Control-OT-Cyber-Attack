# Cyber Attack on OT-PLC-Railway System

#### Introduction 

This project will demo two kinds of cyber attack situation on the OT-PLC-Railway system. (The introduction of OT-PLC-Railway system was shown in the main project readme file)

- **Black Out Attack** : This is one attack situation of Black Energy 3 cyber attack. When the attack happens, all the PLC output coils(energy output) will be turn off. The system HMI center energy may detect the exception situation and the user can not recover to normal situation by using the SCADA PC. ( The SCADA HMI shows every thing normal when the user do recover action but actually all the PLC related output still keep turned off)
- **False Data Injection Attack** : When the attack happens, the reversed user control commend will be injected into the system and the exception situation is not detectable from the SCADA HMI system. (When the user try to turn on the Runway lights in the airport, all the lights will be turn off.)

###### Steps to implement the attack demo: 

1. Connect the attack device (A Raspberry PI with the attack server program) to the OT-PLC-Railway network system by a CAT-5 cable. 

2. Attack situation I : Attacker can use a remote attack control panel to turn off all the PLC output coils without detectable by the train supervisory control and data acquisition (SCADA) system. 

3. Attack situation II : When a normal user open a MS-Word document, a document edit enable message box will pop up. If the confirm button was clicked, the attack server will turn off all the PLC output coils. 

4. Attack situation III : when a normal user click the "PLC detail menu" hyper-link in a MS-Word document the attack start. 

5. Attack situation IV: Connected the attack PC to the system from internet/local Ethernet. Start the attack from the attack control Web interface.

   

------

#### Program Setup

###### Development Environment: Python 2.7 & python 3.7 + HTML5

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
   
3. Flask (need to install on the attakerPC to show the attack control web)

   ```
   pip install Flask
   ```

###### Hardware Needed: 

Raspberry PI Mode 3 B+ with Ettercap installed and IP set: 

```
$ ifconfig eth0 192.168.10.244 netmask 255.255.255.0 up
```

###### Program File List:

| Program File            | Execution Env     | Description                                                  |
| ----------------------- | ----------------- | :----------------------------------------------------------- |
| attckBlackE3.py         | python2.7/python3 | This module will be called from the macro in doc "operation manual.docm"to simulation the black out attack on the OT-PLC-platform. |
| attackhost.py           | python2.7/python3 | This module is used to create a http server on port 8080 to handle the attack get request. |
| attackServ.py           | python2.7/python3 | This module will create a attack service program to run the Ettercap false data injection attack. |
| controlPanel.py         | python2.7/python3 | This module will create attack control panel to start and stop the man in the middle attack. |
| M2PLC221.py             | python2.7/python3 | This module is used to connect the Schneider M2xx PLC.       |
| S7PLC1200.py            | python3           | This module is used to connect the siemens s7-1200 PLC       |
| m221_3 filter           | C                 | This filter is used to do block all the PLC feedback data to the HMI computer.(192.168.10.21) |
| operation manual.docm   | MS word/VBA       | MS-Word document with Macro to active the attack.            |
| attackWeb/attackHost.py | python3           | flask server to                                              |

------

#### Program Design 

The program design followed below diagram:

![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/attack.png)

> The communication between client and server computer is using UDP.

Ettercap filter network sniffing algorithm:

![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/mimAttack.png)

------

#### Program Usage

1. ###### Setup attack device

   - Install Ettercap in Raspberry PI and compile the filter to executable file for the Ettercap : 

     ```
     $ etterfilter m221_3.filter -o m221_3.ef
     ```

   - Plug the Raspberry Pi in the OT-PLC-Railway system and setup the IP address:

     ```
     $ sudo ifconfig eth0 192.168.10.244 netmask 255.255.255.0 up
     ```

   - Copy the file **m221_3.ef** and **attackServ.py** in to the same folder and run the attack server:

     ```
     $ python attackServ.py
     ```

2. ######  Start/stop attack from attack control panel

   - Make should the client computer is also connected in the OT-PLC-Railway system and its IP address is set to same subnet(192.168.10.XXX), run/double click the **controlPanel.py** : 

     ![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/controlPanel.png)

   - Click the "**Connect Serv**" button to test the server connection, the text field will show "**C;1**" to identify the server response server connection successful.

   - Click the "**Active attack**" button to start the attack, the server will response "**A;1**" when it start attack. Click the "**Stop attack**" button and the when sever response "**A;0**" the attack will be stopped.

3. ###### Start attack from the MS-Word document macro

   - Run the attack host on the client computer with the word document.

   - Double click the MS-Word **operation manual.docm** : when the document is opened, an editing enable message box will be show. Click the "**OK**" button.

     ![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/macro1.png)

     The scan cmd window will pop-up and show the computer scan information.

     ![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/scan1.png)

     An executable file will be created with the same folder of the MS-Word document as shown below. Then the attack will be start automatically. 

     ![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/exeFile.png)

     > If the file was put in the 'Desktop', the file may not be created as the "exe" file creation permission is not high enough.

4. ###### Start the attack from the document's hyper-link

   - Run the attack host on the client computer with the word/PDF document.

   - Click the hyper-link and the attack will be start when the bowser pop-up and shows "405 file not found error".

     ![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/link.png)

   

​	

------

> Last edit by LiuYuancheng(liu_yuan_cheng@hotmail.com) at 12/12/2019



