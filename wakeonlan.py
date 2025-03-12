#!/usr/bin/env python3
import socket, selectors
import struct
import signal
import sys
import argparse
import logging, logging.handlers
import threading
import traceback
from pathlib import Path


PROGRAM_VERSION="1.2.0";
PROGRAM_NAME="WakeonLanProxy";
USE_LOCAL_WORKINGDIR=True;
USE_LOG_FILE=True;
USE_CONFIG_FILE=True;

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
        logging.info(f"Escuchando en {port}");
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
                    logging.info(f"Data from {dfrom} for MAC:{DestMAC}");
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
        logging.info("Enviando apagado...presione ctrl+c de nuevo para salir inmediatamente");
        if(self.running):
            self.running=False;
        else:
            sys.exit(0);


#static main section
def ThreadOneFuncToRulethemAll(args):
    trace = "".join(traceback.extract_tb(args.exc_traceback).format());
    logging.error(trace);
    logging.error(args.exc_value);

def OneFuncToRulethemAll(*args):
    trace = "".join(traceback.extract_tb(args[2]).format());
    logging.error(trace);
    logging.error(args);

def main():
    threading.excepthook=ThreadOneFuncToRulethemAll;
    sys.excepthook=OneFuncToRulethemAll;
    parser = argparse.ArgumentParser(prog="Wake on LAN proxy",
    description="Reenvia los Magic packet que viene de afuera hacia la red local");
    parser.add_argument("port",metavar="Puerto de escucha",help="Puerto donde se recibiran los magic packets",type=int);
    parser.add_argument("bcastaddr",metavar="direccion de broadcast",help="Direccion de broadcast de la red para el paquete",type=str);
    parser.add_argument("logdir",metavar="Ruta del Archivo de Log",help="Ruta donde se escribirá el log",type=str);
    try:
        args = parser.parse_args();
    except SystemExit:
        return;
    filelog = Path(args.logdir);
    filelog = filelog / Path(F"{PROGRAM_NAME}.log");
    LogHandlers = [];
    LogHandlers.append(logging.StreamHandler());
    LogHandlers.append(logging.handlers.RotatingFileHandler(filelog,maxBytes=1024*1024*64,backupCount=4));
    logging.basicConfig(format='%(asctime)s | %(levelname)s | %(message)s',
                        level=logging.INFO,
                        handlers=LogHandlers
                        );
    logging.info(f"Iniciando WOL proxy by Gsus V{PROGRAM_VERSION}");
    logging.info(F"Los parametros fueron: {args}");
    p=Program();
    signal.signal(signal.SIGINT,p.exit);
    p.SocketListener(args.port, args.bcastaddr);

if __name__=="__main__":
    main();