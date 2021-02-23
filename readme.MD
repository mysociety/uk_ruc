# UK Composite Rural Urban Classification

A composite 2- and 3-fold metric to describe various small areas (LSOAs/Datazones/SOAs) on a rural/urbal scale that is comparable across the UK. 

This can be found in `output/composite_ruc.csv`.

## Background

For small areas (LSOA/Datazones/SOA) there are different measures of if an area how rural/urban an area is depending on the UK nation. 

* England/Wales - [ONS Rural/Urban Classification (RUC)](https://www.ons.gov.uk/methodology/geography/geographicalproducts/ruralurbanclassifications) [(data)](https://geoportal.statistics.gov.uk/datasets/276d973d30134c339eaecfc3c49770b3_0)
* Scotland - [Scottish Government Urban Rural (SGUR) Classification](https://www.gov.scot/publications/scottish-government-urban-rural-classification-2016/pages/2/)
* Northern Ireland -  NISRA [Delineation of settlements (SDL)](https://www.nisra.gov.uk/publications/urban-rural-geography-documents-2015)

As these reflect different needs in different nations  (for instance, Scotland is far more concerned with remoteness), these scales are not directly comparable. 

England/Wales have an 11 point scale, Scotland has a varying 2,3,6 and 8 scale, and Northern Ireland has 8 bands for settlement size with a 3 point urban/rural scale (this is a Urban/Rural/Mixed as opposed to Scotland's 3-point scale, which splits rural areas by remoteness).

While all split in some form into rural/urban areas, these are based on different definitions. For England/Wales a rural area is part of a settlement of less than 10,000 people, while for Northern Ireland this is less than 5,000 people and Scotland it is less than 3,000 people. 

## Building a comparable measure

All metrics can roughly converge on a binary urban/rural scale where an urban areas are over 10,000 people. For Scotland, using the 6-fold scale, 1-2 are urban, 3-6 are rural. For Northern Ireland, Bands A-D are urban and E-H are rural. 

This is a measure of density that makes most sense in England. A measure roughly equivilent to the Scottish definition (where 5-6 on six point scale are rural) can be found by counting NI G-H bands as rural (max size 2,500), and the RUC E groupings (Villages and Hamlets) as rural. This last one is not directly comparable as different rural classifications in RUC are not based directly on population cut-offs, but is the easiest fix.

This leads to a 2-fold and 3-fold scale:

* CRUC-2: 0-Urban/1-Rural
* CRUC-3: 0-Urban/1-Rural/2-More Rural

Where Urban always means more than 10,000 and 'More Rural' should generally track different ideas of a 'village' sized settlement. 

## National composition of different measures

### Two-fold divide

| ukruc-2   | E   | N   | S   | W   |
|:----------|:----|:----|:----|:----|
| Urban     | 83% | 59% | 70% | 68% |
| Rural     | 17% | 41% | 30% | 32% |

### Three-fold divide

| ukruc-3    | E   | N   | S   | W   |
|:-----------|:----|:----|:----|:----|
| Urban      | 83% | 59% | 70% | 68% |
| Rural      | 9%  | 13% | 12% | 17% |
| More Rural | 8%  | 28% | 17% | 14% |

## Rebuilding

Run `python create_unified_measure.py`.

The scale is built in two steps. As the Northern Ireland lookup only provides SOA to rural/urban/mixed, a settlement band per Super Output Areas needs to be recomposited from Small Areas.

This is done by converting the settlement band to a number from 1-8 (where 8 is the most rural), taking an average of the SA bands, and rounding to the nearest whole number, and then reconverting into a Band for the SOA. 

The three different sets of statistics are then combined using the describes steps to create the composite scales.

## Licencing

Source indexes for each country are licenced as Open Government License (OGL) version 3.0.

Unless otherwise stated, composite datasets are licensed under a [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).

Code and scripts are licenced under a MIT Licence. 