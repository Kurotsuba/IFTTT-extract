--------------------------------------------------------------------------
If-This-Then-That Programs and Descriptions Corpus
--------------------------------------------------------------------------

This archive contains resources relating to the paper:

Language to Code: Learning Semantic Parsers for if-this-then-that Recipes
Chris Quirk, Raymond Mooney and Michel Galley
Proceedings of the ACL, 2015

If you make use of any of these resources, we would be grateful if you could
acknowledge this work by citing the paper above. Specifically, this archive
contains MTurk annotation and code to scrape recipes from IFTTT.com.

--------------------------------------------------------------------------
Steps to scrape recipes from IFTTT.com:

* Install Mono
  See http://www.mono-project.com/ for details.
  This is an easy and seamless process whether you run Linux, Mac OS X, 
  or Windows. For example on Debian-based machines, simply run:
  apt-get install mono-complete

* Install Html Agility Pack (optional)
  If you plan to recompile the code, then download "release binary" from
  http://htmlagilitypack.codeplex.com
  Extract Net45\HtmlAgilityPack.dll and copy it into the
  "ifttt\code" directory.

* Compile (optional)
  If you want to recompile the code, cd to "ifttt\code" and run either
  compile.bat or compile.sh.
  This will create or recreate the file "ifttt\code\Program.exe", which 
  is already included in the distribution.

* Create an IFTTT account, and save your cookies into a "cookies.txt"
  file. In Firefox, one can do so with add-ons such as "Export Cookies".
  In Internet Explorer, select menu "File" > "Import and Export..." >
  "Export to a file" > Select "Cookies" and then save. In either case,
  save the file as "ifttt\data\cookies.txt".

* Run either scrape.sh (Mac OS X or linux) or scrape.bat (Windows)
  See troubleshooting section at the end of this file.
  The scraping code waits 10 seconds between pages to maintain a moderate
  bandwidth.

--------------------------------------------------------------------------
Data

We used Mechanical Turk (MTurk) to get a sense of how well untrained 
humans can write IFTTT recipes. Specifically, we had 5 turkers read
each recipe of the test set and asked them to provide:
trigger channel, trigger, action channel, and action. 

This data is available here:
data\turk_public.tsv (test set)

For convenience, we are also providing channels, triggers and actions
in the same format for the original IFTTT data:
data\ifttt_public.tsv (test set)

After running scrape.sh or scrape.bat, the html will be stored in
data\ifttt and the merged recipes for train/dev/test in
data\recipe_summaries.tsv.

To split the data into train/dev/test, please refer to the files:
data\train.urls
data\dev.urls
data\test.urls

--------------------------------------------------------------------------
Troubleshooting

You might encounter some of the following exceptions:

* "Mono.Security.Protocol.Tls.TlsException: 
  Invalid certificate received from server."
  See http://www.mono-project.com/docs/faq/security/.
  One solution is to import root certificates using mozroots, 
  which downloads and installs all Mozilla's root certificates:
  $ mozroots --import --ask-remove

* "System.Net.WebException: The remote server returned an error: 
  (404) Not Found."
  The IFTTT page is unfortunately gone.

--------------------------------------------------------------------------
Contacts

Chris Quirk <chrisq@microsoft.com>
Michel Galley <mgalley@microsoft.com>
