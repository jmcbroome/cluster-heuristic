import json
import parsimony_pb2
import argparse

intconv = {b:i for i,b in enumerate("ACGT")}

def create_mobj(mstr, refstr):
    if mstr[0] == "-":
        #ambiguous parent base. Assume reference, and return none if the new mutation matches the reference.
        rb = refstr[int(mstr[1:-1])]
        if rb == mstr[-1]:
            return None
        else:
            parent = rb
    else:
        parent = mstr[0]
    if mstr[-1] == '-':
        #ambiguous alternative base. mask it out and return None for now.
        return None
    mobj = parsimony_pb2.mut()
    mobj.mut_nuc.append(intconv[mstr[-1]])
    mobj.par_nuc = intconv[parent]
    mobj.position = int(mstr[1:-1])
    mobj.ref_nuc = intconv[refstr[int(mstr[1:-1])]] 
    return mobj

def build_mutation_list(jsd, ml, refstr):
    nml = parsimony_pb2.mutation_list()
    for m in jsd['branch_attrs']['mutations'].get('nuc',[]):
        mo = create_mobj(m, refstr)
        if mo != None:
            nml.mutation.append(mo)
    ml.append(nml)
    for c in jsd.get('children',[]):
        ml = build_mutation_list(c, ml, refstr)
    return ml

def build_newick(jsd):
    blen = len(jsd['branch_attrs']['mutations'].get('nuc',[]))
    if "children" not in jsd:
        return jsd['name'] + ":" + str(blen)
    else:
        return "(" + ",".join([build_newick(c) for c in jsd['children']]) + ")" + ":" + str(blen)

def parse_args():
    parser = argparse.ArgumentParser(description='Convert auspice json to protobuf')
    parser.add_argument('-i', '--input', required=True, help='input auspice json')
    parser.add_argument('-o', '--output', required=True, help='output protobuf')
    parser.add_argument('-r', '--reference', required=True, help='reference genome')
    return parser.parse_args()

def main():
    args = parse_args()
    f = open(args.input, 'r')
    data = json.load(f)
    f.close()
    mat = parsimony_pb2.data()
    mat.newick = build_newick(data['tree']) + ";"
    rf = open(args.reference, 'r')
    refstr = "".join([l.strip() for l in rf.readlines()])
    rf.close()
    mlv = build_mutation_list(data['tree'], parsimony_pb2.data().node_mutations, refstr)
    mat.node_mutations.extend(mlv)
    f = open(args.output, 'wb+')
    f.write(mat.SerializeToString())
    f.close()

if __name__ == '__main__':
    main()