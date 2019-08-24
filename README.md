# DelayAttackDemo
DelayAttackDemo is a very simple Python script which use sockets to send precalculated 
DNP3 packets over TCP and allows you to choose the number of packets to send and the length of delay. 
It's use is designed for demo purposes.

There are two kinds of Delay Attack (illustrated in the "Delay Attack Demo.pptx").
- First one is simply Delay Attack, it just change the time interval between two packet.
And it is easily been detected by the Bro (now its name has been changed to [Zeek](https://www.zeek.org/), the Bro script is 
in /zeek/detect.zeek)

- Second one is a little bit complicated. It not only delay the next packet, but also 
fulfill the gap using previous packets, so the whole trace looks like normal. This one is much harder
detect by the Bro.


### How to use

- Change the ipdst in Config, which is the destination machine's IP.
- Send the packets:
 ```
 python DelayAttackDemo.py
 ```
- Use Bro to monitor the destination machine:
```buildoutcfg
# Replace /usr/lock/bro/bin/zeek with the path of your zeek bin
# Replace enp0s25 with the network interface on your machine
sudo /usr/lock/bro/bin/zeek -i enp0s25 detect.zeek
```

