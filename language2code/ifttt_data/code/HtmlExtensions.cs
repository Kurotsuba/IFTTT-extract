using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using HtmlAgilityPack;

namespace ifttt
{
    public static class HtmlExtensions
    {
        public static HtmlNode ssn(this HtmlNode n, string type, string klass, bool throwOnEmpty = true)
        {
            var nc = n.SelectSingleNode(".//" + type + "[contains(concat(\" \", normalize-space(@class), \" \"), \" " + klass + " \")]");
            if (throwOnEmpty && nc == null)
                throw new Exception("Failed to match type \"" + type + "\" class \"" + klass + "\" from node " + n.ToString());
            return nc;
        }

        public static HtmlNodeCollection sns(this HtmlNode n, string type, string klass, bool throwOnEmpty = true)
        {
            var nc = n.SelectNodes(".//" + type + "[contains(concat(\" \", normalize-space(@class), \" \"), \" " + klass + " \")]");
            if (throwOnEmpty && nc == null)
                throw new Exception("Failed to match type \"" + type + "\" class \"" + klass + "\" from node " + n.ToString());
            return nc;
        }

        public static string ed(this string s)
        {
            return HtmlEntity.DeEntitize(s);
        }

        public static string ns(this string s)
        {
            return ns(s, ' ');
        }

        public static string us(this string s)
        {
            return ns(s, '_');
        }

        private static string ns(string s, char spaceChar)
        {
            bool first = true;
            bool needSpace = false;
            var sb = new StringBuilder();
            foreach (var c in s)
            {
                if (char.IsWhiteSpace(c))
                {
                    if (!first)
                        needSpace = true;
                }
                else
                {
                    first = false;
                    if (needSpace)
                        sb.Append(spaceChar);
                    needSpace = false;
                    sb.Append(c);
                }
            }
            return sb.ToString();
        }
    }
}
