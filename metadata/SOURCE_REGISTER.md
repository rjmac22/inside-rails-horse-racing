# Source Register

## Dataset

**Title:** Horse Racing Results UK & Ireland 2015–2025  
**Creator:** deltaromeo  
**Platform:** Kaggle  
**Source URL:** https://www.kaggle.com/datasets/deltaromeo/horse-racing-results-ukireland-2015-2025  
**Downloaded:** 21 July 2026  
**Expected update frequency:** Weekly  
**Licence:** Community Data License Agreement – Sharing – Version 1.0

## Local source

**Original archive:** `data/raw/archive.zip`  
**Source inventory:** `metadata/SOURCE_FILE_INVENTORY.tsv`  
**Checksums:** `metadata/SHA256SUMS.txt`

## Source notes

The download contains several related data products rather than one unified database:

- historical archives for 1988–2004 and 2005–2014;
- current form data from 2015 onward;
- recent form exported as HTML;
- daily racecards;
- BHA ratings;
- Betfair mapping files;
- an author-supplied prediction model;
- incremental update files.

The main historical source identified by the author is:

`data/raw/form_2015-present/form_2015-present/raceform.db`

## Project handling rule

Files under `data/raw/` are immutable source files.

They may be read and profiled, but must not be edited, overwritten, cleaned in place or committed to GitHub.

All transformations must write to separate staging, interim or processed locations.

## Publication policy

The GitHub repository will publish:

- code;
- notebooks;
- database schemas;
- validation logic;
- documentation;
- metadata;
- aggregate analytical results.

The raw Kaggle data will not be redistributed through the repository.
