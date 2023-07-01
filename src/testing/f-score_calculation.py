import json

with open('match_score_list_test_algo.json') as f:
    match_score_list = json.load(f)

print(len(match_score_list))

# app = QApplication([])

# correct_count = 600
wrong_count = 0
correct_count = 0
low_count = 0
sum = 0

for match in match_score_list:
    if match[2] != match[3] and match[4] > 0.1:
        wrong_count += 1
        sum += match[4]

for match in match_score_list:
    if match[2] == match[3] and match[4] > 0.1:
        correct_count += 1


# count matches under 0.1
for match in match_score_list:
    if match[4] < 0.1:
        low_count += 1

print(wrong_count)
print(low_count)
print(correct_count)
print(len(match_score_list) - low_count)
print(sum / wrong_count)

# precision = correct_count / (correct_count + wrong_count)
# recall = correct_count / 627
#
# f_score = 2 * precision * recall / (precision + recall)
#
# print(f'Precision: {precision}, Recall: {recall}, F-Score: {f_score}')
