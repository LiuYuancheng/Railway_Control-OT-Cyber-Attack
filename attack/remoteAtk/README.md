# Remote Black Energy 3 Attack 
#### Introduction 

This project will be used to demo the "Black Energy 3" attack on the OT-PLC-Railway system. When the attack happens all the PLC output coils will be turn off but the HMI center will show every thing normal.

Attack implement steps: 

1. Attack plug in the attack device in the OT-PLC-Railway system.(Raspberry PI which with the attack server program)

2. Attack situation 1: Attacker use the remote attack control panel to turn off all the PLC output coils. 
3. Attack situation 2: when the user open a MS word document, a update message box pop up, if the update confirm button was clicked, the attack server will turn off all the PLC output coils. 
4. Attack situation 3: when the user click the "PLC detail menu" hyper-link in the word word document the attack start. 

------

#### Program Setup

###### Development Evn: Python 2.7 & python 3.7

###### Additional Lib/Software Need:

1. snap7 + python-snap7 (need to install for S71200 PLC control) 

   ```
   Install instruction: 
   http://simplyautomationized.blogspot.com/2014/12/raspberry-pi-getting-data-from-s7-1200.html
   ```

2. ettercap-graphical (need to install on Raspberry PI to do the attack)

   ```
   sudo apt-get update -y
   sudo apt-get install -y ettercap-graphical
   ```

   

###### Hardware Needed: 

Raspberry PI Mode 3 B+ with ettercap installed and IP set: 

```
ifconfig eth0 192.168.10.244 netmask 255.255.255.0 up
```



