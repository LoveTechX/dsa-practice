/*
Problem: Two Sum
Platform: LeetCode
Link: https://leetcode.com/problems/two-sum/

Time Complexity: O(n)
Space Complexity: O(n)
*/

#include <bits/stdc++.h>
using namespace std;

class Solution
{
public:
    vector<int> twoSum(vector<int> &nums, int target)
    {
        unordered_map<int, int> map;
        vector<int> result;
        for (int i = 0; i < nums.size(); i++)
        {
            int complement = target - nums[i];
            if (map.find(complement) != map.end())
            {
                result.push_back(map[complement]);
                result.push_back(i);
                return result;
            }
            map[nums[i]] = i;
        }
        return result;
    }
};
int main()
{
    vector<int> nums = {2, 7, 11, 15};
    int target = 9;
    Solution solution;
    vector<int> result = solution.twoSum(nums, target);
    for (int num : result)
    {
        cout << num << " ";
    }
    cout << endl;
    return 0;
}
