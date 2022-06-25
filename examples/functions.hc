add := func (a:i64, b:i64, c:i64) -> (i64) { 
    print a
    print '\n'

    print b
    print '\n'

    print c
    print '\n'

    -> a+b+c
}
a:=5
b:=6

print add[a, b, a]+1
print '\n'
