# sloths
Expressive DataFrame querying

Usage
```python
from sloths import curry, make_queryable
from pandas import DataFrame

@curry
def has(a,b):
    return a in b

df = make_queryable(df)

df.lookup(
    col_a = has('a') & has('s')
)
```
