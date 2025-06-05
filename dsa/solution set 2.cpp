#include <bits/stdc++.h>
#define pb push_back

using namespace std;

// using g++ version 15

int helper(vector<int>& arr, int pos, int prev){
    if(arr.size() == pos) return  0;
    if(arr[pos] > prev){
        return max(
            1 + helper(arr, pos+1, arr[pos]),
            helper(arr, pos+1, prev)
        );
    } else {
        return helper(arr, pos+1, prev);
    }
}

int main() {
    vector<int> arr;
    int num;
    while(cin>>num){
        arr.pb(num);
        if(cin.peek() == '\n') break;
    }
    cout<<helper(arr, 0, -1);

}