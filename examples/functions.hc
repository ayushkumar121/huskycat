add := func (a:i64, b:i64, c:i64) -> (i64) { 
    -> a+b+c
}

sub := add

a:=5
b:=6

print sub[a, b, 6-1]+1
print '\n'
