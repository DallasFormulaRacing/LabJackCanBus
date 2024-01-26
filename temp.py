"""
Demonstrates how to control lua script execution with an LJM host app

Relevant Documentation:

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    Single Value Functions (like eReadName):
        https://labjack.com/support/software/api/ljm/function-reference/single-value-functions
    Multiple Value Functions(such as eReadNameByteArray):
        https://labjack.com/support/software/api/ljm/function-reference/multiple-value-functions

T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    User-RAM:
        https://labjack.com/support/datasheets/t-series/lua-scripting#user-ram

Note:
    Our Python interfaces throw exceptions when there are any issues with
    device communications that need addressed. Many of our examples will
    terminate immediately when an exception is thrown. The onus is on the API
    user to address the cause of any exceptions thrown, and add exception
    handling when appropriate. We create our own exception classes that are
    derived from the built-in Python Exception class and can be caught as such.
    For more information, see the implementation in our source code and the
    Python standard documentation.
"""
from labjack import ljm
from time import sleep

def loadLuaScript(handle, luaScript):
    """Function that loads and begins running a lua script

    """
    try:
        scriptLen = len(luaScript)
        # LUA_RUN must be written to twice to disable any running scripts.
        print("Script length: %u\n" % scriptLen)
        ljm.eWriteName(handle, "LUA_RUN", 0)
        # Then, wait for the Lua VM to shut down. Some T7 firmware
        # versions need a longer time to shut down than others.
        sleep(0.6)
        ljm.eWriteName(handle, "LUA_RUN", 0)
        ljm.eWriteName(handle, "LUA_SOURCE_SIZE", scriptLen)
        ljm.eWriteNameByteArray(handle, "LUA_SOURCE_WRITE", scriptLen, luaScript)
        ljm.eWriteName(handle, "LUA_DEBUG_ENABLE", 1)
        ljm.eWriteName(handle, "LUA_DEBUG_ENABLE_DEFAULT", 1)
        ljm.eWriteName(handle, "LUA_RUN", 1)
    except ljm.LJMError:
        print("Error while loading the lua script")
        raise

def readLuaInfo(handle):
    """Function that selects the current lua execution block and prints
       out associated info from lua

    """
    try:
        for i in range(20):
            # The script sets the interval length with LJ.IntervalConfig.
            # Note that LJ.IntervalConfig has some jitter and that this program's
            # interval (set by sleep) will have some minor drift from
            # LJ.IntervalConfig.
            sleep(1)
            print("LUA_RUN: %d" % ljm.eReadName(handle, "LUA_RUN"))
            # Add custom logic to control the Lua execution block
            executionLoopNum = i % 3
            # Write which lua control block to run using the user ram register
            ljm.eWriteName(handle, "USER_RAM0_U16", executionLoopNum)
            numBytes = ljm.eReadName(handle, "LUA_DEBUG_NUM_BYTES")
            if (int(numBytes) == 0):
                continue
            print("LUA_DEBUG_NUM_BYTES: %d\n" % numBytes)
            aBytes = ljm.eReadNameByteArray(handle, "LUA_DEBUG_DATA", int(numBytes))
            luaMessage = "".join([("%c" % val) for val in aBytes])
            print("LUA_DEBUG_DATA: %s" % luaMessage)
    except ljm.LJMError:
        print("Error while running the main loop")
        raise


def main():
    try:
        luaScript = """
--[[
    Name: accelerometer-lsm303dlhc.lua
    Desc: This is an example that uses the LSM303DLHC Accelerometer on the I2C
          Bus on EIO4(SCL) and EIO5(SDA)
    Note: I2C examples assume power is provided by a LJTick-LVDigitalIO at 3.3V
          (a DAC set to 3.3V or a DIO line could also be used for power)
--]]

--Outputs data to Registers:
--X = 46006
--Y = 46008
--Z = 46010

local SLAVE_ADDRESS = 0x19

-------------------------------------------------------------------------------
--  Desc: Returns a number adjusted using the conversion factor
--        Use 1 if not desired
-------------------------------------------------------------------------------
local function convert_16_bit(msb, lsb, conv)
  res = 0
  if msb >= 128 then
    res = (-0x7FFF+((msb-128)*256+lsb))/conv
  else
    res = (msb*256+lsb)/conv
  end
  return res
end


-- Configure the I2C Bus
I2C.config(1, 0, 65516, 0, SLAVE_ADDRESS, 0)
local addrs = I2C.search(0, 127)
local addrslen = table.getn(addrs)
local found = 0
-- Make sure the device slave address is found
for i=1, addrslen do
  if addrs[i] == SLAVE_ADDRESS then
    print("I2C Slave Detected")
    found = 1
    break
  end
end
if found == 0 then
  print("No I2C Slave detected, program stopping")
  MB.writeName("LUA_RUN", 0)
end
--Data Rate: 10Hz, disable low-power, enable all axes
I2C.write({0x20, 0x27})
-- Continuous update, LSB at lower addr, +- 2g, Hi-Res disable
I2C.write({0x23, 0x49})
-- Configure a 500ms interval
LJ.IntervalConfig(0, 500)
while true do
  -- If an interval is done
  if LJ.CheckInterval(0) then
    local rawacceldata = {}
    -- Sequentially read the addresses containing the accel data
    for i=0, 5 do
      I2C.write({0x28+i})
      local indata = I2C.read(2)
      table.insert(rawacceldata, indata[1])
    end
    local acceldata = {}
    -- Convert the data into Gs
    for i=0, 2 do
      table.insert(acceldata, convert_16_bit(rawacceldata[1+i*2], rawacceldata[2+i*2], (0x7FFF/2)))
    end
    -- Add accelX value, in Gs, to the user_ram register
    MB.writeName("USER_RAM3_F32", acceldata[1])
    -- Add accelY
    MB.writeName("USER_RAM4_F32", acceldata[2])
    -- Add accelZ
    MB.writeName("USER_RAM5_F32", acceldata[3])
    print("X: "..acceldata[1])
    print("Y: "..acceldata[2])
    print("Z: "..acceldata[3])
    print("------")
  end
end
                    \0"""
        # Open first found LabJack
        handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier
        #handle = ljm.openS("T8", "ANY", "ANY")  # T8 device, Any connection, Any identifier
        #handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier
        #handle = ljm.openS("T4", "ANY", "ANY")  # T4 device, Any connection, Any identifier
        #handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")  # Any device, Any connection, Any identifier

        info = ljm.getHandleInfo(handle)
        print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
              "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
              (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

        loadLuaScript(handle, luaScript)
        print("LUA_RUN %d" % ljm.eReadName(handle, "LUA_RUN"))
        print("LUA_DEBUG_NUM_BYTES: %d" % ljm.eReadName(handle, "LUA_DEBUG_NUM_BYTES"))
        readLuaInfo(handle)
        # Close handle
        ljm.close(handle)
    except ljm.LJMError:
        ljm.eWriteName(handle, "LUA_RUN", 0)
        # Close handle
        ljm.close(handle)
        raise
    except Exception:
        ljm.eWriteName(handle, "LUA_RUN", 0)
        # Close handle
        ljm.close(handle)
        raise

if __name__ == "__main__":
    main()