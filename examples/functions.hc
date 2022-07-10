first := func (a:i64, b:i64, c:i64) -> (i64) { 
    -> a+b+c
}

second := func (a:i64, b:i64, c:i64) -> (i64) { 
    -> first[a, b, c]
}

third := second

a:=5
b:=6

print third[a, b, 6-1]+1
print '\n'