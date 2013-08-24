""" A console client, donated by fancyzero, would be emoved later for it does not work well."""
import sys
import os
import time
import socket
import json
import string
mapw = 40
maph = 40
snakeskin=["*","$","#","%","~"]

mapdata=""
def tick():
    global s
    global mapdata
    #send command
    command = '{"action":"new_snake"}\r\n'
    s.send(command)
    #read socket
    while(True):
        mapdata = mapdata + s.recv(10)
        #see if we got a correct snapshot of map
        index = string.find(mapdata,"\r\n")
        if index >= 0:
            print index
            map_snap = mapdata[0:index]
            mapdata = mapdata[index+2:]
            break

    #initial map grids
    map_view = []
    for i in range(mapw*maph):
        map_view.append(" ")

    #parse map snap
    parsed_map = json.loads(map_snap)
    for food in parsed_map["map"]:
        pos = eval('[' + food + ']')
        map_view[pos[0]+pos[1]*mapw]="O"

    for key in parsed_map["snakes"]:
        bodys = parsed_map["snakes"][key]
        for body in bodys:
            pos = eval('[' + body + ']')
            map_view[pos[0]+pos[1]*mapw]="*"

    #clear screen
    os.system('cls' if os.name=='nt' else 'clear')

    #draw map view
    for i in range(mapw):
        for j in range(maph):
           sys.stdout.write(map_view[i+j*mapw])
        sys.stdout.write("\r\n")

def main():
    global s
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if len(sys.argv) > 2:
        server_addr = sys.argv[1]
        server_port = sys.argv[2]
    else:
        server_addr = "localhost"
        server_port = 10080

    s.connect( (server_addr, int(server_port)))
    print "connected to:", server_addr, server_port
    while(True):
        time.sleep(0.5)
        tick()

main()
