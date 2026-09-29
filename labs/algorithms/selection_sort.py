# 排序算法练习（选择排序）— 对应 learning/30
def selection_sort(arr):
    a = list(arr)
    n = len(a)
    for i in range(n):
        m = i
        for j in range(i + 1, n):
            if a[j] < a[m]:
                m = j
        a[i], a[m] = a[m], a[i]
    return a


def test_selection_sort():
    assert selection_sort([3, 1, 2]) == [1, 2, 3]
    assert selection_sort([]) == []


if __name__ == "__main__":
    test_selection_sort()
    print("algorithms lab OK")
