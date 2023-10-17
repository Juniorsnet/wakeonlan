#!/usr/bin/env python3
import socket, selectors
import struct
import signal
import sys
import argparse

class Program:
    sel = selectors.DefaultSelector();
    running = True;
    StringMagicPacket = "!6s"+16*"6s";
    def SocketListener(self, port: int, bcast: str):
        MagicPacketStruct = struct.Struct(self.StringMagicPacket);
        addr = ("",port);
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
        s.setblocking(False);
        ret = s.bind(addr);
        SelKey = self.sel.register(s,selectors.EVENT_READ,data=None);
        print(f"Escuchando en {port}");
        while (self.running):
            #readers, _, _ = select.select([s],[],[],5);
            readers = self.sel.select(timeout=5);
            if(len(readers)>0):
                #Get the socket
                key,mask = readers[0];
                msg = key.fileobj.recvfrom(256);#los magic packets deberían ser de 102 bytes.
            else:
                continue;
            data = msg[0];
            dfrom = msg[1];
            if(MagicPacketStruct.size==len(data)):
                Macs = MagicPacketStruct.unpack(data);
                header = Macs[0].hex(":");
                if(header=="ff:ff:ff:ff:ff:ff"):
                    DestMAC = Macs[1].hex(":");
                    print(f"Data from {dfrom} for MAC:{DestMAC}");
                    self.SendWol(Macs[1],bcast);
        s.close();
    
    def SendWol(self, lunaMacAddress: bytes, bcast: str):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        magic = b'\xff' * 6 + lunaMacAddress * 16
        #daddr = ('<broadcast>', 9);
        daddr = (bcast, 9);
        s.sendto(magic, daddr);#data, (host,port)
        s.close();

    def exit(self,sig,frame):
        print("Enviando apagado...presione ctrl+c de nuevo para salir inmediatamente");
        if(self.running):
            self.running=False;
        else:
            sys.exit(0);

#static main
def main():
    print(f"Iniciando WOL proxy by Gsus V1.2");
    parser = argparse.ArgumentParser(prog="Wake on LAN proxy",
    description="Reenvia los Magic packet que viene de afuera hacia la red local");
    parser.add_argument("port",metavar="Puerto de escucha",help="Puerto donde se recibiran los magic packets",type=int);
    parser.add_argument("bcastaddr",metavar="direccion de broadcast",help="Direccion de broadcast de la red para el paquete",type=str);
    try:
        args = parser.parse_args();
    except SystemExit:
        return;
    p=Program();
    signal.signal(signal.SIGINT,p.exit);
    p.SocketListener(args.port, args.bcastaddr);

if __name__=="__main__":
    main();