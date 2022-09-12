import smbclient
from fabric import Connection


# env.hosts = ['jetson@192.168.3.2']
# env.passwords = {'jetson'}
from reefscanner.basic_model.samba.file_ops_factory import get_file_ops

smbclient.ClientConfig(username='jetson', password='jetson')
a = smbclient._os.stat_volume(r"\\192.168.3.2\images")
print (a)

conn = Connection(
    "jetson@192.168.3.2",
    connect_kwargs={"password": "jetson"}
)
b = conn.run("ls")

camera_os = get_file_ops(True)

dir = '\\\\192.168.3.2\\images/20220225_015741_Seq02'

a = camera_os.listdir(dir)
print(a)