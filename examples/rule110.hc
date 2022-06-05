i:i64 = 0
board_width:i64=10
board_height:i64=10

while i<board_width {
    j:i64 = 0
    while j<board_height {
        print '$'
        j = j + 1
    }
    print '\n'
    i = i + 1
}