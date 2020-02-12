using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ifttt
{
    public class RecipeSummary
    {
        public RecipeSummary(RecipePage rp)
        {
            Filename = rp.Filename;
            Url = rp.Url;
            ID = rp.ID;
            Title = rp.Title;
            Description = rp.Description;
            Author = rp.Author;
            Featured = rp.Featured;
            Uses = rp.Uses;
            Favorites = rp.Favorites;
            Code = rp.Code;
        }

        public RecipeSummary(string line)
        {
            var pcs = line.Split('\t');
            Filename = pcs[0];
            Url = pcs[1];
            ID = int.Parse(pcs[2]);
            Title = pcs[3];
            Description = pcs[4];
            Author = pcs[5];
            Featured = bool.Parse(pcs[6]);
            Uses = int.Parse(pcs[7]);
            Favorites = int.Parse(pcs[8]);
            Code = AstNode.Parse(pcs[9]);
        }

        public static string HeaderLine
        {
            get
            {
            return string.Join("\t",
                "Filename",
                "Url",
                "ID",
                "Title",
                "Description",
                "Author", 
                "Featured",
                "Uses",
                "Favorites",
                "Code");
            }
        }

        public string ToLine()
        {
            return string.Join("\t",
                Filename,
                Url,
                ID.ToString(),
                Title,
                Description,
                Author, 
                Featured.ToString(),
                Uses.ToString(),
                Favorites.ToString(),
                Code.ToString());
        }

        public string Filename;
        public string Url;
        public int ID;
        public string Title;
        public string Description;
        public string Author;
        public bool Featured;
        public int Uses;
        public int Favorites;
        public AstNode Code;
    }
}
