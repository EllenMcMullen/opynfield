motion probability types
========================

The Basics
==========

The **motion probabilities** are a measure of directional persistence (or lack thereof) in the edge region of the arena. They are a collection of 5 measures: P++, P+-, P+0, P0+, and P00.
**P++** is the probability that the animal will take another step forward given that it just took a step forward.
**P+-** is the probability that the animal will take a step in a new direction of travel, given that it just took a step forward.
**P+0** is the probability that the animal will not take a step, given that it just took a step forward.
**P0+** is the probability that the animal will take a step forward given that it was just at rest.
**P00** is the probability that the animal will not take a step, given that it was just at rest.
These measures were originally described in the paper `Modeling novelty habituation during exploratory activity in *Drosophila* <https://d1wqtxts1xzle7.cloudfront.net/50278544/02e7e51e3f4d304a49000000-libre.pdf?1479009170=&response-content-disposition=inline%3B+filename%3DModeling_novelty_habituation_during_expl.pdf&Expires=1689294312&Signature=KkuYstzOiopWFeukXNzviCML8rYh545-nccaGZH-XSpcfuY2gIwy60q36x1GTnUctpquWbixq9yoXQ9O02~yOFi2xgbhREBmQ7KOqhf-wOLOuNqQ6Gunr-sV2pHtFf1hYDtBv1mF-ls56doxJlLjXQZdJ-kdfCbd7y1FSaOoeibyQ0YqVHmPnquwxj31~-J~vVbFN6mPx3A~VJK84ujdDme0dI-kMhn~h3WJ2PUv8qCsyjXjfBn3vI5FWfJWhw1v725doy2gOJQHy4LXLrR27DOYlP6D2crD3-mWFzidR3olGmIk39O~FAxuLTaoH5tHbL2nWncXoILoXaLDdOi4mQ__&Key-Pair-Id=APKAJLOHF5GGSLRBV4ZA>`_

To calculate the motion probabilities, you need to look at a group of animals. Individual animals just have the presence of absence of a behavior recorded at each time point (1 or 0). The group's motion probabilites are then calculated by taking the appropriate averages.
First let's consider the individual presence / absence measures. To do this we need to look at 3 consecutive tracking points.
If the animal takes a step between the 1st and 2nd points, then it has 3 options. It can take another step in the same direction, it can take a step in a different direction, or it can stop moving. These options represent the ++, +-, and +0 behavior choices.
If the animal is at rest for at moment, such that the 1st and 2nd tracking points are right on top of each other, then it has 2 options. It can start moving in any direction, or it can stay at rest. These options represent the 0+ and 00 behavior choices.
We also only want to consider decisions made in the edge region of the arena. Thus point 2 must be in the edge region for the behavior to be defined.

The Original Version (Given + / Given 0)
================================
For a group of animals, for each time point, count the number of animals that performed the ++, +-, +0, 0+, and 00 behaviors at that time point. Then add together the counts for ++, +-, and +0 to get the + count, and add together the counts for 0+ and 00 to get the 0 count. Finally, divide the counts as follows to get the motion probabilities at that time point.
P++Given+ = ++ / +
P+-Given+ = +- / +
P+0Given+ = +0 / +
P0+Given0 = 0+ / 0
P00Given0 = 00 / 0
In this version P++Given+ + P+-Given+ + P+0Given+ = 1 and P0+Given0 + P00Given0 = 1.

The Combined Version (Given Any)
================================
For a group of animals, for each time point, count the number of animals that performed the ++, +-, +0, 0+, and 00 behaviors at that time ponit. Then add together all five counts to get the any count. Finally, divide the counts as follows to get the motion probabilites at that time point.
P++GivenAny = ++ / any
P+-GivenAny = +- / any
P+0GivenAny = +0 / any
P0+GivenAny = 0+ / any
P00GivenAny = 00 / any
In this version P++GivenAny + P+-GivenAny + P+0GivenAny + P0+GivenAny + P00GivenAny = 1.

The Raw Version
================
For a group of animals, for each time point, count the number of animals that performed the ++, +-, +0, 0+, and 00 behaviors at that time ponit. Then divide each count by the number of animals in the group, n. This count, n, differs from the any count defined above because not all animals will be in the edge region at every time point to have a defined behavior at that time point.
P++(Raw) = ++/n
P+-(Raw) = +-/n
P+0(Raw) = +0/n
P0+(Raw) = 0+/n
P00(Raw) = 00/n
In this version there is no guarantee that anything adds to one.

How to choose
=============
Generally it is best to use the original version to preserve the interpretation of the individual measures listed above. However, it may be useful to see how the combined version compares to the original version. For instance, P++Given+ tends to decrease over time while P+-Given+ and P+0Given+ increase. However, if you look at the raw behavior counts, P+- and P+0 remain extremely rare, and it is P00 that increases. This is because at the end of the experiement, when an animal is mostly still, it may be very rare for a 'first step' to even occur so that P+- or P+0 can follow.

A final note
============
Because of the strong preference for the original version, I typically refer to P++Given+, P+-Given+, P+0Given+, P0+Given0, and P00Given0 soley as P++, P+-, P+0, P0+, and P00 in figure titles, axes labels, etc. It is only in filenames that the full version is displayed in order to contrast it to the other versions that are saved out simultaneously.
