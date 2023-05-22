# set duplicate names' genders to be the same (only if one of them is unknown, not if one name is marked as male vs
# female)
def fix_unmatched_genders(db):
    names = [record['ID'] for record in db]
    genders = [record['gender'] for record in db]
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if names[j] == names[i] and genders[i] != genders[j]:
                unk = i if genders[i] == 'unknown' else j
                k = j if unk == i else i
                db[unk]['gender'] = db[k]['gender']

    return db