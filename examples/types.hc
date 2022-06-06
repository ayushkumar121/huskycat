// Datatypes: i64
// we also have a i32 type but i64 and i32 are not intercompatible rn

a:i64=10+1*2
// ^ we need compile time evaluation for this
a=a+1

print a // we use c printf for printing but we would need a custom function for this in the future

// Datatypes: bool (8bit)
b:bool=true

// b=1
// ^  this should fail because of static typechecking
print b

// Datatypes: byte (8bit)

c:byte='a'

print c
print '#'