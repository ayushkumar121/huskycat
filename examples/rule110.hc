
width:i64=40
height:i64=30
state:ptr=resb 2400
s:ptr=state

i:i64 = 0
j:i64 = 0
while j<width*height {
    s=state+j
    ^s='_'
    j = j + 1
}

s=state+38
^s='#'

while i<height {
    j = 0
    s = state
    while j<width {
        s=state+j+i*width
        print ^s
    
        print '\b'
            
        j = j + 1
    }
    print '\n'
    
    j = 0
    while (j<width-2) && (i<height-1){
        s1:ptr=state+j+ i*width
        s2:ptr=state+j+1 + i*width
        s3:ptr=state+j+2 + i*width


        // 111 => 0
        if (^s1 == '#')&&(^s2 == '#')&&(^s3 == '#')  {
            s2=state+j+1 + (i+1)*width
            ^s2='_'
        }
    
        // 110 => 1
        else if (^s1 == '#')&&(^s2 == '#')&&(^s3 == '_')  {
            s2=state+j+1 + (i+1)*width
            ^s2='#'

        }
   
        // 101 => 1
        else if (^s1 == '#')&&(^s2 == '_')&&(^s3 == '#')  {
            s2=state+j+1 + (i+1)*width
            ^s2='#'

        }

        // 100 => 0
        else if (^s1 == '#')&&(^s2 == '_')&&(^s3 == '_')  {
            s2=state+j+1 + (i+1)*width
            ^s2='_'

        }

        // 011 => 1
        else if (^s1 == '_')&&(^s2 == '#')&&(^s3 == '#')  {
            s2=state+j+1 + (i+1)*width
            ^s2='#'

        }

        // 010 => 1
        else if (^s1 == '_')&&(^s2 == '#')&&(^s3 == '_')  {
            s2=state+j+1 + (i+1)*width
            ^s2='#'
        
        }
        
        // 001 => 1
        else if (^s1 == '_')&&(^s2 == '_')&&(^s3 == '#')  {
            s2=state+j+1 + (i+1)*width
            ^s2='#'
            
        }

        // 000 => 0
        else if (^s1 == '_')&&(^s2 == '_')&&(^s3 == '_')  {
            s2=state+j+1 + (i+1)*width
            ^s2='_'

        }

        j = j + 1
    }
    
i=i+1
}