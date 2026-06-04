with open("app/main.py", "r", encoding="utf-8") as f:
    main_content = f.read()

with open("tests/test_simulate.py", "r", encoding="utf-8") as f:
    test_content = f.read()

import re

main_match = re.search(r'"name":\s*"(被迫妥協型)"', main_content)
test_match = re.search(r'==\s*"(被迫妥協型)"', test_content)

if main_match:
    main_str = main_match.group(1)
    print(f"main: {main_str} - bytes: {[ord(c) for c in main_str]}")
else:
    print("Not found in main.py")

if test_match:
    test_str = test_match.group(1)
    print(f"test: {test_str} - bytes: {[ord(c) for c in test_str]}")
else:
    print("Not found in test_simulate.py")
