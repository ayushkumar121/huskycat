// Arrays

// str:type=struct(int64, byte[])

arr:ptr = resb 10*8
print (arr + 8)[0] // deref the first byte ?

// this will point to a statically allocated array 