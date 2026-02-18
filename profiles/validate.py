from profiles import Recipe, Research


def validate_recipes(recipes: list[Recipe]) -> bool:
    ids_all = set()
    ids_in = set()
    ids_out = set()
    recipe_ids = set()
    for r in recipes:
        if r.id in recipe_ids:
            print(f"Duplicate Recipe ID: {r.id}")
        else:
            recipe_ids.add(r.id)
        ids_in |= set([i.id for i in r.inp])
        ids_out |= set([i.id for i in r.out])
        ids_all |= ids_in | ids_out
    for id in ids_in.difference(ids_out):
        print(f"Item can't be produced: {id}")
    return len(ids_in.difference(ids_out)) == 0


def validate_research(research: list[Research]) -> bool:
    research_ids = set()
    research_prerequs = set()
    for r in research:
        if r.prerequisites:
            research_prerequs |= set(r.prerequisites)
        research_ids.add(r.id)
    for id in research_prerequs.difference(research_ids):
        print(f"Research is a prerequisite but can't be researched: {id}")
    return len(research_prerequs.difference(research_ids)) == 0
