using HtmlAgilityPack;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace ifttt
{
    public class RecipePage
    {
        public RecipePage(string filename, HtmlDocument doc)
        {
            Filename = filename;
            Url = doc.DocumentNode.SelectSingleNode("//meta[@property='og:url']").Attributes["content"].Value;
            var docNode = doc.DocumentNode;
            //var footer = docNode.ssn("div", "recipe-page_recipe-footer");
            ID = int.Parse(
                docNode.ssn("div", "recipe-page recipe-page_shared").Attributes["id"].Value.Replace("recipe_","")
                //footer.sns("div", "mobile-only").First().InnerText.ns().Replace("Recipe ID ", "")
                );

            Title = docNode.ssn("h1", "l-page-title").InnerText.ns();
            var desc = docNode.ssn("p", "recipe-page-shared_description-content", false);
            Description = (desc != null ? desc.SelectSingleNode("span[@itemprop='description']").InnerText.ns() : "");

            Author = docNode.ssn("span", "stats_author").InnerText.ns().Replace("by ", "");

            Uses = ParseNum(docNode.ssn("span", "stats_item__use-count").InnerText.ns().Split(' ')[0]);
            Favorites = ParseNum(docNode.ssn("span", "stats_item__favorites-count__number").InnerText.ns());

            Featured = (docNode.ssn("div", "recipe-featured-star", false) != null);

            Code = new AstNode("ROOT", 
                new AstNode("IF"),
                ParseTrigger(doc, docNode),
                new AstNode("THEN"),
                ParseAction(doc, docNode)
                );
        }

        public AstNode ParseTrigger(HtmlDocument d, HtmlNode n)
        {
            var typ = n.ssn("span", "recipe_trigger");
            var form = d.GetElementbyId("live_trigger_fields_complete");
            IEnumerable<HtmlNode> fields = ((IEnumerable<HtmlNode>)form.sns("div", "trigger-field", false)) ?? new HtmlNode[0];
            return new AstNode("TRIGGER",
                new AstNode(typ.Attributes["title"].Value.ed().us()),
                new AstNode("FUNC",
                    new AstNode(form.ssn("h4", "t-or-a-fields-heading_specific-t-or-a_name").InnerText.us()),
                    new AstNode("PARAMS", 
                            fields.Select(node => ParseTriggerParam(node)).ToArray()
                        )
                    )
                );
        }
        
        public AstNode ParseTriggerParam(HtmlNode n)
        {
            string name = n.ssn("label", "trigger-field_label").InnerText.us();
            var node = new AstNode(name);

            var c = n.ssn("div", "trigger-field_collection", false);
            if (c != null)
            {
                if (c.ChildNodes.Count == 0) c = c.ParentNode;
                foreach (var select in c.sns("select", "tf-collection-sel"))
                    AppendChildFromSelect(node, select);
                return node;
            }
            c = n.ssn("div", "tf-time-sel-unit_inputs", false) ??
                n.ssn("div", "tf-datetime-sel-unit_inputs", false) ??
                n.ssn("div", "tf-min-sel-unit", false);
            if (c != null)
            {
                foreach (var child in c.ChildNodes)
                {
                    if (child is HtmlTextNode)
                    {
                        var t = child.InnerText.ed().ns();
                        if (!string.IsNullOrWhiteSpace(t))
                            node.Children.Add(new AstNode(t));
                        continue;
                    }
                    if (child.Name == "select")
                    {
                        AppendChildFromSelect(node, child);
                        continue;
                    }
                }

                return node;
            }
            c = n.ssn("input", "tf-text", false);
            if (c != null)
            {
                node.Children.Add(new AstNode(c.Attributes["value"].Value.ed().ns()));
                return node;
            }
            c = n.ssn("div", "nativeCheckbox-multiwrapper", false);
            if (c != null)
            {
                foreach (var cc in c.sns("input", "tf-checkbox"))
                {
                    if (cc.Attributes.Contains("checked") && cc.Attributes["checked"].Value == "checked")
                        node.Children.Add(new AstNode(cc.Attributes["value"].Value));
                }
                return node;
            }


            return new AstNode("???");
        }

        private static void AppendChildFromSelect(AstNode node, HtmlNode select)
        {
            var option = (select.SelectNodes("./option[@selected='selected']") ?? select.ChildNodes)
                .FirstOrDefault();
            if (option != null)
                node.Children.Add(new AstNode(option.Attributes["value"].Value.ns()));
        }

        public AstNode ParseAction(HtmlDocument d, HtmlNode n)
        {
            var typ = n.ssn("span", "recipe_action");
            var form = d.GetElementbyId("live_action_fields_complete");
            IEnumerable<HtmlNode> fields = ((IEnumerable<HtmlNode>)form.sns("div", "action-field", false)) ?? new HtmlNode[0];
            return new AstNode("ACTION",
                new AstNode(typ.Attributes["title"].Value.ed().us()),
                new AstNode("FUNC",
                    new AstNode(form.ssn("h4", "t-or-a-fields-heading_specific-t-or-a_name").InnerText.ns().Replace(" ", "_")),
                        new AstNode("PARAMS",
                            fields.Select(node => ParseActionParam(node)).ToArray()
                        )
                    )
                );
        }
        public AstNode ParseActionParam(HtmlNode n)
        {
            string name = n.ssn("label", "action-field_label").InnerText.us();
            var node = new AstNode(name);

            var c = n.ssn("textarea", "action-field_textarea", false);
            if (c != null)
            {
                node.Children.Add(new AstNode(c.InnerText.ns()));
                return node;
            }
            c = n.ssn("div", "action-field_collection", false);
            if (c != null)
            {
                if (c.ChildNodes.Count == 0) c = c.ParentNode;
                foreach (var select in c.sns("select", "af-collection-sel"))
                    AppendChildFromSelect(node, select);
                return node;
            }

            return new AstNode("???");
        }

        public static int ParseNum(string s)
        {
            var m = Regex.Match(s, @"^(\d+(\.\d+)?)[kK]$");
            if (m.Success)
                return (int)(double.Parse(m.Groups[1].Value) * 1000.0);
            m = Regex.Match(s, @"^(\d+(\.\d+)?)[mM]$");
            if (m.Success)
                return (int)(double.Parse(m.Groups[1].Value) * 1000000.0);
            return int.Parse(s);
        }

        public string Filename;
        public string Url;
        public int ID;
        public string Title;
        public string Author;
        public string Description;
        public bool Featured;
        public int Uses;
        public int Favorites;
        public AstNode Code;
    }
}
