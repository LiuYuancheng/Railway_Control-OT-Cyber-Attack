# Railway_PLC_Control
#### Introduction

##### This project will create a 2 trains HMI system for the user to simulation different railway operation. The system use Schneider M221 and siemens s7 1200 to control the hardware. The program can also simulate 3 kind of cyber attack for the railway system. 

![](https://github.com/LiuYuancheng/RailWay_PLC_Control/blob/master/doc/readme0.png)

------

###### Function Tab Introduction

| The program provide 2 function tab to display system operation information and let user control/simulation different function |
| ------------------------------------------------------------ |
| Tab Idx0 System: Control the different components in the rail way system and 2 trains. |
| Tab Idx1 PLC Control:  Show the PLC information and user can turn on/off PLC coils from this tab. |
| Tab Idx2 Data Display: Show the PLC Memory /register status or overwrite PLC data. |
| Tab Setting: Change the system setting and start different cyber attack simulation. |

###### PLC output connection map table:

\# PLC 0 [schneider M221]: 

\#   M0  -> Q0.0 Airport LED

\#   M10 -> Q0.1 Power Plant

\#   M60 -> Q0.2 Industrial LED

\# PLC 1 [seimens S7-1200]

\#   Qx0.0-> Q0.0 station + sensor

\#   Qx0.1-> Q0.1 level crossing pwr

\#   Qx0.2-> Q0.2 Resident LED

\# PLC 2 [schneider M221]:

\#   M0  -> Q0.0 fork turnout

\#   M10 -> Q0.1 track A pwr

\#   M20 -> Q0.2 track B pwr

\#   M60 -> Q0.3 city LED

