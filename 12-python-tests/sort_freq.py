#!/usr/bin/env python3

def sort(arr, k):
    dic = {}
    for i in arr:
        if i not in dic:
            dic[i] = 1
        else:
            dic[i] += 1
    print(dic)
    result = sorted(dic, key=dic.get, reverse=True)[:k]
    return result

animals = ["dog", "cat", "cow", "dog", "cow", "dog"]
print(sort(animals, 2))
