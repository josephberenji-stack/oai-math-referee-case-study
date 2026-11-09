import os
import glob,collections,sys
E=collections.defaultdict(set)
C=os.environ.get("CLOSURE_DIR", "/srv/oai/casestudy/results-hodge/closure")
for d in [C+"/unfold", C+"/rerun-2026-11-03-hb/unfold"]:
    for f in glob.glob(d+"/*/*.tsv"):
        for l in open(f,errors="replace"):
            if l.startswith("EDGE\t"):
                c=l.rstrip("\n").split("\t")
                if len(c)>=6 and c[5]!="mathlib": E[c[1]].add(c[2])
src="OAI.AlgebraicGeometry.HodgeConjecture.ThetaCycle.AbelianMapsProduct.four_abelian_maps_nonzero_product"
seen={src}; st=[src]
while st:
    x=st.pop()
    for y in E.get(x,()):
        if y not in seen: seen.add(y); st.append(y)
print("constants reached from",src,len(seen),"; source has edges:",len(E.get(src,())))
for t in ["WeightOneInput","ConditionalWeightOneInput","surface_hodge_map_algebraic","p23_weight_one_of_conditional","algebraic_maps_of_hodge_term","algebraic_maps_of_wedge_data"]:
    print(t, sorted(n for n in seen if n.split(".")[-1]==t)[:4])
