from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import OVSSwitch
from mininet.cli import CLI
import subprocess

class Topo(Topo):

    def build(self):

        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        s1 = self.addSwitch('s1', cls=OVSSwitch)
        self.addLink(h1, s1)
        self.addLink(s1, h2)

topo = Topo()
net = Mininet(topo, controller=None)
net.start()

h1 = net.get('h1')
h2 = net.get('h2')

# Inicia el servidor en h1 como un proceso separado
server_process = subprocess.Popen(['python3', 'web_server_lab1.py'], cwd='/media/dayi/SD ALMACEN/Lab 1 RC/')

result = h2.cmd('curl http://10.0.0.1:8086/page1.html')
print(result)

CLI(net)
net.stop()