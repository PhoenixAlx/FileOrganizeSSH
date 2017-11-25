#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  fileorganizessh.py
#  
#  Copyright 2017 FM Alex Bueno @PhoenixAlx
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import paramiko
import json
import os
import time

def read_configuration(name_file="config.json"):
    '''read parameters from configuration file'''
    conf={}
    with open(name_file) as json_file:  
        conf = json.load(json_file)
    return conf
def send_messages_bot(conf,text):
    ''' send messages to bot telegram'''
    URL="https://api.telegram.org/bot"+conf["tg_api"]+"/sendMessage"
    tg_chats_ids=conf["tg_chats_ids"].split(",");
    for CHAT_ID in tg_chats_ids:
        tg_command='curl -s -d'+' "chat_id='+CHAT_ID+'&disable_web_page_preview=1&text='+text+'" '+URL+' > /dev/null';
        print(tg_command)
        os.system(tg_command);
    return True
def download_files(conf):
   '''download series via ssh''' 
   path_files=conf['path_remote'];
   ssh_client= paramiko.SSHClient()
   ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
   ssh_client.connect(hostname=conf['host_remote'],username=conf['user_remote'],password=conf['password_remote'])
   ftp_client=ssh_client.open_sftp()
   stdin,stdout,stderr=ssh_client.exec_command('ls '+path_files)
   files_in_folder=ftp_client.listdir(path=path_files)
   if (len(files_in_folder)>0):
       #copy file in folders local
       text='%s files found, i am going to download'%(len(files_in_folder));
       send_messages_bot(conf,text);
       for f in files_in_folder:
           #send message save files
           text='file %s downloading'%(f);
           send_messages_bot(conf,text);
           #get labels for files in conf
           labels=conf['labels'];
           labels_folders=labels.keys();
           path_file_remote=path_files+"/"+f;
           #check all ok labels in file name
           file_saved=False;
           for lf in labels_folders:
               labes_in_folder=labels[lf].split(",");
               total_ok=0;
               folder_local="";
               for l in labes_in_folder:
                   if (l.lower() in f.lower()):
                       total_ok=total_ok+1;
               if (total_ok==len(labes_in_folder) and not file_saved):
                   #save file in folder
                   folder_local=conf['path_local']+"/"+lf;
                   if not os.path.exists(folder_local):
                       os.makedirs(folder_local)
               
                   path_file_local=folder_local+"/"+f;
                   ftp_client.get(path_file_remote,path_file_local);
                   #send message file save
                   text='file %s saved in %s'%(f,path_file_local);
                   send_messages_bot(conf,text);
                   #remove remote file
                   ftp_client.remove(path_file_remote);
                   #send message file remove
                   text='file %s removed of %s'%(f,path_file_remote);
                   send_messages_bot(conf,text);
                   file_saved=True;
           if not file_saved:
               #copy in unknowfolder
               folder_local=conf['path_local_unknown'];
               text=' New type of files  %s '%(f);
               send_messages_bot(conf,text);
               if not os.path.exists(folder_local):
                       os.makedirs(folder_local)
               
               path_file_local=folder_local+"/"+f;
               ftp_client.get(path_file_remote,path_file_local);
               #send message file save
               text='file %s saved in %s'%(f,path_file_local);
               send_messages_bot(conf,text);
               #remove remote file
               ftp_client.remove(path_file_remote);
               #send message file remove
               text='file %s removed of %s'%(f,path_file_remote);
               send_messages_bot(conf,text);
               file_saved=True;
                                  
               
 
                
                    
            
       text='%s files downloaded'%(len(files_in_folder));
       send_messages_bot(conf,text);
   ftp_client.close()
   return True;
def tests():
    conf=read_configuration(name_file="config.json");
    if (conf=={}):
        print ("error configuration");
    else:
        print ("configuration ok");
    
def main():
    conf=read_configuration(name_file="config.json");
    text='Start watch files in %s '%(conf["path_remote"]);
    send_messages_bot(conf,text);
    no_error=True;
    count_error=0;
    while (no_error):
        if count_error<conf['limit_errors']:
            try:
                download_files(conf);
            except:
                text="upps!!!. Something is wrong downloading files. I am going to wait %s seconds and i will try again."%(str(conf['time_sleep']));
                send_messages_bot(conf,text);
                count_error=count_error+1;
            time.sleep(conf['time_sleep']);
        else:
            text="so many errors.";
            send_messages_bot(conf,text);
            no_error=False;
        conf=read_configuration(name_file="config.json");
       
main();
