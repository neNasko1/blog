---
title: Fancy Blog Tech
lang: en
date: "2026-01-04"
---

# Blog info

Personal blog of Atanas Dimitrov.

## Math

Math is supported through the use of the `MathML` standard: $3 = 1 + 2$

Inline $\sum_{i=1}^{n} i = \frac{n (n + 1)}{2}$.

And display:
$$
    \sum_{i=1}^{n} i = \frac{n (n + 1)}{2}
$$

For $a_{i} = a_{i - 1} + \frac{1}{2^{i}}$ we have $\lim_{i \rightarrow \infty} a_{i} = 2$.

## Code

Code is also supported and includes the default `pandoc` syntax highlighting.

```python
def a():
    return 100

print(10 + a())

very_long = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
```

```cpp
template<typename T, typename F>
std::vector<T> map(const std::vector<T>& input, const F& fn) {
    std::vector<T> ret = {};
    for (const auto& it : input) {
        ret.push_back(fn(it));
    }
    return ret;
}
```
