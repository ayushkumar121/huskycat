// Arrays

// reserving 10 bytes of global memory
arr:ptr = resb 10

^arr = 'b'
b:byte =  ^arr

arr = arr + 1
^arr = 'c'
c:byte =  ^arr

print b
print '\n'

print c
print '\n'
// this will point to a statically allocated array 