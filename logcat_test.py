import subprocess

base_adb_command = ['adb']
adb_command = base_adb_command[:]
# print (adb_command)
adb_command.append('logcat')
adb_command.extend(['-d'])
# print (adb_command)
pid = "com.happylabs.hps"
adb = subprocess.Popen(adb_command, stdout=subprocess.PIPE)
adb2 = subprocess.Popen(['grep','amazonaws'], stdin=adb.stdout ,stdout=subprocess.PIPE)
adb3 = subprocess.Popen(['grep',pid], stdin=adb2.stdout ,stdout=subprocess.PIPE)
for line in adb3.stdout.readlines():
    print (line)

