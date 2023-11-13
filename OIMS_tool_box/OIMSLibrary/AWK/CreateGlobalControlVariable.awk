#<%REGION File header%>
#=============================================================================
# File      : CreateGlobalControlVariable.awk
# Author    : Gideon Kruseman <g.kruseman@cgiar.org>
# Version   : 1.0
# Date      : 10/17/2023 12:49:28 PM
# Changed   : 10/17/2023 2:27:21 PM
# Changed by: Gideon Kruseman <g.kruseman@cgiar.org>
# Remarks   :
#
# $call awk -v global=<control variable identifier> file with value on first line
#
#=============================================================================
#<%/REGION File header%>
$0 && NR==1 {print "$setglobal " global "  " $0 > "TMP/CreateGlobalControlVariable.return"}
#============================   End Of File   ================================