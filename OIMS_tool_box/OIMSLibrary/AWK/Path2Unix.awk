#<%REGION File header%>
#=============================================================================
# File      : Path2Unix.awk
# Author    : Gideon Kruseman <g.kruseman@cgiar.org>
# Version   : 1.0
# Date      : 10/17/2023 12:26:51 PM
# Changed   : 10/17/2023 2:45:21 PM
# Changed by: Gideon Kruseman <g.kruseman@cgiar.org>
# Remarks   :
# This code checks if a path is in unix format if it is in DOS or NT or Windows format it converts the path
# the script reads a single record and returns it
#=============================================================================
#<%/REGION File header%>
BEGIN {
  FS="\\"
}
$0 && NR==1 {
  print $0
  path=$1
  print "path=$1:   " path
  for (i=2;i<=NF;i++) {
    path=path"/"$i
    print "path=path\"/\"$i:   " path
  }
}

END {
  print path > "TMP/Path2Unix.return"
}
#============================   End Of File   ================================