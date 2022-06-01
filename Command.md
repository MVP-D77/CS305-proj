## Command

```c
./netsim.py servers start -s servers/2servers

./netsim.py servers start -s servers/5servers

python netsim.py onelink start
python netsim.py onelink run -e topology/onelink/onelink.events -l netsim_log

python netsim.py twolink start
python netsim.py twolink run -e topology/twolink/twolink.events -l netsim_log

python netsim.py sharelink start
python netsim.py sharelink run -e topology/sharelink/sharelink.events -l netsim_log

python proxy1_framework.py --listen_port 6600 --log ../logs/log1.txt
  
python proxy1_framework.py --listen_port 7700 --log ../logs/log2.txt

python dns.py ../docker_setup/netsim/topology/onelink/onelink 5000
```

