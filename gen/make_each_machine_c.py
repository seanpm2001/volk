#
# Copyright 2010-2011 Free Software Foundation, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from volk_regexp import *
import string

def _make_each_machine_struct(machine_name, archs, functions, fcountlist, taglist, alignment):

    #make the machine fcountlist and taglist a subset given the archs list
    machine_fcountlists = list()
    machine_taglists = list()
    for i in range(len(fcountlist)):
        machine_fcountlist = list()
        machine_taglist = list()
        for j in range(len(fcountlist[i])):
            if len(set(archs).intersection(map(str.lower, fcountlist[i][j]))) == len(fcountlist[i][j]):
                machine_fcountlist.append(fcountlist[i][j])
                machine_taglist.append(taglist[i][j])
        machine_fcountlists.append(machine_fcountlist)
        machine_taglists.append(machine_taglist)

    #create the volk machine struct for this machine file
    tempstring = ""
    tempstring += "struct volk_machine volk_machine_" + machine_name + " = {\n"
    tempstring += "    " + ' | '.join(["(1 << LV_" + arch.swapcase() + ")" for arch in archs]) + ",\n"
    tempstring += "    \"%s\",\n"%machine_name
    tempstring += "    %s,\n"%alignment

    #fill in the description for each function
    for i in range(len(functions)):
        tempstring += "    \"%s\",\n"%functions[i]
        tempstring += "    {%s},\n"%(', '.join(['"%s"'%tag for tag in machine_taglists[i]]))
        tempstring += "    {%s},\n"%(', '.join([' | '.join(['(1 << LV_%s)'%fc for fc in fcount]) for fcount in machine_fcountlists[i]]))
        tempstring += "    {%s},\n"%(', '.join(['%s_%s'%(functions[i], tag) for tag in machine_taglists[i]]))
        tempstring += "    %d,\n"%len(machine_taglists[i])

    tempstring = strip_trailing(tempstring, ",")
    tempstring += "};\n"
    return tempstring

def make_each_machine_c(machine_name, archs, functions, fcountlist, taglist, alignment):
    tempstring = r"""
// This file is automatically generated by make_each_machine_c.py.
// Do not edit this file.
"""
    for arch in archs:
        tempstring += "#define LV_HAVE_" + arch.swapcase() + " 1\n"
    
    tempstring += """
#include <volk/volk_common.h>
#include "volk_machines.h"
#include <volk/volk_config_fixed.h>

"""
    for func in functions:
        tempstring += "#include <volk/" + func + ".h>\n"
    tempstring += "\n\n"

    tempstring += """
#ifdef LV_HAVE_ORC
%s
#else
%s
#endif
"""%(
    _make_each_machine_struct(machine_name, archs+["orc"], functions, fcountlist, taglist, alignment),
    _make_each_machine_struct(machine_name, archs, functions, fcountlist, taglist, alignment)
)

    return tempstring

