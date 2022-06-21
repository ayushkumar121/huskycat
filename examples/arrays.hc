arr:^i64 = [10] i64

i:i64=0
while i<10 {
    temp:^i64 = arr+i*8
    ^temp=i
    i = i+1
}

i=0
while i<10 {
    temp:^i64 = arr+i*8
    print ^temp
    print '\n'
    i = i+1
}