#<%REGION File header%>
#=============================================================================
# File      : Path2NT.awk
# Author    : Gideon Kruseman <g.kruseman@cgiar.org>
# Version   : 1.0
# Date      : 10/17/2023 12:26:51 PM
# Changed   : 10/17/2023 2:49:24 PM
# Changed by: Gideon Kruseman <g.kruseman@cgiar.org>
# Remarks   :
# This code checks if a path is in windows format if it is in UNIX format it converts the path
# the script reads a single record and returns it in the right format
#=============================================================================
#<%/REGION File header%>
BEGIN {
  FS="/"
}
$0 && NR==1 {
  print $0
  path=$1
  print "path=$1:   " path
  for (i=2;i<=NF;i++) {
    path=path"\\"$i
    print "path=path\"\\\\\"$i:   " path
  }
}

END {
  print path > "TMP/Path2NT.return"
}
#============================   End Of File   ================================