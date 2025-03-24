## Computation Approach (V2)

The file **V2** contains the final approach for computation. A **BFS (Breadth-First Search)** is used to explore nodes in lexicographical order.

- When the length of words in the response is **greater than or equal to** the maximum length returned by the API, the last two words of the response are checked for a common prefix.
- The first differing letter in the last word is identified that is not common in the last two words, forming a new prefix:  
  **common prefix + first differing letter**  
- This new prefix is stored on that node. When BFS reaches this node, any lexicographical order less than the stored word is ignored.
  
- If the response length is **less than** the maximum possible response length, the BFS does not explore its children when reaching this node.
