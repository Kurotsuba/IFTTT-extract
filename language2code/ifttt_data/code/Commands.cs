using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using HtmlAgilityPack;
using System.IO.Compression;
using System.Net;
using System.Text.RegularExpressions;

namespace ifttt
{
    public static class Commands
    {
        #region Page downloading
        public class CWebClient : WebClient
        {
            public CWebClient(string cookieFile) : base()
            {
                m_sCookieFile = cookieFile;
            }

            protected override WebRequest GetWebRequest(Uri address)
            {
                var r =  base.GetWebRequest(address);
                if (!(r is HttpWebRequest)) return r;

                var req = r as HttpWebRequest;
                req.UserAgent = "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0";
                req.CookieContainer = new CookieContainer();
                foreach (string line in File.ReadAllLines(m_sCookieFile))
                {
                    string[] els = line.Split('\t');
                    if (els.Length != 7)
                        continue;
                        //throw new ArgumentException("cookie file in incorrect format: " + m_sCookieFile);
                    string k = els[5];
                    string v = els[6];
                    string site = els[0];
                    req.CookieContainer.Add(new Cookie(k, v, "", site));
                }
                return req;
            }

            string m_sCookieFile;
        }

        public static void DownloadAllRecipes(string urlList, string targetDir, string cookieFile)
        {
            if (!Directory.Exists(targetDir)) Directory.CreateDirectory(targetDir);
            var r = new Regex(@"recipes.(\d+)-");
            Func<string, int> getId = (s => int.Parse(r.Match(s).Groups[1].Value));

            int secondsToSleepBetween = 10;

            //var wc = new CWebClient(cookieFile);
            int lastUpdate = Environment.TickCount;
            foreach (var u in File.ReadLines(urlList))
            {
                try
                {
                    var id = getId(u);
                    var subdir = Path.Combine(targetDir, string.Format("{0:X2}", id % 0xFB));
                    if (!Directory.Exists(subdir)) Directory.CreateDirectory(subdir);
                    var file = u.Replace("https://ifttt.com", "").Replace('/', '_') + ".html";
                    var path = Path.Combine(subdir, file);
                    Console.WriteLine(u);

                    if (File.Exists(path)) continue;

                    {
                        int currentTime = Environment.TickCount;
                        int elapsed = currentTime - lastUpdate;
                        System.Threading.Thread.Sleep(Math.Max(100, secondsToSleepBetween * 1000 - elapsed));
                        lastUpdate = Environment.TickCount;
                    }
                    DownloadRecipe(u, path, cookieFile);
                    Console.Error.WriteLine("u: " + u);
                    Console.Error.WriteLine("path: " + path);
                    Console.Error.WriteLine("c: " + cookieFile);
                    Console.WriteLine(" --> {0}", new FileInfo(path).Length);
                    ParseSingleRecipeDebug(path);
                    //ParseSingleRecipeDebug(path);
                }
                catch (Exception e)
                {
                    Console.Error.WriteLine(u);
                    Console.Error.WriteLine(e.ToString());
                }
            }
        }

        public static void DownloadRecipe(string url, string file, string cookieFile)
        {
            CWebClient wc = new CWebClient(cookieFile);
            DownloadRecipe_help(wc, url, file);
        }

        static void DownloadRecipe_help(CWebClient wc, string url, string file)
        {
            wc.DownloadFile(url, file);
        }

        static List<string> GetAllUrls(string dir = @"d:\data\ifttt\popular_pages")
        {
            HashSet<string> urls = new HashSet<string>();
            object mutex = new object();
            Parallel.ForEach(Directory.GetFiles(dir, "popular*"), f =>
            {
                var l = GetUrlsFromPage(f).ToList();
                lock (mutex)
                    foreach (var u in l)
                        urls.Add(u);
            });
            return urls.ToList();
        }

        public static void GetAllRecipeUrls(string popPagesDir, string urlListFile)
        {
            var l = GetAllUrls(popPagesDir);
            l.Sort();
            File.WriteAllLines(urlListFile, l);
        }

        static List<string> GetUrlsFromPage(string pageFilename)
        {
            var d = new HtmlDocument();
            d.Load(pageFilename);
            var pop = d.DocumentNode.SelectSingleNode("//div[@id='popular']");
            var urls = new List<string>();
            foreach (var n in pop.SelectNodes(".//a[contains(@class, 'recipe-desc_title')]"))
            {
                urls.Add("https://ifttt.com" + n.Attributes["href"].Value);
            }
            return urls;
        }
        #endregion

        #region Recipe parsing

        public const string RecipeSummaryFile = @"d:\src\nl2code\ifttt\data\recipe_summaries.tsv.gz";

        public static void ParseAllRecipes(string inputDir, string outputFile)
        {
            var lLock = new object();
            var l = new List<RecipeSummary>();
            Parallel.ForEach(Directory.GetDirectories(inputDir),
                d =>
                {
                    var ll = new List<RecipeSummary>();
                    foreach (var r in Directory.GetFiles(d, "*.html"))
                    {
                        //Console.WriteLine(r);
                        var rp = ParseRecipe(r);
                        if (rp == null) continue;
                        ll.Add(new RecipeSummary(rp));
                    }
                    lock (lLock)
                    {
                        l.AddRange(ll);
                        Console.WriteLine(l.Count.ToString() + "\t" + d);
                    }
                });
            l.Sort((x, y) => (x.ID - y.ID));

            using (var sw = new StreamWriter(outputFile))
            {
                sw.WriteLine(RecipeSummary.HeaderLine);
                foreach (var s in l)
                    sw.WriteLine(s.ToLine());
            }
        }

        public static void ParseSingleRecipeDebug(string filename)
        {
            SummarizeRecipe(ParseRecipe(filename));
        }

        public static RecipePage ParseRecipe(string htmlFile)
        {
            var d = new HtmlDocument();
            var fi = new FileInfo(htmlFile);
            if (fi.Length == 0) return null;
            d.Load(htmlFile, new UTF8Encoding());
            if (d.DocumentNode.SelectSingleNode("//title").InnerText.ns() == "IFTTT / Error") return null;

            return new RecipePage(htmlFile, d);
        }

        public static void SummarizeRecipe(RecipePage rp)
        {
            Console.WriteLine("{0,30}:{1}", "ID", rp.ID);
            Console.WriteLine("{0,30}:{1}", "Title", rp.Title);
            Console.WriteLine("{0,30}:{1}", "Description", rp.Description);
            Console.WriteLine("{0,30}:{1}", "Author", rp.Author);
            Console.WriteLine("{0,30}:{1}", "Featured", rp.Featured);
            Console.WriteLine("{0,30}:{1}", "Uses", rp.Uses);
            Console.WriteLine("{0,30}:{1}", "Favorites", rp.Favorites);
            Console.WriteLine("{0,30}:{1}", "Code", rp.Code.ToString());
        }

        public static System.Tuple<List<AstNode>, List<AstNode>> ParseTriggerAction(string code)
        {
            return ParseTriggerAction(AstNode.Parse(code));
        }

        public static System.Tuple<List<AstNode>, List<AstNode>> ParseTriggerAction(AstNode node)
        {
            var root = AstNode.Parse("(ROOT (IF) [TRIGGER 1] (THEN) [ACTION 2])");
            var vars = new List<AstNode>();
            if (!TreeTransforms.Match(node, root, vars))
                throw new ArgumentException("Failed to parse");

            var triggerParts = new List<AstNode>();
            if (!(
                TreeTransforms.Match(vars[0], AstNode.Parse("(TRIGGER [* 1] (FUNC [* 2] [PARAMS 3]))"), triggerParts)
                ||
                TreeTransforms.Match(vars[0], AstNode.Parse("(TRIGGER [* 1] (FUNC [* 2] [PARAMS 3] [OUTPARAMS 4]))"), triggerParts)
                ))
                throw new Exception("failed to parse");
            if (triggerParts.Count == 3) triggerParts.Add(new AstNode("OUTPARAMS"));

            var actionParts = new List<AstNode>();
            if (!TreeTransforms.Match(vars[1], AstNode.Parse("(ACTION [* 1] (FUNC [* 2] [PARAMS 3]))"), actionParts))
                throw new Exception("failed to parse");

            return System.Tuple.Create(triggerParts, actionParts);
        }

        public static void GatherNormalizedParamNames(string code, string paramTypes, string normalizedParamsOut)
        {
            //var root = AstNode.Parse("(ROOT (IF) [TRIGGER 1] (THEN) [ACTION 2])");

            Dictionary<string, string> typeMap = new Dictionary<string, string>();
            foreach (var t in File.ReadLines(paramTypes).Skip(1).Select(line => line.Split('\t')))
                typeMap[t[0]] = t[1];


            Func<string, string> getType = (s => 
                {
                    string type;
                    if (typeMap.TryGetValue(s, out type)) return type;
                    return "???";
                });
            var counter = new Counter<string>();
            foreach (var l in File.ReadLines(code))
            {
                var parts = ParseTriggerAction(l);
                string name = string.Format("TRIGGER {0} {1}\t( {2} )",
                    parts.Item1[0].Name,
                    parts.Item1[1].Name,
                    string.Join(", ", parts.Item1[2].Children.Select(c => c.Name + ":" + getType(c.Name))),
                    string.Join(", ", parts.Item1[3].Children.Select(c => c.Name + ":" + getType(c.Name))));
                counter.Increment(name);

                name = string.Format("ACTION {0} {1}\t( {2} )",
                    parts.Item2[0].Name,
                    parts.Item2[1].Name,
                    string.Join(", ", parts.Item2[2].Children.Select(c => c.Name + ":" + getType(c.Name))));
                counter.Increment(name);
            }

            int total = counter.Count;
            int groups = 0;
            using (var sw = new StreamWriter(normalizedParamsOut))
            foreach (var g in counter.GroupBy(p => p.Key.Split('\t')[0]))
            {
                ++groups;
                var rep = g.OrderByDescending(p => p.Value).First();
                sw.WriteLine(rep.Key);
            }

            Console.WriteLine("Normalized {0} func+params into {1} func+params", total, groups);
        }

        public static IEnumerable<RecipeSummary> GetRecipes()
        {
            return GetRecipes(RecipeSummaryFile);
        }

        public static IEnumerable<RecipeSummary> GetRecipes(string file)
        {
            foreach (var line in ReadLinesMaybeGz(file).Skip(1))
            {
                yield return new RecipeSummary(line);
            }
        }
        #endregion

        public static IEnumerable<string> ReadLinesMaybeGz(string file)
        {
            if (file.EndsWith(".gz"))
                return ReadLinesGz(file);
            return File.ReadLines(file);
        }

        public static IEnumerable<string> ReadLinesGz(string file)
        {
            using (var fs = new FileStream(file, FileMode.Open))
            using (var gz = new GZipStream(fs, CompressionMode.Decompress))
            using (var sr = new StreamReader(gz))
            {
                string line;
                while (null != (line = sr.ReadLine()))
                    yield return line;
            }
        }
    }
}
