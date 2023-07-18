coverage types
==============

Coverage
========

**Coverage*** is another way to view an animal's activity. Rather than considering the activity as a function of how much time an animal has spent in the arena, you could consider it as a function of how many chances the animal has had to learn the arena boundary.
Coverage was first described in the paper `Exploratory activity and habituation of *Drosophila* in confined domains <https://www.researchgate.net/profile/Gregg-Roman/publication/268523480_Exploratory_activity_and_habituation_of_Drosophila_in_confined_domains/links/546fbef00cf216f8cfa9e5a1/Exploratory-activity-and-habituation-of-Drosophila-in-confined-domains.pdf>`_ as the number of times the animal has traversed the entire arena and the fraction of the arena it has covered in addition.
To calculate coverage, we first divide the edge region of the arena into equal segments, or bins. Then at each tracking point, we count the number of visits that the animal has made to each bin. Finally, for each tracking point, we take the minimum of the visit counts at that point (n, the maximum number of visits such that every bin has been visited at least n times) and add to it the fraction of bins that have been visited more than n times.
For example, if at a time point, t, the animal had visites 75% of the arena (and possibly some of it more than once), but has not visited the entire arena, C(t) = 0.75
As another example, if at some other time point t, the animal has visited every part of the arena at least 3 times, and has visited 30% of the arena more than 3 times, the C(t) = 3.3
Coverage (or 'raw' coverage) is often sufficient for comparing groups of animals that reach a similar average final coverage. However, there are cases where it is better to normalize coverage in some way. These normalizations are described below.

Percent Coverage
================

**Percent Coverage** (though really a fraction rather than a percent) normalizes each individual animal's coverage vector by the maximum coverage that animal reached, essentially re-scaling it to between 0 and 1.

PICA (Percent of Individual Coverage Asymptote)
===============================================

**PICA** normalizes each individual animal's coverage vector by the asymptote value of that individual's time vs coverage model. Instead of normalizing it by the maximum value reached during the experiement (as in percent coverage), we normalize it by the maximum value we expect the animal to reach if the experiment had been continued indefinitely.

PGCA (Percent of Group Coverage Asymptote)
===============================================

**PGCA** also normalizes each individual animal's coverage vector by an asymptote value. However, instead of taking this asymptote from an individual's time vs coverage relationship, it is taken from the group average time vs coverage relationship.

How to choose
=============
Typically percent coverage is the best predictor of other behavioral measures, but it is also important to look at coverage itself to reveal learning differences.
This analysis has been mainly tested on various *Drosophila* species as well as some mice data. One of the other measures may perform better in different study systems.
