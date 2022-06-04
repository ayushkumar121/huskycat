// Datatypes: i64
// we also have a i32 type but i64 and i32 are not intercompatible rn

a:i64= 10+1*2
// ^ we need compile time evaluation for this

a=a+1

b:i64=7
b=a-b

print a b // we use c printf for printing but we would need a custom function for this in the future

// Datatypes: bool (8bit)
c:bool=true

// c=1 this should fail because of static typechecking
// ^

print c

// Logical operators
c = !c
print c


// Type Casting
// Maybe we will allow casting via following syntax

// d:int=1
// e:bool=cast:i64 d
// print e

// Control flow

// if ,,,,, { <-- jump to label if false
// 
// } <-- end

// Compiler configuration the file itself