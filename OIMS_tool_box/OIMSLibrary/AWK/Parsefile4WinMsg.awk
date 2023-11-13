#<%REGION File header%>
#=============================================================================
# File      : Parsefile4WinMsg.awk
# Author    : Gideon Kruseman <g.kruseman@cgiar.org>
# Version   : 1.0
# Date      : 3/9/2023 6:22:07 PM
# Changed   : 3/9/2023 7:10:52 PM
# Changed by: Gideon Kruseman <g.kruseman@cgiar.org>
# Remarks   :
#  In order to use winmsg system to show larger text files that have been generated
#  such as the error handling file ADAMControlerror.txt we need to parse the file and send it to
#
#
#=============================================================================
#<%/REGION File header%>
BEGIN {
    FS=","
    printf("\n\n")
}
$0 {
    if (CurrentFileName!=FILENAME) {
        CurrentFileName=FILENAME
        ++FileCounter

    }
}
$0 && FileCounter==1 {
     winmessageID=$1
     printf("put_utility f 'WinMsg' / 'test' / 'the following can be found in the file %s: ';\n",$2)
     printf("put_utility f 'WinMsg' / 'test' / ' . ';\n")

}

$0 && FileCounter==2 {
    gsub(/'/, "\`", $0)
    printf("put_utility f 'WinMsg' / '" winmessageID "' / '%s';\n", $0)
}
END{
     printf("put_utility f 'WinMsg' / 'test' / ' . ';\n")
     printf("put_utility f 'WinMsg' / 'test' / ' . ';\n")
     printf("put_utility f 'WinMsg' / 'test' / ' this window message will disappear automatically after a few minutes';")

}
#============================   End Of File   ================================