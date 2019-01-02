from boa.interop.Neo.Storage import Get, Put, Delete, GetContext
from boa.interop.Neo.Runtime import Notify
from boa.interop.Neo.Action import RegisterAction
from boa.interop.Neo.Header import GetHash,GetTimestamp
from boa.interop.Neo.Transaction import GetReferences,GetOutputs
from boa.interop.Neo.TriggerType import Application, Verification
from boa.interop.System.ExecutionEngine import GetScriptContainer, GetExecutingScriptHash
from boa.interop.Neo.Blockchain import GetHeight, GetHeader
from boa.interop.Neo.Runtime import GetTrigger, CheckWitness
from boa.interop.Neo.Output import GetScriptHash, GetValue, GetAssetId
from boa.builtins import concat, list, range, take, substr

SERIALIZED_NAME = 'LUCKYNEO'

GAS_ASSET_ID = b'\xe7-(iy\xeel\xb1\xb7\xe6]\xfd\xdf\xb2\xe3\x84\x10\x0b\x8d\x14\x8ewX\xdeB\xe4\x16\x8bqy,`'
OWNER = b''
TWOWEEKS = 1209600000

OnWinner = RegisterAction('onWinner', 'to', 'amount', 'scripthash')
OnRefund = RegisterAction('refund', 'to', 'amount')


def Main(operation):

    print('entered main, getting trigger')
    trigger = GetTrigger()
    print('got trigger')
    print(trigger)

     # current bug with Verification()
    if trigger == b'\x00':

        print("doing verification!")
        owner_len = len(OWNER)
        print('owner len has been found')
        if owner_len == 20:
            print('checking witness')
            res = CheckWitness(OWNER)
            print("owner verify result")
            print(res)
            return res

    # current bug with Verification()
    elif trigger == b'\x10':
        print('doing application')
        if operation == 'deploy':
            print("Deploying contract")
            deploy = Deploy()
            return deploy
        elif operation == 'getTotal':
            print("Getting Time!")
            total = GetTotal()
            return total
        elif operation == 'timeLeft':
            print("Getting time left")
            time = TimeLeft()
            return time
        elif operation == 'getEntries':
            print('Getting Entries')
            entries = GetEntries()
            return entries
        elif operation == 'pickWinner':
            print('Picking a winner')
            winner = PickWinner()
            return winner
        else:
            print('simulating gas transaction')
            entry = AddEntry()
            return entry


def PickWinner():
    tx = GetScriptContainer()
    context = GetContext()
    references = GetReferences(tx)
    if _TimeHasExpired():
        winningEntry = _getWinner()
        schash = GetExecutingScriptHash()
        entries = GetEntries()
        numEntries = len(entries)
        luckycut = numEntries - 30
        OnWinner(winningEntry, luckycut, schash)
        SetTime()
        Put(context, "entries", 0)
    else:
        print("contest isn't over yet!")

def _getWinner():
    entries = GetEntries()
    numEntries = len(entries)
    print("Number of entries:")
    print(numEntries)
    if numEntries == 0:
        return 0
    currentHeight = GetHeight()
    currentHeader = GetHeader(currentHeight)
    currentHash = GetHash(currentHeader)
    winningIndex = currentHash % numEntries
    winningEntry = entries[winningIndex]
    return winningEntry

def Deploy():
    print('checking if its the owner')
    isowner = CheckWitness(OWNER)
    if True:
        print('it is the owner')
        time = SetTime()
        return time
    else:
        print('you are not the owner')
    return 0

def GetTotal():
    context = GetContext()
    out = Get(context, 'entries')
    return out

def TimeLeft():
    context = GetContext()
    time = Get(context, 'endTime')
    Notify(time)
    return time

def GetEntries():
    context = GetContext()
    entries = Get(context, 'entries')
    Notify(entries)
    return entries

def SetTime():
    if _TimeHasExpired():
        context = GetContext()
        currentHeight = GetHeight()
        currentHeader = GetHeader(currentHeight)
        time = GetTimestamp(currentHeader) + TWOWEEKS
        print('setting time')
        print(time)
        Put(context, "endTime", time)
        return time
    return 0

def _TimeHasExpired():
    context = GetContext()
    currentHeight = GetHeight()
    print("got current height:")
    print(currentHeight)
    currentHeader = GetHeader(currentHeight)
    print("got current block...")
    endTime = Get(context, 'endTime')
    return endTime < GetTimestamp(currentHeader)

def AddEntry():
    tx = GetScriptContainer()
    context = GetContext()
    references = GetReferences(tx)

    # if _TimeHasExpired():
    #     # refund gas and neo and pick winner
    #     PickWinner()
    #     return 0
    
    print("adding entry")
    if len(references) < 1:
        print("no gas attached")
        return False

    print("reading reference")
    reference = references[0]
    print("reference read")

    sender = GetScriptHash(reference)
    print("sender hash is")
    print(sender)
    print("reading script hash")

    print("getting asset ID. ID is here:")
    output_asset_id = GetAssetId(reference)
    print(output_asset_id)
    print('asset id printed above')


    if output_asset_id == GAS_ASSET_ID:
        print("executing script hash")
        receiver = GetExecutingScriptHash()
        temp_outputs = GetOutputs(tx)
        for output in temp_outputs:
            print("getting shash..")
            shash = GetScriptHash(output)
            if shash == receiver:
                print("adding value?")
                value = GetValue(output) / 100000000
                print("value storing in entries")
                print(value)
                print('string we will save to the entries array')
                entries = Get(context, 'entries')
                print('current entries')
                print(entries)
                remainder = value % 1
                print('remainder is')
                Notify(remainder)
                value = value - remainder
                print('remainder and value set')
                Notify(value)
                if value > 0:
                    if entries != bytearray(b''):
                        print('deserializing the byte array')
                        entries = deserialize_bytearray(entries)
                        end = len(entries) + value
                        if end > 1024:
                            print('contest capped at 1024')
                            return 0
                        new_entries = range(0, end)
                        i = 0
                        for item in new_entries:
                            if i < len(entries):
                                new_entries[i] = entries[i]
                            else:
                                new_entries[i] = sender
                            i += 1
                        # last_entry = entries[len(entries) - 1]
                        # colon_index = [pos for pos, char in enumerate(
                        #     last_entry) if char == ':']
                        # previous_total = substr(
                        #     last_entry, 0, colon_index)
                    else:
                        print('setting an empty array')
                        # list isn't working below
                        new_entries = range(0, value)
                        j = 0
                        for item in new_entries:
                            new_entries[j] = sender
                            j += 1
                else:
                    print("no gas added")
                Notify(new_entries)
                new_entries = serialize_array(new_entries)
                Put(context, "entries", new_entries)
    return entries


def deserialize_bytearray(data):

    # ok this is weird.  if you remove this print statement, it stops working :/
    print("deserializing data...")

    # get length of length
    collection_length_length = substr(data, 0, 1)

    # get length of collection
    collection_len = substr(data, 1, collection_length_length)

    # create a new collection
    new_collection = list(length=collection_len)

    # calculate offset
    offset = 1 + collection_length_length

    # trim the length data
    newdata = data[offset:]

    for i in range(0, collection_len):

        # get the data length length
        itemlen_len = substr(newdata, 0, 1)

        # get the length of the data
        item_len = substr(newdata, 1, itemlen_len)

        start = 1 + itemlen_len
        end = start + item_len

        # get the data
        item = substr(newdata, start, item_len)

        # store it in collection
        new_collection[i] = item

        # trim the data
        newdata = newdata[end:]

    return new_collection


def serialize_array(items):

    # serialize the length of the list
    itemlength = serialize_var_length_item(items)

    output = itemlength

    # now go through and append all your stuff
    for item in items:

        # get the variable length of the item
        # to be serialized
        itemlen = serialize_var_length_item(item)

        # add that indicator
        output = concat(output, itemlen)

        # now add the item
        output = concat(output, item)

    # return the stuff
    return output


def serialize_var_length_item(item):

    # get the length of your stuff
    stuff_len = len(item)

    # now we need to know how many bytes the length of the array
    # will take to store

    # this is one byte
    if stuff_len <= 255:
        byte_len = b'\x01'
    # two byte
    elif stuff_len <= 65535:
        byte_len = b'\x02'
    # hopefully 4 byte
    else:
        byte_len = b'\x04'

    out = concat(byte_len, stuff_len)

    return out
