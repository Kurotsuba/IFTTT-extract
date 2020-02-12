#!/bin/bash

mono code/Program.exe DownloadAllRecipes data/all.urls data/ifttt data/cookies.txt
mono code/Program.exe DownloadAllRecipes data/ifttt data/recipe_summaries.tsv
