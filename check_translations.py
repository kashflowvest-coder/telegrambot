import re
from i18n import TRANSLATIONS
missing = set()
for file_name in ['bot_handlers.py', 'bot_keyboards.py']:
    with open(file_name, encoding='utf-8') as f:
        content = f.read()
    keys = re.findall(r't\("([^"]+)"', content)
    keys += re.findall(r"t\('([^']+)'", content)
    for k in keys:
        if k not in TRANSLATIONS:
            missing.add(k)
with open('missing_keys.txt', 'w', encoding='utf-8') as f:
    for m in sorted(missing):
        f.write(m + '\n')
print("Done!")
