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

### Dependence
Python Version: Python 2.7

For GUI demo: Tkinter

### Bro Demo
- Before start the demo, please make sure that the bro(zeek) has been installed in the destination machine
- Please kindly find the installation guide from https://docs.zeek.org/en/current/install/install.html


- Start the DNP3 server in the destination machine
```buildoutcfg
sudo python3 server.py
```

- Use Bro to monitor the destination machine:
Bro script store  in /zeek/detect.zeek
```buildoutcfg
# Replace /usr/local/bro/bin/zeek with the path of your zeek bin
# Replace enp0s25 with the network interface on your machine
sudo /usr/local/bro/bin/zeek -i enp0s25 detect.zeek
```

- Change the ipdst in Config, which is the destination machine's IP.
- Send the packets through command line:
 ```
 python gui_bro.py
 ```
 
 ### Machine Learning Demo
 ```buildoutcfg
 python gui_ML.py
```

--ml_data 
 |_ data.csv (ML data for delay from 1-50)
 |_ delay0.csv (ML data without delay)
 |_ RNN_Attention (ML model)
 |_ scalar_x.pkl (Preprocessing model)
 |_ scalar_y.pkl (Preprocessing model)
 




