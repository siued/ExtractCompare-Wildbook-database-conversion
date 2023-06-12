import json

with open('match_score_list_test_algo.json') as f:
    match_score_list = json.load(f)

sum = 0
count = 0

sum2 = 0
count2 = 0

for match in match_score_list:
    if match[2] != match[3] and match[4] > 0.5:
        print(match)
        sum += match[4]
        count += 1

    if match[2] == match[3]:
        sum2 += match[4]
        count2 += 1

print(sum / count)
print(count)

print(sum2 / count2)
print(count2)