import json

with open('country_code.json', 'r+') as f:
    text = "".join(f.readlines()) 

country_code = json.loads(text)
print(country_code)
output_dict: dict[str, str] = {}
with open('country_intro.txt', 'r+') as f:
    for pair in country_code:
        code = pair['Code']
        output_dict[code] = f.readline().strip()

with open('countryintro.json', 'w') as f:
    json.dump(output_dict, f)