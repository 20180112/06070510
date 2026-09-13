# 线上面试：动态规划 / 回溯手撕模板

口诀：DP 先说「状态是什么、从哪转来、初始值、答案在哪」；回溯是「路径、选择列表、剪枝、递归、撤销」。

---

## 一、回溯万能模板

```python
def backtrack(path, 可选集合或下标):
    if 满足结束条件:
        ans.append(path[:])   # 一定拷贝
        return
    for 选择 in 当前可选:
        if 不合法:           # 剪枝
            continue
        path.append(选择)     # 做选择
        backtrack(...)        # 进入下一层
        path.pop()            # 撤销
```

三个变体只改「循环从哪开始、用不用 visited」：

| 题型 | 循环 | visited | 去重 |
| --- | --- | --- | --- |
| 子集 subsets | `for i in range(start, n)` | 不用 | 同层 `i>start and nums[i]==nums[i-1]` 需先排序 |
| 组合 combination | 同上，path 长度到 k 结束 | 不用 | 同上 |
| 排列 permutation | `for i in range(n)` | 要用 | `used[i]`；同值还要 `used[i-1]==False` 才跳过 |

### 子集（含去重）

```python
def subsets(nums):
    nums.sort()
    ans, path = [], []
    def dfs(start):
        ans.append(path[:])          # 每个节点都记一份
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue
            path.append(nums[i])
            dfs(i + 1)               # i+1：每个数最多一次
            path.pop()
    dfs(0)
    return ans
```

组合总和（可重复用同一数字）：`dfs(i)` 不是 `dfs(i+1)`，并加 `if s > target: return`。

### 全排列

```python
def permute(nums):
    n, ans, path = len(nums), [], []
    used = [False] * n
    def dfs():
        if len(path) == n:
            ans.append(path[:])
            return
        for i in range(n):
            if used[i]:
                continue
            used[i] = True
            path.append(nums[i])
            dfs()
            path.pop()
            used[i] = False
    dfs()
    return ans
```

### 回溯怎么讲（线上 20 秒）

「用递归搜索所有方案。进入时把选择放进路径，返回时 pop 掉，这样各分支互不影响。结束条件就是收到一组完整解。重复数字先排序，同一层相同值只走第一个，避免重复组合。」

---

## 二、DP 通用四步（先口述再写代码）

1. **dp 含义**：`dp[i]` / `dp[i][j]` 表示什么。  
2. **转移**：从哪几个已知状态来。  
3. **初始**：`dp[0]`、空串、第一行第一列。  
4. **答案**：`dp[n]` 还是 `max(dp)`。

一维能滚就一维，省空间面试加分但正确更重要。

### 模板 A：一维线性（爬楼梯 / 打家劫舍）

```python
# 爬楼梯：dp[i] = dp[i-1] + dp[i-2]
def climb(n):
    if n <= 2:
        return n
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b

# 打家劫舍：dp[i] = max(dp[i-1], dp[i-2] + nums[i])
def rob(nums):
    pre2 = pre1 = 0          # 前两家的最优
    for x in nums:
        pre2, pre1 = pre1, max(pre1, pre2 + x)
    return pre1
```

口述：「到第 i 个，要么不用它（等于 i-1），要么用它（等于 i-2 加上它）。」

### 模板 B：完全背包 / 零钱兑换（可重复选）

`dp[j]` = 凑出金额 j 的最少硬币数。外层物品或金额都可以，完全背包是 **金额从小到大**（正序），让同一硬币用多次。

```python
def coinChange(coins, amount):
    inf = amount + 1
    dp = [0] + [inf] * amount
    for x in coins:
        for j in range(x, amount + 1):     # 正序 = 可重复
            dp[j] = min(dp[j], dp[j - x] + 1)
    return dp[amount] if dp[amount] < inf else -1
```

0-1 背包（每个物品一次）：内层 **倒序** `for j in range(W, w-1, -1)`。

口述：「背包容量当第二维。能重复用就正序更新，只能用一次就倒序，避免本轮新值把自己再加一遍。」

### 模板 C：网格（路径数 / 最小路径和）

```python
def uniquePaths(m, n):
    dp = [1] * n
    for _ in range(1, m):
        for j in range(1, n):
            dp[j] += dp[j - 1]     # 上 + 左，滚动成一行
    return dp[-1]

def minPathSum(grid):
    m, n = len(grid), len(grid[0])
    dp = [0] * n
    dp[0] = grid[0][0]
    for j in range(1, n):
        dp[j] = dp[j - 1] + grid[0][j]
    for i in range(1, m):
        dp[0] += grid[i][0]
        for j in range(1, n):
            dp[j] = min(dp[j], dp[j - 1]) + grid[i][j]
    return dp[-1]
```

口述：「格子只能从左边或上边来，障碍物把 dp 设成 0 或 inf。」

### 模板 D：两个字符串（LCS / 编辑距离）

`dp[i][j]` = 第一个串前 i 个、第二个前 j 个 的结果。实现多用 `(n+1)*(m+1)`，下标偏 1。

```python
def longestCommonSubsequence(a, b):
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[n][m]

def minDistance(a, b):  # 编辑距离
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],      # 删
                    dp[i][j - 1],      # 插
                    dp[i - 1][j - 1],  # 改
                )
    return dp[n][m]
```

口述 LCS：「相等就左上角 +1，不等就左边或上边取 max。」  
口述编辑距离：「相等直接抄左上；不等是删、插、改三种 +1 取最小。第一行第一列是和空串的距离。」

### 模板 E：最长递增子序列 LIS（n² 可过面试）

```python
def lengthOfLIS(nums):
    n = len(nums)
    dp = [1] * n                 # 以 i 结尾的 LIS
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)
```

口述：「每个位置取前面所有比它小的 dp 的最大值再 +1。」

---

## 三、线上怎么说再怎么写

1. 先 15 秒：这是回溯还是 DP。  
2. DP 说清 `dp[i]`；回溯说清结束条件和剪枝。  
3. 写代码：先函数签名和 `ans`，再循环。  
4. 举一个 `n=3` 的小例子自己走一遍。  
5. 复杂度：回溯最坏指数；DP 一般 \(O(n^2)\) 或 \(O(nm)\)。

---

## 四、考前默写清单（各写一遍）

回溯：子集、全排列、组合总和。  
DP：打家劫舍、零钱兑换、最小路径和、LCS、编辑距离。
