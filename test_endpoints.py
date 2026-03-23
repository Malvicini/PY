from app import app

with app.test_client() as c:
    r = c.get('/api/families')
    print('families status:', r.status_code)
    try:
        print(r.get_json())
    except Exception as e:
        print('Could not decode JSON:', e)

    # if there is at least one family, try sequences
    js = r.get_json() or []
    if js:
        fam_code = js[0].get('family_code')
        r2 = c.get('/api/sequences?family_code=' + str(fam_code))
        print('sequences status:', r2.status_code)
        try:
            print(r2.get_json())
        except Exception as e:
            print('Could not decode JSON:', e)
