

# Cyber Attack on OT-PLC-Railway System

#### Introduction 

This project will demo two kinds of cyber attack situation on the OT-PLC-Railway system. (The introduction of OT-PLC-Railway system was shown in the main project readme file)

- **Black Out Attack** : This is one attack situation of Black Energy 3 cyber attack. When the attack happens, all the PLC output coils(energy output) will be turn off. The system HMI center energy may detect the exception situation and the user can not recover to normal situation by using the SCADA PC. ( The SCADA HMI shows every thing normal when the user do recover action but actually all the PLC related output still keep turned off)
- **False Data Injection Attack** : When the attack happens, the reversed user control commend will be injected into the system and the exception situation is not detectable from the SCADA HMI system. (When the user try to turn on the Runway lights in the airport, all the lights will be turn off.)

![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/attackCtrlWeb.png)

###### Steps to Implement The Attack Demo : 

1. Connect the attack device (A Raspberry PI with the attack server program) to the OT-PLC-Railway network system by a CAT-5 cable. 

2. Attack situation I : Attacker can use a remote attack control panel to turn off all the PLC output coils without detectable by the train supervisory control and data acquisition (SCADA) system. 

3. Attack situation II : When a normal user open a MS-Word document, a document edit enable message box will pop up. If the confirm button was clicked, the attack server will turn off all the PLC output coils. 

4. Attack situation III : when a normal user click the "PLC detail menu" hyper-link in a MS-Word document the attack start. 

5. Attack situation IV: Connected the attack PC to the system from internet/local Ethernet. Start the attack from the attack control Web interface.

   

###### Program File Deployment For The Demo : 

To run the demo, please deploy the programs by following below diagram: 

![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/fileDeploy.png)

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
| attckBlackE3.py         | python2.7/python3 | This module will be called from the macro in doc "operation manual.docm" to simulation the black out attack on the OT-PLC-platform. |
| attackhost.py           | python2.7/python3 | This module is used to create a http server on port 8080 to handle the attack get request. |
| attackServ.py           | python2.7/python3 | This module will create a attack service program to run the Ettercap false data injection attack. |
| controlPanel.py         | python2.7/python3 | This module will create attack control panel to start and stop the man in the middle attack. |
| M2PLC221.py             | python2.7/python3 | This module is used to connect the Schneider M2xx PLC.       |
| S7PLC1200.py            | python3           | This module is used to connect the siemens s7-1200 PLC       |
| m221_1 filter/m221_1.ef | C                 | This filter is used do reverse all the PLC communication command between HMI and the PLC1. ( 192.168.10.21<=> 192.168.10.72) |
| m221_3 filter/m221_2.ef | C                 | This filter is used to do block all the PLC feedback data to the HMI computer.(192.168.10.21) |
| operation manual.docm   | MS word/VBA       | MS-Word document with Macro to active the attack.            |
| attackWeb/attackHost.py | python3           | flask server to create a attack control web for the people who does the presentation. |

* Programs deployment is shown in the Introduction section <Program file deployment for the demo>  . 

------

#### Program Design 

The program design followed below diagram:

![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/attack.png)

> The communication between client and server computer is using UDP.

Ettercap filter network sniffing algorithm:

![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/mimAttack.png)

------

#### Program Usage/ Demo Implement

> All the program has to mode: test mode and demo mode. The demo is used to do the demo on the real PLC-Railway System and under test mode all the programs can run on one computer without do any setting or connect to any hardware.
>
> To active test mode set the test flag TEST_MODE = True  # Test mode flag - True: test on local computer

1. ###### Setup Attack Device

   - Set the IP address and copy the file base on the section "Program file deployment for the demo".

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

2. ######  Start/Stop Black Out Attack From Attack Control Panel

   - Make should the client computer is also connected in the OT-PLC-Railway system and its IP address is set to same subnet(192.168.10.XXX), run/double click the **controlPanel.py** : 

     ![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/controlPanel.png)

   - Click the "**Connect Serv**" button to test the server connection, the text field will show "**C;1**" to identify the server response server connection successful.

   - Click the "**Active attack**" button to start the attack, the server will response "**A;1**" when it started the attack. Click the "**Stop attack**" button and the when sever response "**A;0**" the attack will be stopped.

3. ###### Start Black Out Attack From the MS-Word Document's Macro

   - Open the word document and press "Alt+F11" to edit the macro execution path. Replace the attackBlackE3.py path in the follow line which shown in the VBA editor:

     ```
     Shell "cmd /c C:\Python27\python.exe C:\Users\dcslyc\Documents\attackBlackE3.py " & sDir, vbNormalFocus
     ```

     > If there is a space in the path need to put "" at the front and end of the path, for example : 
     >
     > Shell "cmd /c C:\Python27\python.exe ""C:\Users\Liu Yuancheng\Documents\attackBlackE3.py"" " & sDir, vbNormalFocus

   - Run the **attackhost.py** on the client computer with the word document.

   - Double click the MS-Word **operation manual.docm** : when the document is opened, an editing enable message box will be show. Click the "**OK**" button. 

     ![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/macro1.png)

     The scan command window will pop-up and show the computer scan information. 

     ![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/scan1.png)

     An executable file will be created with the same folder of the MS-Word document as shown below. Then the attack will be start automatically. 

     ![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/exeFile.png)

     > If the file was put in the  'Desktop', the file may not be created as the "exe" file creation permission is not high enough.

4. ###### Start Black Out Attack From the Document's Hyper-link

   - Run the **attackhost.py** on the client computer with the word/PDF document.

   - Click the hyper-link and the attack will be start when the bowser pop-up and shows "405 file not found error".

     ![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/link.png)


 5. ###### Start/Stop Black Out Attack/ False Data Injection Attack From Web Control Panel

    - Run the attackHost.py in the attackWeb folder:

      ```
      python attackHost.py
      ```

    - Type in url http://127.0.0.1:5000/ (local)  http://xxx.xxx.xx.xx:5000/ (remote) or in the browser. the web will show: 

      ![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/attack/remoteAtk/doc/attackCtrlWeb.png)

    - Press the "Start/Stop attack" button in the first line to active/de-active Black Out attack. 

    - Press the "Start/Stop attack" button in the second line to active/de-active the False Data Injection Attack.

      

------

> Last edit by LiuYuancheng(liu_yuan_cheng@hotmail.com) at 07/01/2020



