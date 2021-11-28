import sys
from collections import deque

#Membaca input dari file .txt
file = open(sys.argv[1], "r")
text = list(file)
text[len(text) - 1] += "\n"
text = deque([s.strip() for s in text])
original = text.copy()

def getComponent(stringInput):
    array = stringInput.split(',')
    stripped = [i.strip(',)RW( ') for i in array]
    return stripped

def searchLock(name, lockList):
    for lock in (lockList):
        if (lock[1] == name):
            return lock[0]
    return False

def checkTransactions(arrayInput, trx):
    count = 0
    for inp in (arrayInput):
        if (trx == getComponent(inp)[0]):
            count+=1
    return count

def unlockLocks(trx, lockList):
    for lock in (lockList):
        if (lock[0] == trx):
            lockList.remove(lock)
            print("[>]"+lock[0], "UNLOCKS", lock[1])
    return lockList


lock = []
queue = deque([])
aborted = []
#CheckQueue akan diupdate menjadi true bila ada terjadi abort/commit
#Karena disaat abort/commit akan terjadi pelepasan lock
checkQueue = False

while (len(text) != 0):
    #Bila ada queue menunggu
    if (queue and checkQueue):
        current = (queue.popleft())
    else:
        current = (text.popleft())
    
    #Kalau Tx sudah di abort maka tidak dijalankan
    if (getComponent(current)[0] in aborted):
        continue
    
    print(current)
    if (current[0] == 'R'):
        R = getComponent(current)
        
        #Tx sudah memiliki lock
        if (R in lock):
            print('*'+R[0], "already has exclusive lock for", R[1])
            print("[>]"+R[0], "READ" , R[1])
        else:
            print(R[0], "request lock for", R[1])
            #Lock sedang dipegang transaksi lain
            if (searchLock(R[1], lock)):
                print("[X]Deny request,", searchLock(R[1], lock), "has the lock")
                #Bila jumlah write/read request hanya 1, diperbolehkan menunggu
                if(checkTransactions(original, R[0]) == 1):
                    queue.append(current)
                    print("[>]"+R[0], "is added to the queue")
                    checkQueue = False
                else:
                    print('*'+R[0], "has more than 1 Write/Read request")
                    print("[>]ABORT", R[0])
                    #Melepas lock
                    lock = unlockLocks(R[0], lock)
                    #Memasukan ke list transaction yang aborted
                    aborted.append(R[0])
                    checkQueue = True
                    
            else:
                print("lock request approved")
                print("[>]"+R[0], "LOCK", R[1])
                lock.append([R[0],R[1]])
                print("[>]"+R[0], "READ" , R[1])
        
    elif (current[0] == 'W'):
        W = getComponent(current)
        
        #Tx sudah memiliki lock
        if ([W[0],W[1]] in lock):
            print('*'+W[0], "already has exclusive lock for", W[1])
            print("[>]"+W[0], "WRITE" , W[1], "with", W[2])
        else:
            print(W[0], "request lock for", W[1])
            #Lock sedang dipegang transaksi lain
            if (searchLock(W[1], lock)):
                print("[X]Deny request,", searchLock(W[1], lock), "has the lock")
                #Bila jumlah write/read request hanya 1, diperbolehkan menunggu
                if(checkTransactions(original, W[0]) == 1):
                    queue.append(R)
                    checkQueue = False
                else:
                    print('*'+W[0], "has more than 1 Write/Read request")
                    print("[>]ABORT", W[0])
                    #Melepas lock
                    lock = unlockLocks(W[0], lock)
                    #Memasukan ke list transaction yang aborted
                    aborted.append(W[0])
                    checkQueue = True
                    
            else:
                print("lock request approved")
                print("[>]"+W[0], "LOCK", W[1])
                lock.append([W[0],W[1]])
                print("[>]"+W[0], "WRITE" , W[1], "with", W[2])
        
    elif (current[0] == 'C'):
        #Membuka semua lock Tx
        trx = "T"+current.strip('C')
        lock = unlockLocks(trx, lock)
        checkQueue = True
    else:
        print("Ada yang salah dengan input file")
    print()

