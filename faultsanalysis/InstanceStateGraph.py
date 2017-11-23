# Build graphs for InstanceStateAnalysis
# Author: Vincenzo Musco (http://www.vmusco.com)
# Date: November 20, 2017

import argparse
import re
import faultsanalysis.InstanceStateAnalysis as so
import smali.SmaliInstructionMatchers as sim
import smali.SmaliObject
import smali.SmaliProject
import networkx as nx

def buildName(clazz, name, params, ret):
    name = '%s.%s(%s)%s' % (clazz.replace('/', '.')[1:-1], name, params, ret)
    return name

def draw(G, frm, method, project = None):
    for line in method:
        mtch = sim.matchVirtualOrDirectInvocation(line)[2:]

        if mtch is None:
            mtch = sim.matchSuperInvocation(line)

        if mtch is not None:
            name = buildName(*mtch)
            G.add_edge(frm, name)

            if project is not None:
                # look recursively for other methods...
                cl = project.searchClass(mtch[0])
                if cl is not None:
                    m = cl.findMethod(mtch[1], mtch[2], mtch[3])

                    if m is not None:
                        draw(G, name, m.getCleanLines(), project)

            #print(name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export GraphML call graphs related to saving/restoring activities instances...')
    parser.add_argument('smali', type=str,
                        help='Folder containing smali files')
    parser.add_argument('output', type=str,
                        help='Folder where to output graphs files')
    parser.add_argument('--recursive', '-R', action='store_true',
                        help='True to follow recursion in calls')

    args = parser.parse_args()
    path = args.smali
    rec = args.recursive

    project = smali.SmaliProject.SmaliProject()
    project.parseFolder(path)

    for dentry in so.findClassesOfInterests(project):
        clazz = dentry["class"]
        type = dentry["type"]
        rootparent = dentry["rootparent"]
        filename = '%s'% (re.sub('[.()/;]', '_', clazz.getBaseName().replace('/', '.')))

        # Let's look if developper override reading/writing methods...
        loadSave = so.findReadWriteMethods(type, clazz.methods)
        loadInstanceDeclaration = loadSave["load"]
        saveInstanceDeclaration = loadSave["save"]

        loadInvokeSuper = 0
        saveInvokeSuper = 0

        G = nx.DiGraph()

        for k in loadInstanceDeclaration + saveInstanceDeclaration:
            frm = k.getFullSignature()

            G.add_node(frm)
            draw(G, frm, k.getCleanLines(), project if rec else None)

        if G.number_of_nodes() > 0:
            fullpath = "%s/%s_%s.graphml" % (args.output, 'F' if not rec else 'R', filename)
            while '//' in fullpath:
                fullpath = fullpath.replace('//', '/')

            print('Generating %s' % fullpath)
            nx.write_graphml(G, fullpath)