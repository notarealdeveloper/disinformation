# disinformation

This module contains methods of handling NaN heavy
data without having to guess the missing values.

The current methods are intentionally simple
proofs of concept that aim to:

1. Perform a presence-absence encoding,
   so that a value being NaN becomes a
   non-problematic fact about the data,
   rather than "missing data" that we
   need to impute or infer before using
   certain models.

2. Put all features on a common scale,
   so as not to confuse statistical models
   that implicitly assume the data lives in
   a euclidean or affine space in which
   "every direction has the same units."

3. Explicitly represent the frequency with
   each feature column is present or absent,
   rather than just representing the fact
   of their presence or absence as a 0 or 1.
   That is, for a given input feature `a`,
   larger numbers in the `a_presence`
   column correspond to rarer events in
   terms of the presence or absence of
   that feature. This follows the common
   idea in information theory (or in every
   day language) that common things should
   have simple encodings, and the less common
   a thing, the "larger" is the space occupied
   by its encoding. Since we typically use
   models that operate on floats rather than
   abstract code-words, the largeness of the
   floats in the `presence` encodings below
   is intended to represent the rareness of
   the presence or absence of that feature
   in the dataset.


Other methods readily suggest themselves,
but here's how the current ones work:


# Example 1

# The functions can take a dataframe or a series.

```
>>> nan = float('nan')

>>> s = pd.Series([-100,nan,+1000], name='a')
```

encode_jaynes uses a cdf representation of the data,
which handles outliers better but loses information
about absolute scale.

```
>>> es.encode_jaynes(s)

   a_presence  a_value
0    0.333333     -1.0
1   -0.666667      0.0
2    0.333333      1.0
```

encode_shannon uses a z-scored representation of the data,
which handles outliers less well and removes absolute units,
but preserves relative magnitude in standard-deviation units.
That is, though this representation does not retain absolute
scale, it preserves relative position in units of that column's
standard deviation.

```
>>> es.encode_shannon(s)

   a_presence   a_value
0    0.764828 -0.707107
1   -1.258953  0.000000
2    0.764828  0.707107
```

We can also pass them dataframes.

```
>>> df = pd.DataFrame({'a': [1,2,nan], 'b': [3, nan, nan]})

>>> df
     a    b
0  1.0  3.0
1  2.0  NaN
2  NaN  NaN

>>> es.encode_jaynes(df)

   a_presence  a_value  b_presence  b_value
0    0.333333     -1.0    0.666667      0.0
1    0.333333      1.0   -0.333333      0.0
2   -0.666667      0.0   -0.333333      0.0

>>> es.encode_shannon(df)

   a_presence   a_value  b_presence  b_value
0    0.764828 -0.707107    1.258953      0.0
1    0.764828  0.707107   -0.764828      0.0
2   -1.258953  0.000000   -0.764828      0.0
```
