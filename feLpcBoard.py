"""                                                                                            Python frontend for controlling UVic light pulser card                                         """

import midas
import midas.frontend
import midas.event
import collections
import ctypes
import os
import subprocess
from time import time
import shlex

import serial
import time



class MyPeriodicEquipment(midas.frontend.EquipmentBase):

    def __init__(self, client):
        # The name of our equipment. This name will be used on the midas status
        # page, and our info will appear in /Equipment/MyPeriodicEquipment in
        # the ODB.
        equip_name = "LPC_Board"
        
        # Define the "common" settings of a frontend. These will appear in
        # /Equipment/MyPeriodicEquipment/Common. The values you set here are
        # only used the very first time this frontend/equipment runs; after 
        # that the ODB settings are used.
        default_common = midas.frontend.InitialEquipmentCommon()
        default_common.equip_type = midas.EQ_PERIODIC
        default_common.buffer_name = "SYSTEM"
        default_common.trigger_mask = 0
        default_common.event_id = 1
        default_common.period_ms = 3000
        default_common.read_when = midas.RO_ALWAYS
        default_common.log_history = 1

        self.numPorts = 8

        # Create the settings directory.  
        default_settings = collections.OrderedDict([  
            ("external_trigger", True),
            ("internal_trigger_rate", False ),
            ("enable_led", 0),
            ("led_bias", 1023), # set to slowest LED pulse by default
        ])                                                                             
        
        # You MUST call midas.frontend.EquipmentBase.__init__ in your equipment's __init__ method!
        midas.frontend.EquipmentBase.__init__(self, client, equip_name, default_common, default_settings)

        # Initalize connection to serial port
        self.ser = serial.Serial('/dev/ttyUSB0', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1)  # open serial port       
        if self.ser.name == '/dev/ttyUSB0':
            print("Successfully connected to serial port " + self.ser.name)         # check which port was really used 
        else:
            print("Unsuccessfully connected to serial port; response =  " + self.ser.name)
            
        # By default I think we should enable the board and set it to external trigger

        cmd="E\n"
        self.ser.write(cmd.encode())
        line = self.ser.readline()
        line = self.ser.readline()
        if line != b'\n' and line != b'\r\n' :
            print("LPC board is enabled: " +str(line[:12]))

        # Set to external trigger
        cmd="TE\n"
        self.ser.write(cmd.encode())

        line = self.ser.readline()
        line = self.ser.readline()
        if line != b'\n' and line != b'\r\n' :
            print("Set to use external trigger: "+str(line[:28]))

        # Set to slow external trigger rate
        cmd="RS\n"
        self.ser.write(cmd.encode())

        line = self.ser.readline()
        line = self.ser.readline()
        if line != b'\n' and line != b'\r\n' :
            print("Set to slow rate for internal trigger: "+str(line))

        # Setup callback on LED bias
        self.client.odb_watch(self.odb_settings_dir + "/led_bias", self.led_bias_callback)

        # Setup callback on LED enables
        self.client.odb_watch(self.odb_settings_dir + "/enable_led", self.led_enable_callback)

        # Setup callback on external trigger
        self.client.odb_watch(self.odb_settings_dir + "/external_trigger", self.external_trigger_callback)


        # You can set the status of the equipment (appears in the midas status page)
        self.set_status("Initialized")

        
        
    def readout_func(self):
        
        event = midas.event.Event()

        # Read the status of the LPC ADC bias
        data = []
        adc_value = 0
        #data.append(adc_value)
        cmd="Q"
        self.ser.write(cmd.encode())

        line = self.ser.readline()
        if line != b'\n' and line != b'\r\n' :
            print(line)
        line = self.ser.readline()
        if line != b'\n' and line != b'\r\n' :
            #print(line)
            #print(line[12:16])
            data.append(int(line[12:16]))
        print("read LED bias ADC"  + str(data))
        event.create_bank("LPNK", midas.TID_INT, data)



        return event

 
    def led_bias_callback(self,client, path, odb_value):
        print("New ODB content at %s is %s" % (path, odb_value))
        
        # Set the DAC value
        # DAC value must be in range 0-1023
        if odb_value < 0 or odb_value > 1023:
            self.client.msg("Invalid DAC value (must be 0-1023); value= "+str(odb_value))
        else:            
            cmd="S"+str(odb_value).zfill(4)
            print(cmd)
            self.ser.write(cmd.encode())
            
            time.sleep(5)
            line = self.ser.readline()
            line = self.ser.readline()
            if line != b'\n' and line != b'\r\n' :
                print(line)
                self.client.msg("LED bias DAC set to " +str(odb_value))
            else:
                self.client.msg("ADC set failed?")


    def led_enable_callback(self,client, path, odb_value):
        print("New ODB content at %s is %s" % (path, odb_value))
        
        # Set the DAC value
        # DAC value must be in range 0-7
        if odb_value < 0 or odb_value > 7:
            self.client.msg("LED must be 0-7 (0 is disable); value= "+str(odb_value))
        else:            
            cmd="L"+str(odb_value)
            print(cmd)
            self.ser.write(cmd.encode())
            
            time.sleep(5)
            line = self.ser.readline()
            line = self.ser.readline()
            if line != b'\n' and line != b'\r\n' :
                print(line)
                if odb_value == 0:
                    self.client.msg("LED triggering disabled")
                else:
                    self.client.msg("LED" +str(odb_value)+" has been enabled")
            else:

                self.client.msg("LED enable set failed?")

    def external_trigger_callback(self,client, path, odb_value):
        print("New ODB content at %s is %s" % (path, odb_value))
        
        cmd="TE"
        if odb_value == True : 
            cmd="TE"
        else:
            cmd="TI"


        
        print(cmd)
        self.ser.write(cmd.encode())
            
        time.sleep(5)
        line = self.ser.readline()
        line = self.ser.readline()
        if line != b'\n' and line != b'\r\n' :
            print(line)
            if odb_value == True:
                self.client.msg("External trigger enabled")
            else:
                self.client.msg("Internal trigger enabled")


class MyFrontend(midas.frontend.FrontendBase):
    """
    """
    def __init__(self):
        # You must call __init__ from the base class.
        midas.frontend.FrontendBase.__init__(self, "feLpcBoard")
        
        # You can add equipment at any time before you call `run()`, but doing
        # it in __init__() seems logical.
        self.add_equipment(MyPeriodicEquipment(self.client))

    def begin_of_run(self, run_number):
        self.set_all_equipment_status("Running", "greenLight")
        self.client.msg("Frontend has seen start of run number %d" % run_number)
        return midas.status_codes["SUCCESS"]
        
    def end_of_run(self, run_number):
        self.set_all_equipment_status("Finished", "greenLight")
        self.client.msg("Frontend has seen end of run number %d" % run_number)
        return midas.status_codes["SUCCESS"]
        
if __name__ == "__main__":


    # The main executable is very simple - just create the frontend object,
    # and call run() on it.
    my_fe = MyFrontend()
    my_fe.run()
