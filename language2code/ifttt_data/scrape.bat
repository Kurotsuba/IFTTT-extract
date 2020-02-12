@ECHO OFF

mono code\Program.exe DownloadAllRecipes data\all.urls data\ifttt data\cookies.txt
mono code\Program.exe ParseAllRecipes data\ifttt data\recipe_summaries.tsv
