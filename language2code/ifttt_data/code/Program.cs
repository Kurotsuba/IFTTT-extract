using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ifttt
{
    class Program
    {
        static void Main(string[] args)
        {
            if (args.Length < 1)
            {
                Console.Error.WriteLine("Usage: ifttt.exe [command:String]");
                Console.Error.WriteLine("where [command:String] is either:");
                Console.Error.WriteLine("   DownloadAllRecipes");
                Console.Error.WriteLine("   ParseAllRecipes");
            }
            else if (args[0] == "DownloadAllRecipes")
            {
                if (args.Length != 4)
                    throw new ArgumentException("Usage: ifttt.exe DownloadAllRecipes [urlList:String] [targetDir:String] [cookieFile:String]");
                string urlList = args[1];
                string targetDir = args[2];
                string cookieFile = args[3];
                Commands.DownloadAllRecipes(urlList, targetDir, cookieFile);
            }
            else if (args[0] == "ParseAllRecipes")
            {
                if (args.Length != 3)
                    throw new ArgumentException("Usage: ifttt.exe ParseAllRecipes [inputDir:String] [outputFile:String]");
                string inputDir = args[1];
                string outputFile = args[2];
                Commands.ParseAllRecipes(inputDir, outputFile);
            }
            else
            {
                Console.Error.WriteLine("Unknown command: " + args[0]);
            }
        }
    }
}
