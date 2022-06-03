// Datatypes: int (signed 64bit)
a:i32=10+1
// ^ we need compile time evaluation for this

a=a+1

b:i64=7
b=a-b

print a b // we use c printf for printing but we would need a custom function for this in the future

// Datatypes: bool (8bit)
c:bool=false
print c

// c=1 this should fail because of static typechecking
// ^
// Maybe we will allow casting via following syntax
// c:int=1


// Logical operators
// c = c or false and not or

// Control flow

// if ,,,,, { <-- jump to label if false
// 
// } <-- end