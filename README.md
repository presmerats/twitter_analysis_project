Twitter project
===============


Instructions
-------------

How to run it?
```
source ~/.twitter_setup.sh
python scraping.py <OPTION>
```
Options are:
* graph
* bow

Development and Testing
------------------------

General workflow for a new feature described here.

First create a new branch for the new feature:
```
git checkout -b new_feature
```

Write tests then do your work and when finished do:

```
git add <all new files> 
git commit -m "new_feature finished"
git checkout testing
git merge new_feature
python unittests

```

If all is correct then:
```
git checkout master
git merge testing
```