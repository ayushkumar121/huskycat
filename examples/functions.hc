add := func (a:i64, b:i64, c:i64) -> (i64) { 
    -> a+b+c
}

// sub := func (a:i64, b:i64, c:i64) -> (i64) { 
//     -> add[a, b, c]
// }

a:=5
b:=6

print add[a, b, 6-1]+1
print '\n'
