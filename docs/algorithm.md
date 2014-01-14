Date Inference Algorithm
========================

Problem Statement
-----------------

In order to automatically generate time series analyses of tabular data, we need a way to determine if a series
of entries represent a date (or date and time) and, if so, how to read that date so we can normalize the representation.
Unfortunately, ISO 8601 has not existed since time immemorial, so there are a plethora of formats possible. Furthermore,
many of the formats are ambiguous: 5/5/5 could be interpreted as:

- May 5 2005 (month-day-year)
- May 2005 5 (month-year-day)
- 5 May 2005 (day-month-year)
- 5 2005 May (day-year-month)
- 2005 May 5 (year-month-day)
- 2005 5 May (year-day-month)

(Furthermore, year '5' could refer to 1905 or, less likely, 5 CE.)

Another complication is that entries may contain noise. For example, so entries could contain a time portion or a
timezone, while others do not. Entries may be blank. Some entries could contain years with four digits and others with
two digits.

Assumptions
-----------

1. Formats will not be redundant. This means that months, for example, will not be repeated within a single entry.
2. Every example instance shall encode zero or one date / date-time instances.
3. Dates are part of the Gregorian Calendar.
4. Dates will fall into the near past/near future (e.g. 1000 CE <= year <= 9999 CE).
5. Dates are not relative (e.g. "yesterday").

Overview of Approach
--------------------

1. Drop entries with zero length.
2. Tokenize entries by character class.
3. Reduce list of tokenized entries to those with the most common (mode) length
4. For tokens that share the same index within the tokenized list, assign date time elements based on
   their probability (matches) and break ties based on their restrictivity (i.e. month numbers (1..12)
   are more restrictive than day of months (1..31).
5. Apply corrective rules (similar to Brill Tagger: http://dx.doi.org/10.3115/974499.974526 ) to arrive at a final
   list of date elements
6. Convert date elements to their strptime format elements.

